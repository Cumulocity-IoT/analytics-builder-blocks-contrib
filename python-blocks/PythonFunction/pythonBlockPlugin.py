import collections, json, types, os, subprocess, importlib, re
import http.client
from apama.eplplugin import EPLAction, EPLPluginBase, Event
from RestrictedPython import compile_restricted, Eval, Guards, safe_builtins, limited_builtins, utility_builtins

class Context(object):
	def __init__(self, logger, state, params):
		self.logger = logger
		self._state = state
		self.params = [params['param1'], params['param2'], params['param3'], params['param4'], params['param5']]

	def getState(self, key, default=None):
		if key not in self._state:
			self._state[key] = default
		return self._state[key]

	def setState(self, key, value):
		self._state[key] = value

	def hasState(self, key):
		return key in self._state


class Value(object):
	def __init__(self, value, properties={}, timestamp=0.0):
		self.value = value
		self.properties = properties
		self.timestamp = timestamp
		self._guarded_writes = True

	def _asdict(self):
		return {
			"value": self.value,
			"properties": self.properties,
			"timestamp": self.timestamp
		}

class PythonBlockPlugin(EPLPluginBase):

	safe_modules = {
		"math": importlib.import_module("math"),
		"functools": importlib.import_module("functools"),
		"itertools": importlib.import_module("itertools"),
		"copy": importlib.import_module("copy"),
		"cmath": importlib.import_module("cmath"),
		"decimal": importlib.import_module("decimal"),
		"fractions": importlib.import_module("fractions"),
		"numbers": importlib.import_module("numbers"),
		"operator": importlib.import_module("operator"),
		"collections": importlib.import_module("collections"),
		"heapq": importlib.import_module("heapq"),
		"bisect": importlib.import_module("bisect"),
		"statistics": importlib.import_module("statistics"),
		"array": importlib.import_module("array"),
		"enum": importlib.import_module("enum"),
		"typing": importlib.import_module("typing"),
		"dataclasses": importlib.import_module("dataclasses"),
		"string": importlib.import_module("string"),
		"re": importlib.import_module("re"),
		"textwrap": importlib.import_module("textwrap"),
		"difflib": importlib.import_module("difflib"),
		"unicodedata": importlib.import_module("unicodedata"),
		"base64": importlib.import_module("base64"),
		"binascii": importlib.import_module("binascii"),
		"hashlib": importlib.import_module("hashlib"),
		"hmac": importlib.import_module("hmac"),
		"json": importlib.import_module("json"),
		"datetime": importlib.import_module("datetime"),
		"time": importlib.import_module("time"),
		"calendar": importlib.import_module("calendar"),
		"uuid": importlib.import_module("uuid"),
		"random": importlib.import_module("random"),
		"secrets": importlib.import_module("secrets"),
		"json": types.SimpleNamespace(loads=json.loads, dumps=json.dumps, JSONDecodeError=json.JSONDecodeError),
		"csv": importlib.import_module("csv"),
	}

	@staticmethod
	def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
		if not name:
			raise ImportError("Empty module name not allowed in import")

		parts = name.split(".")
		top_level = parts[0]

		if top_level not in PythonBlockPlugin.safe_modules:
			raise ImportError(f"Import of module '{name}' is not allowed in restricted python block")

		module = PythonBlockPlugin.safe_modules[top_level]

		if fromlist:
			prefix_len = 0
			for i in range(len(parts), 0, -1):
				prefix = ".".join(parts[:i])
				if prefix in PythonBlockPlugin.safe_modules:
					module = PythonBlockPlugin.safe_modules[prefix]
					prefix_len = i
					break

			for part in parts[prefix_len:]:
				if not hasattr(module, part):
					raise ImportError(f"Module '{name}' has no attribute '{part}' in restricted python block")
				module = getattr(module, part)

		return module


	def install_requirements(self, requirements, requirementsDir, packages):
		os.makedirs(requirementsDir, exist_ok=True)
		with open(os.path.join(requirementsDir, "requirements.txt"), "w") as reqFile:
			reqFile.write(requirements)
		self.getLogger().info(f"Installing requirements for python function block")
		self.getLogger().debug(f"Requirements:\n{requirements}")
		try:
			subprocess.check_call(["/usr/bin/env", "python3", "-m", "pip", "install", "--target", requirementsDir, "-r", os.path.join(requirementsDir, "requirements.txt")], timeout=120)
		except Exception as e:
			self.getLogger().error(f"Failed to install package requirements: {e}")
		self.getLogger().info(f"Permitting additional packages for python function block: {packages}")
		importlib.invalidate_caches()
		for package in [p for p in re.split(r"[^A-Za-z0-9_.]+", packages) if p]:
			package = package.strip()
			if not package:
				continue
			PythonBlockPlugin.safe_modules[package] = importlib.import_module(package)

	def __init__(self,init):
		super(PythonBlockPlugin,self).__init__(init)
		self.install_requirements(self.getConfig().get("requirements"), self.getConfig().get("requirementsDir"), self.getConfig().get("packages"))

	@EPLAction("action<> returns chunk")
	def createPythonState(self):
		return dict()

	@EPLAction("action<string> returns chunk")
	def validate(self, expression):
		bytecode = compile_restricted(expression, '<inline code>', 'exec')
		globals = dict(PythonBlockPlugin.safe_globals)
		exec(bytecode, globals)
		onInput = globals.get("onInput", None)
		if not callable(onInput):
			raise Exception("The provided code does not define a callable onInput function")
		return (onInput, globals)

	@EPLAction("action<chunk, chunk, apamax.analyticsbuilder.blocks.PythonFunction_$Parameters, sequence<apama.analyticsbuilder.Value>> returns sequence<apama.analyticsbuilder.Value>")
	def execute(self, code, state, properties, inputs):
		(onInput, globals) = code
		result = onInput([Value(x.fields['value'], x.fields['properties'], x.fields['timestamp']) for x in inputs], Context(self.getLogger(), state, properties.fields))
		if result is None:
			return []
		else:
			return [Event("apama.analyticsbuilder.Value", x._asdict() if isinstance(x, Value) else {"value":x, "properties":{}, "timestamp":0.0}) for x in result]

