__pysys_title__   = r""" DistanceTravelled block - distance between two positions. """
__pysys_purpose__ = r""" DistanceTravelled block - distance between two positions. """

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

		# Equator 1 degree apart: 0°N, 0°E to 0°N, 1°E
		# One degree of longitude at equator is approximately 111.19 km (111194.93 meters)
		self.sendEventStrings(correlator,
			self.timestamp(1),
			self.inputEvent('position', True, id=self.modelId, properties={'lat': 0.0, 'lng': 0.0}),
			self.timestamp(2),
			self.inputEvent('position', True, id=self.modelId, properties={'lat': 0.0, 'lng': 1.0}),
			self.timestamp(10),
		)

	def validate(self):
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')

		# Distance at equator for 1 degree of longitude: approximately 111,194.93 meters
		self.assertBlockOutput('distance', [111194.93])
