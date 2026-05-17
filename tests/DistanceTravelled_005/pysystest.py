__pysys_title__   = r""" DistanceTravelled block - invalid position with missing latitude. """
__pysys_purpose__ = r""" DistanceTravelled block - invalid position with missing latitude. """

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

		# First: valid position
		# Second: position missing latitude (only has longitude)
		# Third: another valid position
		# The invalid position should be skipped (no output, not stored as previous)
		self.sendEventStrings(correlator,
			self.timestamp(1),
			self.inputEvent('position', True, id=self.modelId, properties={'lat': 51.5074, 'lng': -0.1278}),
			self.timestamp(2),
			self.inputEvent('position', True, id=self.modelId, properties={'lng': 2.3522}),
			self.timestamp(3),
			self.inputEvent('position', True, id=self.modelId, properties={'lat': 48.8566, 'lng': 2.3522}),
			self.timestamp(10),
		)

	def validate(self):
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')

		# Only one output: distance from first valid position to third position
		# (the second position is skipped because it lacks latitude)
		# Distance from 51.5074°N, 0.1278°W to 48.8566°N, 2.3522°E: approximately 343.56 km
		self.assertBlockOutput('distance', [343556.06])
