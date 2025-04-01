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
		self.modelId = self.createTestModel('apamax.analyticsbuilder.blocks.ReceiveAsyncSignal',{'signalType':'Reset', 'scopeToModel': True})
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1),
							  'apamax.analyticsbuilder.blocks.AsyncSignal("Reset","'+self.modelId+'",any(apama.analyticsbuilder.Partition_Default,apama.analyticsbuilder.Partition_Default()),{})',
							  self.timestamp(2),
							  'apamax.analyticsbuilder.blocks.AsyncSignal("Reset","'+self.modelId+'",any(apama.analyticsbuilder.Partition_Default,apama.analyticsbuilder.Partition_Default()),{"a":any(float,100)})',
							  self.timestamp(3),
							  channel='apamax.analyticsbuilder.blocks.AsyncSignal')

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		self.assertBlockOutput('value', [True, True])
		self.assertThat('outputs == expected', outputs = [value['properties'] for value in self.allOutputFromBlock()], expected = [
			{},
			{'a':100.0}
			])

		