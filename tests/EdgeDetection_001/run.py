#
#  $Copyright (c) 2019 Software AG, Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA, and/or its subsidiaries and/or its affiliates and/or their licensors.$
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploying a new model with correct parameter.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.EdgeDetection',{'threshold':1.0})
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1),
		                      self.inputEvent('value', 1.5, id = self.modelId),
		                      self.timestamp(2),
							  self.inputEvent('value', 2.9, id = self.modelId),
		                      self.timestamp(4),
							  self.inputEvent('value', 1.9, id = self.modelId),
		                      self.timestamp(5),
							  self.inputEvent('value', 2.3, id = self.modelId),
		                      self.timestamp(6),
							  self.inputEvent('value', 1.1, id = self.modelId),
		                      self.timestamp(7),
							  self.inputEvent('value', 8.0, id = self.modelId),
		                      self.timestamp(8),
							  self.inputEvent('value', 9.5, id = self.modelId),
		                      self.timestamp(9),
							  self.inputEvent('value', 9.2, id = self.modelId),
		                      self.timestamp(10),
							  self.inputEvent('value', 8.8, id = self.modelId),
		                      self.timestamp(11),
							  self.inputEvent('value', 9.6, id = self.modelId),
		                      self.timestamp(12),
							  self.inputEvent('value', 1.6, id = self.modelId),
		                      self.timestamp(13),
							  self.inputEvent('value', 2.6, id = self.modelId),
		                      self.timestamp(14)
							  )

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		OUTPUT_REGEX = r'apamax.analyticsbuilder.test.Output[(]"%(outputId)s","%(modelId)s","[^"]*",%(time)s,any[(][^"]*,(.*)[)],[{].*[}][)]'
		self.assertThat("expected == output", expected='true', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'isEdge', 'modelId':'model_0','time':7}).group(1)")
		
		
			
		