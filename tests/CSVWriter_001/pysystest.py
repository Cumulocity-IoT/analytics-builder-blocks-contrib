__pysys_title__   = r""" CSVWriter block - touch test. """
#                        ================================================================================
__pysys_purpose__ = r""" CSVWriter block - touch test. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploying a new model with correct parameter.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.CSVWriter')
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1),
		                      self.inputEvent('value', '{"infile": [{"field1": 11,"field2": 12,"field3": 13},{"field1": 21,"field2": 22,"field3": 23},{"field1": 31,"field2": 32,"field3": 33}]}', id = self.modelId),
		                      self.timestamp(2)
							  )

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		self.outputFromBlock('csvOutput','field1,field2,field3\n11,12,13\n21,22,23\n31,32,33')
		

