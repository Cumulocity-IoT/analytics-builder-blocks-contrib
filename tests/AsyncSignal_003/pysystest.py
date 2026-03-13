__pysys_title__   = r""" Async Send Signal block - test model scope. """
#                        ================================================================================
__pysys_purpose__ = r""" Aync Send Signal - test. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploying a new model with correct parameter.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.blocks.SendAsyncSignal',{'signalType':'Reset', 'scopeToModel': True})
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1),
		                      self.inputEvent('send', True, id = self.modelId),
		                      self.timestamp(2),
							  self.inputEvent('send', False, id = self.modelId),
							  self.timestamp(3),
							  self.inputEvent('params', True, id = self.modelId, properties={'a':100}),
							  self.inputEvent('send', True, id = self.modelId),
							  self.timestamp(5)
							  )

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		self.assertGrep("waiter.out", expr=re.escape('apamax.analyticsbuilder.blocks.AsyncSignal("Reset","'+self.modelId+'",any(apama.analyticsbuilder.Partition_Default,apama.analyticsbuilder.Partition_Default()),{})'))
		self.assertGrep("waiter.out", expr=re.escape('apamax.analyticsbuilder.blocks.AsyncSignal("Reset","'+self.modelId+'",any(apama.analyticsbuilder.Partition_Default,apama.analyticsbuilder.Partition_Default()),{"a":any(float,100)})'))
		
