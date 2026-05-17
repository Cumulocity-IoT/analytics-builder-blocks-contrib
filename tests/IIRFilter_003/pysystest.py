__pysys_title__   = r""" IIRFilter block - moderate smoothing (α=0.5). """
__pysys_purpose__ = r""" IIRFilter block - balanced blend of new input and previous smoothed value. """

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

		# Sequence: 0.0, 100.0
		# With α=0.5 (moderate smoothing):
		# y[0] = 0.0 (initialization)
		# y[1] = 0.5*100.0 + 0.5*0.0 = 50.0 + 0.0 = 50.0
		self.sendEventStrings(correlator,
			self.timestamp(1),
			self.inputEvent('value', 0.0, id=self.modelId),
			self.timestamp(2),
			self.inputEvent('value', 100.0, id=self.modelId),
			self.timestamp(10),
		)

	def validate(self):
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')

		# Moderate smoothing: equal weight to new input and previous value
		self.assertBlockOutput('smoothed', [0.0, 50.0])
