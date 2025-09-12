__pysys_title__   = r""" Http Output Tests """ 
#                        ================================================================================
__pysys_purpose__ = r""" Test calling GET items via HTTP""" 
	
__pysys_created__ = "2025-06-05"

import pysys.basetest, pysys.mappers
from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	
	def ABStartPython(self, script, args, ignoreExitStatus=False, stdouterr=None, environs=None, pythonPaths=None, **kwargs):
		"""
		Starts a python process, using the same python version and environment the tests are running under (python 3)
		@param script: .py file from input dir or absolute path
		@param stdouterr: the prefix to use for std out and err files
		@param environs: additional env vars which will override those in the parent process
		@param pythonPaths: additional python paths
		"""
		script = os.path.join(self.input, script)
		assert os.path.exists(script), script
		if not stdouterr: stdouterr = os.path.basename(script)

		env = dict(os.environ)
		env['PYTHONDONTWRITEBYTECODE'] = 'true'
		if environs: env.update(environs)
		env['PYTHONUNBUFFERED'] = 'true'
		if pythonPaths:
			env['PYTHONPATH'] = os.pathsep.join(pythonPaths) + os.pathsep + env.get('PYTHONPATH', '')

		try:
			return self.startProcess(sys.executable, [script]+args,
				ignoreExitStatus=ignoreExitStatus, stdout=stdouterr+'.out', stderr=stdouterr+'.err',
				displayName='python3 '+kwargs.pop('displayName', stdouterr), environs=env, **kwargs)
		except Exception:
			self.logFileContents(stdouterr+'.err') or self.logFileContents(stdouterr+'.out')
			raise
		
	def execute(self):
		# Using available port for HTTP connection.
		self.httpConPort = self.getNextAvailableTCPPort()
		
		# Starting dummy HTTP server.
		server = self.ABStartPython('server.py', [str(self.httpConPort)], stdouterr='test-http-server', state=BACKGROUND)
		self.waitForSocket(self.httpConPort, process=server)
		
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploying a new model with correct parameter.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.HTTPOutput',{'method':'GET', 
																				   'auth_type': 'No Auth',
																					 'url':'http://localhost:'+str(self.httpConPort) + '/items/#{id}'})
		# Simple GET with item id = 200
		self.sendEventStrings(correlator,
		                      self.timestamp(1),
		                      self.inputEvent('value', 1.5, id = self.modelId),
							  self.inputEvent('substituteInfo', True, id = self.modelId, properties={'id': "1"}),
							  self.timestamp(2),
							  self.timestamp(3),
							  self.timestamp(4))
		# Simple GET with missing item id = 404
		self.sendEventStrings(correlator,
		                      self.inputEvent('value', 1.5, id = self.modelId),
							  self.inputEvent('substituteInfo', True, id = self.modelId, properties={'id': "2"}),
							  self.timestamp(5),
							  self.timestamp(6),
							  self.timestamp(7))
		

		pass

	def validate(self):
		self.assertBlockOutput('statusCode', [200.0, 404.0])
		self.assertBlockOutput('responseBody', [True, True])
		self.assertLineCount(self.analyticsBuilderCorrelator.logfile, expr='.*ERROR.*', condition="==0")
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		pass
