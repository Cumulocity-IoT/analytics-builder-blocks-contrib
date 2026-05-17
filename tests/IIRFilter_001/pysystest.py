__pysys_title__   = r""" IIRFilter block - first value initialization. """
__pysys_purpose__ = r""" IIRFilter block - on first activation, output equals input. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(
			blockSourceDir=f'{self.project.SOURCE}/generated-blocks/')

		correlator.receive('all.evt')

		self.modelId = self.createTestModel(
			'apamax.analyticsbuilder.custom.IIRFilter',
			{'alpha': 0.5},
			inputs={'value': 'float'},
			outputs={'smoothed': 'float'},
		)

		self.sendEventStrings(correlator,
			self.timestamp(1),
			self.inputEvent('value', 10.0, id=self.modelId),
			self.timestamp(10),
		)

	def validate(self):
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')

		# First value should initialize the filter to the input value
		self.assertBlockOutput('smoothed', [10.0])
