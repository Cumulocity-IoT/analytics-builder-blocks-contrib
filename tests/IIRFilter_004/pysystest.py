__pysys_title__   = r""" IIRFilter block - fast tracking (α=0.9). """
__pysys_purpose__ = r""" IIRFilter block - closely follows raw input with minimal smoothing. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(
			blockSourceDir=f'{self.project.SOURCE}/generated-blocks/')

		correlator.receive('all.evt')

		self.modelId = self.createTestModel(
			'apamax.analyticsbuilder.custom.IIRFilter',
			{'alpha': 0.9},
			inputs={'value': 'float'},
			outputs={'smoothed': 'float'},
		)

		# Sequence: 10.0, 50.0
		# With α=0.9 (fast tracking):
		# y[0] = 10.0 (initialization)
		# y[1] = 0.9*50.0 + 0.1*10.0 = 45.0 + 1.0 = 46.0
		self.sendEventStrings(correlator,
			self.timestamp(1),
			self.inputEvent('value', 10.0, id=self.modelId),
			self.timestamp(2),
			self.inputEvent('value', 50.0, id=self.modelId),
			self.timestamp(10),
		)

	def validate(self):
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')

		# Fast tracking: heavily weighted toward new input value
		self.assertBlockOutput('smoothed', [10.0, 46.0])
