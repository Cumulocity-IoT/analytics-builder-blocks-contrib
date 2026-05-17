__pysys_title__   = r""" DistanceTravelled block - first position produces no output. """
__pysys_purpose__ = r""" DistanceTravelled block - first position produces no output. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(
			blockSourceDir=f'{self.project.SOURCE}/generated-blocks/')

		correlator.receive('all.evt')

		self.modelId = self.createTestModel(
			'apamax.analyticsbuilder.custom.DistanceTravelled',
			inputs={'position': 'pulse'},
			outputs={'distance': 'float'},
		)

		self.sendEventStrings(correlator,
			self.timestamp(1),
			self.inputEvent('position', True, id=self.modelId, properties={'lat': 51.5074, 'lng': -0.1278}),
			self.timestamp(10),
		)

	def validate(self):
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')

		# First position should produce no output
		self.assertBlockOutput('distance', [])
