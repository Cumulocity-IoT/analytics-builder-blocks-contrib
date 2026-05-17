__pysys_title__   = r""" IIRFilter block - heavy smoothing (α=0.1). """
__pysys_purpose__ = r""" IIRFilter block - heavily smoothed series lags behind raw changes. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(
			blockSourceDir=f'{self.project.SOURCE}/generated-blocks/')

		correlator.receive('all.evt')

		self.modelId = self.createTestModel(
			'apamax.analyticsbuilder.custom.IIRFilter',
			{'alpha': 0.1},
			inputs={'value': 'float'},
			outputs={'smoothed': 'float'},
		)

		# Sequence of inputs: 10.0, 20.0, 30.0
		# With α=0.1 (heavy smoothing):
		# y[0] = 10.0 (initialization)
		# y[1] = 0.1*20.0 + 0.9*10.0 = 2.0 + 9.0 = 11.0
		# y[2] = 0.1*30.0 + 0.9*11.0 = 3.0 + 9.9 = 12.9
		self.sendEventStrings(correlator,
			self.timestamp(1),
			self.inputEvent('value', 10.0, id=self.modelId),
			self.timestamp(2),
			self.inputEvent('value', 20.0, id=self.modelId),
			self.timestamp(3),
			self.inputEvent('value', 30.0, id=self.modelId),
			self.timestamp(10),
		)

	def validate(self):
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')

		# Heavy smoothing causes lag: outputs [10.0, 11.0, 12.9] despite input jumps
		self.assertBlockOutput('smoothed', [10.0, 11.0, 12.9])
