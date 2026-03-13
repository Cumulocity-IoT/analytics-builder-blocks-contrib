__pysys_title__   = r""" XOR block - touch test. """
#                        ================================================================================
__pysys_purpose__ = r""" XOR block - touch test. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploying a new model with correct parameter.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.Xor')
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1),
		                      self.inputEvent('value1', True, id = self.modelId),
		                      self.timestamp(2),
		                      self.inputEvent('value2', False, id = self.modelId),
							  self.timestamp(20)
							  )

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='xorOutput = true')
		