def practical_write(*args):
    if len(args) == 1:
        # sometimes called with just a single sentinel or value
        return args[0]

    elif len(args) == 2:
        # variable assignment: name, value
        name, value = args
        if isinstance(name, str) and name.startswith("_"):
            raise TypeError(f"assignment to private variable {name} is forbidden")
        globals()[name] = value
        return value

    elif len(args) == 3:
        # attribute assignment: obj, name, value
        obj, name, value = args
        if isinstance(name, str) and name.startswith("_"):
            raise TypeError(f"assignment to private attribute {name} is forbidden")
        try:
            setattr(obj, name, value)
        except AttributeError:
            # fallback for attribute-less objects (numpy scalars, pandas Index)
            obj[name] = value
        return value

    else:
        raise TypeError(f"unexpected number of arguments: {len(args)}")


PythonBlockPlugin.safe_globals = {
   "__builtins__": {**safe_builtins, **limited_builtins, **utility_builtins,
		"__import__": PythonBlockPlugin.safe_import,
		"dict": dict,
		"map": map,
		"filter": filter,
		"enumerate": enumerate,
		"reversed": reversed,
	},
   "Value": Value,
   "_getiter_": Eval.default_guarded_getiter,
   "_getitem_": Eval.default_guarded_getitem,
   "_iter_unpack_sequence": Guards.guarded_iter_unpack_sequence,
   "_unpack_sequence_": Guards.guarded_unpack_sequence,
   "_iter_unpack_sequence": Guards.guarded_iter_unpack_sequence,
   "_unpack_sequence_": Guards.guarded_unpack_sequence,
   "_write_": practical_write,
}


