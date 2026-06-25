#
#  $Copyright (c) 2019 Software AG, Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA, and/or its subsidiaries and/or its affiliates and/or their licensors.$
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/../blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploying a new model with correct parameter.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.LowpassFilter',{'cutoff':1.0, 'windowDurationSec':5.0})
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1582902000),
		                      self.inputEvent('value', 3.5, id = self.modelId),
		                      self.timestamp(1582902005),
							  self.inputEvent('value', 5.5, id = self.modelId),
                              self.timestamp(1582902005.1),
                              self.inputEvent('value', 6.5, id = self.modelId),
                              self.timestamp(1582902005.2),
                              self.inputEvent('value', 5.7, id = self.modelId),
		                      self.timestamp(1582902006),
							  self.inputEvent('value', 7.5, id = self.modelId),
                              self.timestamp(1582902006.1),
                              self.inputEvent('value', 8.5, id = self.modelId),
                              self.timestamp(1582902006.2),
                              self.inputEvent('value', 18.5, id = self.modelId),
                              self.timestamp(1582902006.3),
                              self.inputEvent('value', 12.5, id = self.modelId),
                              self.timestamp(1582902006.4),
                              self.inputEvent('value', 13.0, id = self.modelId),
		                      self.timestamp(1582902007),
							  self.inputEvent('value', 2.7, id = self.modelId),
                              self.timestamp(1582902007.1),
                              self.inputEvent('value', 12.7, id = self.modelId),
                              self.timestamp(1582902007.2),
                              self.inputEvent('value', 1.7, id = self.modelId),
                              self.timestamp(1582902007.3),
                              self.inputEvent('value', 4.7, id = self.modelId),
                              self.timestamp(1582902007.4),
                              self.inputEvent('value', 5.7, id = self.modelId),
		                      self.timestamp(1582902008),
							  self.inputEvent('value', 5.0, id = self.modelId),
                              self.timestamp(1582902008.1),
                              self.inputEvent('value', 15.0, id = self.modelId),
                              self.timestamp(1582902008.2),
                              self.inputEvent('value', 5.0, id = self.modelId),
		                      self.timestamp(1582902009),
                              self.inputEvent('value', 8.0, id = self.modelId),
                              self.timestamp(1582902009.1),
                              self.inputEvent('value', 7.0, id = self.modelId),
		                      self.timestamp(1582902025)
							  )

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		self.assertGrep('output.evt', expr=self.outputExpr('filtered', properties='.*"lowpassFilter":any.*sequence.*float.*,.*0,0,0,0,1,1,1,1.*'), contains=True)
		self.assertGrep('output.evt', expr=self.outputExpr('filtered', properties='.*"lowpassFilter":any.*sequence.*float.*,.*0,0,0,0,1,1,1.*'), contains=True)
		self.assertGrep('output.evt', expr=self.outputExpr('filtered', properties='.*"lowpassFilter":any.*sequence.*float.*,.*0,0,0,0,1,1,1,2.*'), contains=False)
		self.assertGrep('output.evt', expr=self.outputExpr('filtered', properties='.*"lowpassFilter":any.*sequence.*float.*,.*0,0,0,0,1,1,1.*'), contains=True)
		self.assertGrep('output.evt', expr=self.outputExpr('filtered', properties='.*"lowpassFilter":any.*sequence.*float.*,.*0,0,0,1,1,1,2.*'), contains=False)
		self.assertGrep('output.evt', expr=self.outputExpr('filtered', properties='.*"lowpassFilter":any.*sequence.*float.*,.*0,0,0,1,1,1.*'), contains=True)
		self.assertGrep('output.evt', expr=self.outputExpr('filtered', properties='.*"lowpassFilter":any.*sequence.*float.*,.*0,1,2,3.*'), contains=False)
		self.assertGrep('output.evt', expr=self.outputExpr('filtered', properties='.*"lowpassFilter":any.*sequence.*float.*,.*0,1.*'), contains=True)
