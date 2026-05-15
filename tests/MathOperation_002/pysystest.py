__pysys_title__   = r""" MathOperation block - Subtraction test. """
#                        =========================================================================
__pysys_purpose__ = r""" MathOperation block - Subtraction test. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')

		# Deploying a new model with subtraction operation.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.blocks.MathOperation',
											{'operation': 'substraction'})
		self.sendEventStrings(correlator,
							  self.timestamp(1),
							  self.inputEvent('value1', 20.0, id=self.modelId),
						  self.inputEvent('value2', 8.0, id=self.modelId),
						  self.timestamp(2),
						  )

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
						expr='Model "' + self.modelId + '" with PRODUCTION mode has started')
		
		# Verify the output is the difference: 20.0 - 8.0 = 12.0
		self.assertBlockOutput('output', [12.0])
