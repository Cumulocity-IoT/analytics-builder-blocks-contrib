---
name: write-analytics-builder-tests
description: 'Write PySys tests for Apama Analytics Builder blocks. Use when: creating a test for a block, adding test cases for a block, writing pysystest.py files, testing block inputs and outputs, verifying block behaviour with assertBlockOutput or assertGrep, testing block parameters or state.'
argument-hint: 'Name of the block to test, and any specific scenarios to cover'
---

# Write PySys Tests for Analytics Builder Blocks

## Overview

Tests live in `tests/<BlockName>_NNN/pysystest.py` (e.g. `tests/Nand_001/pysystest.py`). Each test is a single Python file — no other files are needed. Tests use the PySys framework with the Analytics Builder test extension.

The correlator is **externally clocked** — time only advances when a `self.timestamp()` event is sent. Always send a final timestamp after the last input to ensure the last events are flushed and processed.

---

## Step 1 — Read the Block

Before writing a test, read the block's `.mon` file to identify:
- The **fully qualified block ID** (the `event` name in the package, e.g. `apamax.analyticsbuilder.custom.Nand`)
- All **input names** (parameters of the `$process` action prefixed with `$input_`)
- All **output names** (calls to `$setOutput_<name>`)
- All **parameters** (fields of the `_$Parameters` event)
- The **block logic** — what inputs and parameter combinations produce which outputs

---

## Step 2 — Plan Test Cases

Design one `pysystest.py` per scenario. A minimal test suite for a block should cover:

| Test | Purpose |
|---|---|
| `_001` | **Touch test** — deploys successfully, basic happy-path input → output |
| `_002` ... | Edge cases, parameter variations, boundary values, inverse inputs |

Each test should be focused — test one behaviour per file.

---

## Step 3 — Create the Test File

### Naming and location

```
tests/<BlockName>_<NNN>/pysystest.py
```

The `<NNN>` suffix is a zero-padded 3-digit number starting at `001`.

### `pysystest.py` template

```python
__pysys_title__   = r""" <BlockName> block - <short description of scenario>. """
#                        =========================================================================
__pysys_purpose__ = r""" <BlockName> block - <short description of scenario>. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
    def execute(self):
        correlator = self.startAnalyticsBuilderCorrelator(
            blockSourceDir=f'{self.project.SOURCE}/blocks/')

        # engine_receive process listening on all the channels.
        correlator.receive('all.evt')

        # Deploy the model. Pass parameters if the block has any.
        # Always declare ALL inputs and outputs that will be connected in this test.
        # Omit inputs/outputs dicts only when using defaults (float type, all ports connected).
        self.modelId = self.createTestModel(
            '<fully.qualified.BlockId>',
            {'paramName': value},              # omit if no params
            inputs={'inputName': 'float',      # list every input wired in this test
                    'inputName2': 'pulse'},    # use 'pulse', 'float', 'boolean', 'string'
            outputs={'outputName': 'float'},   # list every output asserted in this test
        )

        self.sendEventStrings(correlator,
                              self.timestamp(1),
                              self.inputEvent('<inputName>', <value>, id=self.modelId),
                              self.timestamp(2),
                              self.inputEvent('<inputName>', <value>, id=self.modelId),
                              self.timestamp(20),  # final flush
                              )

    def validate(self):
        # Always verify the model started successfully.
        self.assertGrep(self.analyticsBuilderCorrelator.logfile,
                        expr='Model "' + self.modelId + '" with PRODUCTION mode has started')

        # Always add at least one output assertion — an empty validate() is a Python IndentationError.
        self.assertBlockOutput('<outputName>', [<expected_value>])
```

#### `blockSourceDir` path

- For blocks in `blocks/`:  `f'{self.project.SOURCE}/blocks/'`
- For blocks in other directories (e.g. `cumulocity-blocks/`): `f'{self.project.SOURCE}/cumulocity-blocks/'`

---

## Step 4 — Choose an Assertion Method

### Option A — `assertBlockOutput` (simplest, for ordered value sequences)

Use when you want to assert the full sequence of values produced on an output:

```python
self.assertBlockOutput('outputName', [value1, value2, ...])
```

### Option B — `outputExpr` + `assertGrep` (for specific value at a specific time)

Use `self.outputExpr(outputId, value, time=t)` to build a regex that matches an output event:

```python
self.assertGrep('output.evt', expr=self.outputExpr('trigger', None, time=40))
self.assertGrep('output.evt', expr=self.outputExpr('result', 10.5))
```

Pass `None` as value when you only care that the output fired, not its value.

> **Floating-point caution**: avoid asserting exact float values that may render with rounding (e.g. `4.6` may appear as `4.599999999997`). Prefer `assertBlockOutput` which handles this, or use `assertGrep` with a lenient regex.

