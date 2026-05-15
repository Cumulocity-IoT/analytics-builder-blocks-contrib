__pysys_title__   = r""" MathOperation block - Multiplication test. """
#                        =========================================================================
__pysys_purpose__ = r""" MathOperation block - Multiplication test. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')

		# Deploying a new model with multiplication operation.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.blocks.MathOperation',
											{'operation': 'multiplication'})
		self.sendEventStrings(correlator,
							  self.timestamp(1),
							  self.inputEvent('value1', 6.0, id=self.modelId),
						  self.inputEvent('value2', 7.0, id=self.modelId),
						  self.timestamp(2),
						  )

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
						expr='Model "' + self.modelId + '" with PRODUCTION mode has started')
		
		# Verify the output is the product: 6.0 * 7.0 = 42.0
		self.assertBlockOutput('output', [42.0])
