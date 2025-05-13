__pysys_title__   = r""" Category Logging - Base Functionality """ 
#                        ================================================================================
__pysys_purpose__ = r""" Checks that the Logging block is able to log messages at different levels. """ 
	
__pysys_created__ = "2025-05-13"
#__pysys_skipped_reason__   = "Skipped until Bug-1234 is fixed"

#__pysys_traceability_ids__ = "Bug-1234, UserStory-456" 
#__pysys_groups__           = "myGroup, disableCoverage, performance"
#__pysys_modes__            = lambda helper: helper.inheritedModes + [ {'mode':'MyMode', 'myModeParam':123}, ]
#__pysys_parameterized_test_modes__ = {'MyParameterizedSubtestModeA':{'myModeParam':123}, 'MyParameterizedSubtestModeB':{'myModeParam':456}, }

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest


class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploying a new model with correct parameter.
		model1 = self.createTestModel('apamax.analyticsbuilder.custom.Logging', id = 'WARNModel',
									  parameters = {'logLevel':'WARN'})
		
		model2 = self.createTestModel('apamax.analyticsbuilder.custom.Logging', id = 'INFOModel',
									  parameters ={'logLevel':'INFO'})
		
		model3 = self.createTestModel('apamax.analyticsbuilder.custom.Logging', id = 'CRITModel',
								parameters ={'logLevel':'CRIT'})
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1),
		                      self.inputEvent('object', 0x4024000001000306, id = model1),
							  self.inputEvent('object', 'a string value', id = model2),
							  self.inputEvent('object', True, id = model3),
		                      self.timestamp(2)
							  )
		pass

	def validate(self):
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='WARN.*4621819117605750000')
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='INFO.*a string value')
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='CRIT.*true')
		pass