### Option C — `assertGrep` on correlator log (quick smoke check)

For simple blocks that log their output:

```python
self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='myOutput = true')
```

### Option D — `OUTPUT_REGEX` pattern (for multiple outputs at specific times)

Use when a block fires multiple output ports at the same timestamp:

```python
OUTPUT_REGEX = r'apamax.analyticsbuilder.test.Output\("%(outputId)s","%(modelId)s","[^"]*",%(time)s,any\([^"]*,(.*)\),\{.*\}\)'
self.assertThat("expected == output",
                expected='true',
                output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX % {'outputId': 'entered', 'modelId': 'model_0', 'time': 2}).group(1)")
```

---

## Step 5 — Key Rules

- **Always send a final `self.timestamp()` after the last input** — otherwise the last events may not be processed.
- **Always declare all connected inputs and outputs in `createTestModel`**: pass `inputs={'name': 'type', ...}` and `outputs={'name': 'type', ...}` for every port used in the test. The type string matches the `$INPUT_TYPE_` / `$OUTPUT_TYPE_` constant value (`'pulse'`, `'float'`, `'boolean'`, `'string'`). Omitting a mandatory input means the framework treats it as disconnected, which causes incorrect or no output.

  ```python
  # CORRECT — all ports declared
  self.modelId = self.createTestModel(
      'apamax.analyticsbuilder.custom.CountBy',
      inputs={'input': 'pulse', 'reset': 'pulse'},
      outputs={'count': 'float'},
  )

  # WRONG — omitting inputs/outputs causes the block to behave as if inputs are disconnected
  self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.CountBy')
  ```
- Events sent between two timestamps that are **less than 0.1 s apart** are held and processed together.
- **For blocks with multiple inputs that must be evaluated together** (e.g. `value1` and `value2`), send all of them _between the same pair of timestamps_. Sending them at different timestamps causes the block to fire once per input, producing more outputs than expected:

  ```python
  # CORRECT — both inputs processed simultaneously at t=1
  self.sendEventStrings(correlator,
                        self.timestamp(1),
                        self.inputEvent('value1', 10.0, id=self.modelId),
                        self.inputEvent('value2', 5.0, id=self.modelId),
                        self.timestamp(2),
                        )
  # assertBlockOutput('output', [15.0])  ✓ one output

  # WRONG — block fires at t=1 and again at t=2, producing two outputs
  self.sendEventStrings(correlator,
                        self.timestamp(1),
                        self.inputEvent('value1', 10.0, id=self.modelId),
                        self.timestamp(2),
                        self.inputEvent('value2', 5.0, id=self.modelId),
                        self.timestamp(3),
                        )
  # assertBlockOutput('output', [15.0])  ✗ fails — actual output is [10.0, 15.0]
  ```

- **`validate()` must never be empty** — an empty method body is a Python `IndentationError`. Always include at least the model-started assertion.
- `inputEvent` default type is `float`. For boolean inputs pass `True`/`False`. For string inputs include `inputs={'inputName': 'string'}` in `createTestModel`.
- To leave an input disconnected, pass `inputs={'inputName': None}` in `createTestModel`.
- `self.modelId` is automatically assigned `model_0`, `model_1`, etc. if not specified.

---

## Testing Timer-Based Blocks

Blocks that use timers (`TimerParams.recurring`, `TimerParams.relative`, etc.) require careful timestamp placement in tests. The correlator is externally clocked, so **timers only fire when you advance time past their trigger point**.

### Key principles

1. **Timer fires when time advances past the trigger point** — A recurring timer created at t=3 with period=10 fires when you send `self.timestamp(13)` (or any time ≥ 13).
2. **Place timestamps at timer boundaries** — To verify timer output, send a `self.timestamp()` at exactly the expected fire time.
3. **Inputs between timer ticks are accumulated** — Inputs sent between timer fires are processed immediately but timer output only appears at the next tick.
4. **Use `outputExpr` with `time=` to verify exact output timing**:
   ```python
   self.assertGrep('output.evt', expr=self.outputExpr('output', 2.0, time=13))
   ```

### Example — Testing a recurring timer block

```python
# Block with period=10s, first input at t=3 starts the timer
self.sendEventStrings(correlator,
    self.timestamp(3),
    self.inputEvent('value', 1.0, id=self.modelId),   # t=3: starts timer, period=10
    self.timestamp(7),
    self.inputEvent('value', 2.0, id=self.modelId),   # t=7: within first period
    self.timestamp(13),                                # t=13: timer fires (3+10)
    self.timestamp(23),                                # t=23: timer fires again (13+10)
    self.timestamp(24),                                # final flush
)

# Validate with timestamp assertions
self.assertBlockOutput('output', [1.0, 2.0, 2.0])
self.assertGrep('output.evt', expr=self.outputExpr('output', 1.0, time=3))
self.assertGrep('output.evt', expr=self.outputExpr('output', 2.0, time=13))
self.assertGrep('output.evt', expr=self.outputExpr('output', 2.0, time=23))
```

