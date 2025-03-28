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
		self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.AlarmBand',{'upper':10.0,'lower':5.0})
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1),
		                      self.inputEvent('value', 3.0, id = self.modelId),
		                      self.timestamp(2),
							  self.inputEvent('value', 5.5, id = self.modelId),
		                      self.timestamp(3),
							  self.inputEvent('value', 7.5, id = self.modelId),
		                      self.timestamp(4),
							  self.inputEvent('value', 12.0, id = self.modelId),
		                      self.timestamp(5),
							  self.inputEvent('value', 6.0, id = self.modelId),
		                      self.timestamp(6),
							  self.inputEvent('value', 3.0, id = self.modelId),
		                      self.timestamp(7)
							  )

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		OUTPUT_REGEX = r'apamax.analyticsbuilder.test.Output[(]"%(outputId)s","%(modelId)s","[^"]*",%(time)s,any[(][^"]*,(.*)[)],[{].*[}][)]'
		self.assertThat("expected == output", expected='true', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'entered', 'modelId':'model_0','time':2}).group(1)")
		self.assertThat("expected == output", expected='false', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'left', 'modelId':'model_0','time':2}).group(1)")
		self.assertThat("expected == output", expected='false', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'up', 'modelId':'model_0','time':2}).group(1)")
		self.assertThat("expected == output", expected='false', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'down', 'modelId':'model_0','time':2}).group(1)")
		
		self.assertThat("expected == output", expected='true', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'entered', 'modelId':'model_0','time':3}).group(1)")
		self.assertThat("expected == output", expected='false', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'left', 'modelId':'model_0','time':3}).group(1)")
		self.assertThat("expected == output", expected='false', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'up', 'modelId':'model_0','time':3}).group(1)")
		self.assertThat("expected == output", expected='false', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'down', 'modelId':'model_0','time':3}).group(1)")
		
		self.assertThat("expected == output", expected='false', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'entered', 'modelId':'model_0','time':3.9999999999999996}).group(1)")
		self.assertThat("expected == output", expected='true', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'left', 'modelId':'model_0','time':3.9999999999999996}).group(1)")
		self.assertThat("expected == output", expected='true', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'up', 'modelId':'model_0','time':3.9999999999999996}).group(1)")
		self.assertThat("expected == output", expected='false', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'down', 'modelId':'model_0','time':3.9999999999999996}).group(1)")
		
		self.assertThat("expected == output", expected='true', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'entered', 'modelId':'model_0','time':5}).group(1)")
		self.assertThat("expected == output", expected='false', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'left', 'modelId':'model_0','time':5}).group(1)")
		self.assertThat("expected == output", expected='false', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'up', 'modelId':'model_0','time':5}).group(1)")
		self.assertThat("expected == output", expected='false', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'down', 'modelId':'model_0','time':5}).group(1)")
		
		self.assertThat("expected == output", expected='false', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'entered', 'modelId':'model_0','time':6}).group(1)")
		self.assertThat("expected == output", expected='true', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'left', 'modelId':'model_0','time':6}).group(1)")
		self.assertThat("expected == output", expected='false', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'up', 'modelId':'model_0','time':6}).group(1)")
		self.assertThat("expected == output", expected='true', output__eval="self.assertGrep('output.evt', expr=OUTPUT_REGEX%{'outputId':'down', 'modelId':'model_0','time':6}).group(1)")
		
			
		