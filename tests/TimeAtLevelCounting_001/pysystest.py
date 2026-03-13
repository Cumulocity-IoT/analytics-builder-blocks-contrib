__pysys_title__   = r""" Time at Level Counting block - touch test. """
#                        ================================================================================
__pysys_purpose__ = r""" Time at Level Counting block - touch test. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/',initialCorrelatorTime=1582902000.0)
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploying a new model with correct parameter.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.TimeAtLevelCounting', {'threshold':50.0})
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1582902000),
		                      self.inputEvent('value', 49.0, id = self.modelId),
		                      self.timestamp(1582903000),
		                      self.inputEvent('value', 50.0, id = self.modelId),
		                      self.timestamp(1582903010),
		                      self.inputEvent('value', 51.5, id = self.modelId),
		                      self.timestamp(1582903910),
		                      self.inputEvent('value', 55.9, id = self.modelId),
		                      self.timestamp(1582904000),
							  self.inputEvent('value',50.0, id = self.modelId),
							  self.timestamp(1582904500),
							  self.inputEvent('value', 49.99, id = self.modelId),
		                      self.timestamp(1582905000),
							  self.inputEvent('value', 47.00, id = self.modelId),
		                      self.timestamp(1582905200),
							  self.inputEvent('value', 50.01, id = self.modelId),
		                      self.timestamp(1582906000),
							  self.inputEvent('value', 48.0, id = self.modelId),
		                      self.timestamp(1582907000),
							  )

	def validate(self):

		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		self.outputFromBlock('timeAtLevelOutput',[0.0],time=1582902000)
		self.outputFromBlock('timeAtLevelOutput',[0],time=1582903000)
		self.outputFromBlock('timeAtLevelOutput',[10],time=1582903010)
		self.outputFromBlock('timeAtLevelOutput',[910],time=1582903910)
		self.outputFromBlock('timeAtLevelOutput',[1000],time=1582904000)
		self.outputFromBlock('timeAtLevelOutput',[0],time=1582904500)
		self.outputFromBlock('timeAtLevelOutput',[0],time=1582905000)
		self.outputFromBlock('timeAtLevelOutput',[0],time=1582905200)
		self.outputFromBlock('timeAtLevelOutput',[0],time=1582906000)