### Common timer testing mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Not advancing time past the timer fire point | Timer never fires, no output | Add `self.timestamp(fireTime)` |
| Final timestamp too close to last timer | Timer doesn't get a chance to output | Add a final flush timestamp after the last expected timer fire |
| Expecting immediate output from a delayed/queued block | Test fails with fewer outputs than expected | Understand whether the block outputs on input or on timer tick |
| Recurring timer period calculation wrong | Outputs at unexpected times | Timer fires at `(creation_time + N * period)` for N=1,2,3... |

---

## Examples

### Boolean gate block (no parameters)

```python
self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.Nand')
self.sendEventStrings(correlator,
                      self.timestamp(1),
                      self.inputEvent('value1', True, id=self.modelId),
                      self.timestamp(2),
                      self.inputEvent('value2', False, id=self.modelId),
                      self.timestamp(20),
                      )
# validate
self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='nandOutput = true')
```

### Block with two inputs that are evaluated together (e.g. binary operations)

For blocks where the output depends on both inputs simultaneously (arithmetic, logic gates), always send both inputs between the same timestamp pair:

```python
self.modelId = self.createTestModel('apamax.analyticsbuilder.blocks.MathOperation',
                                    {'operation': 'add'})
self.sendEventStrings(correlator,
                      self.timestamp(1),
                      self.inputEvent('value1', 10.0, id=self.modelId),  # both in same window
                      self.inputEvent('value2', 5.0, id=self.modelId),
                      self.timestamp(2),
                      )
# validate
self.assertBlockOutput('output', [15.0])  # exactly one output: 10.0 + 5.0
```

### Block with `Value` input (structured properties, e.g. GPS position)

When a block declares a `Value $input_<name>` parameter, the input carries structured data in its `properties` dictionary. In tests, declare the type as `'pulse'` and pass the properties via the `properties=` keyword argument to `inputEvent()`. The first positional argument is `True` (the pulse signal):

```python
self.modelId = self.createTestModel(
    'apamax.analyticsbuilder.custom.DistanceTravelled',
    inputs={'position': 'pulse'},   # Value inputs are declared as 'pulse' in tests
    outputs={'distance': 'float'},
)
self.sendEventStrings(correlator,
    self.timestamp(1),
    self.inputEvent('position', True, id=self.modelId, properties={'lat': 51.5074, 'lng': -0.1278}),
    self.timestamp(2),
    self.inputEvent('position', True, id=self.modelId, properties={'lat': 48.8566, 'lng': 2.3522}),
    self.timestamp(10),
)
# validate
self.assertBlockOutput('distance', [343556.06])
```

> **Rule**: blocks that receive `Value` inputs with `.properties` data — declare `'pulse'` in `createTestModel` and use `inputEvent(..., True, properties={...})`. Never use `'any'`, `'string'`, or `'dictionary<string,any>'` for this case.

---

### Block with parameters and numeric output

```python
self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.AlarmBand',
                                    {'upper': 10.0, 'lower': 5.0})
self.sendEventStrings(correlator,
                      self.timestamp(1),
                      self.inputEvent('value', 3.0, id=self.modelId),
                      self.timestamp(2),
                      )
# validate
self.assertBlockOutput('entered', [False])
```

### Block with numeric float output

```python
self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.IntToFloat64')
self.sendEventStrings(correlator,
                      self.timestamp(1),
                      self.inputEvent('value', 0x4024000000000000, id=self.modelId),
                      self.timestamp(2),
                      )
# validate
self.assertGrep('output.evt', expr=self.outputExpr('floatOutput', 10))
```

---

## Completion Checklist

- [ ] Test file is at `tests/<BlockName>_<NNN>/pysystest.py`
- [ ] `__pysys_title__` and `__pysys_purpose__` are set
- [ ] `blockSourceDir` points to the correct block source directory
- [ ] `createTestModel` uses the correct fully-qualified block ID
- [ ] All block parameters under test are passed to `createTestModel`
- [ ] A final `self.timestamp()` is sent after all inputs
- [ ] Model deployment is asserted with `assertGrep` on the logfile
- [ ] Block output values are asserted with an appropriate assertion method
- [ ] Test passes when run with `cd tests && pysys run <TestDir>`
