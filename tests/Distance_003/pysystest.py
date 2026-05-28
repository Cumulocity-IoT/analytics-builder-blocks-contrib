__pysys_title__   = r""" DistanceTravelled block - zero distance for identical positions. """
__pysys_purpose__ = r""" DistanceTravelled block - zero distance for identical positions. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(
			blockSourceDir=f'{self.project.SOURCE}/blocks/')

		correlator.receive('all.evt')

		self.modelId = self.createTestModel(
			'apamax.analyticsbuilder.custom.Distance',
			inputs={'position': 'pulse'},
			outputs={'distance': 'float'},
		)

		# Identical positions: should output 0.0 meters
		self.sendEventStrings(correlator,
			self.timestamp(1),
			self.inputEvent('position', True, id=self.modelId, properties={'lat': 40.7128, 'lng': -74.0060}),
			self.timestamp(2),
			self.inputEvent('position', True, id=self.modelId, properties={'lat': 40.7128, 'lng': -74.0060}),
			self.timestamp(10),
		)

	def validate(self):
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')

		# Distance from a point to itself is zero
		self.assertBlockOutput('distance', [0.0])
