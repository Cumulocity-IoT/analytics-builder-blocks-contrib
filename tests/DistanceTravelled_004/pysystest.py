__pysys_title__   = r""" DistanceTravelled block - antipodal points (half Earth circumference). """
__pysys_purpose__ = r""" DistanceTravelled block - antipodal points (half Earth circumference). """

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

		# Antipodal points (opposite sides of Earth): 0°N, 0°E and 0°N, 180°E
		# Distance is half Earth's circumference: approximately 20,015,086.8 meters
		self.sendEventStrings(correlator,
			self.timestamp(1),
			self.inputEvent('position', True, id=self.modelId, properties={'lat': 0.0, 'lng': 0.0}),
			self.timestamp(2),
			self.inputEvent('position', True, id=self.modelId, properties={'lat': 0.0, 'lng': 180.0}),
			self.timestamp(10),
		)

	def validate(self):
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')

		# Distance from equator 0° to equator 180° is half Earth's circumference
		self.assertBlockOutput('distance', [20015086.8])
