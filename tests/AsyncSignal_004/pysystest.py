__pysys_title__   = r""" Async Receive Signal block - test scoped to model. """
#                        ================================================================================
__pysys_purpose__ = r""" Aync Receive Signal - test. """

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

		
