#
# Copyright (c) 2025 Cumulocity GmbH, Düsseldorf, Germany and/or its licensors
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except 
# in compliance with the License. You may obtain a copy of the License at 
# http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, 
# software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES 
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language 
# governing permissions and limitations under the License.
#

__pysys_title__   = r""" Rate Limiter - Basic test """
#                        ========================================================================================================================

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploying a new model with correct parameter.
		self.modelId = self.createTestModel('apamax.analyticskit.blocks.cumulocity.RateLimiter',{'windowDuration':120.0, 'limit': 5.0})
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1),
		                      self.inputEvent('value', True, id = self.modelId),
		                      self.timestamp(10),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(20),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(30),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(40),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(50),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(60),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(120),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(130),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(140),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(150),
							  self.timestamp(180),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(240),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(250),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(260),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(310),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(320),
							  self.inputEvent('value', True, id = self.modelId),
							  self.timestamp(330)
							  )

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		self.assertGrep('output.evt', expr=self.outputExpr('trigger', None, time=40))
		self.assertGrep('output.evt', expr=self.outputExpr('trigger', None, time=140))
		self.assertGrep('output.evt', expr=self.outputExpr('trigger', None, time=320))