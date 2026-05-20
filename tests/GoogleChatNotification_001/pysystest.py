__pysys_title__   = r""" Google Chat Notification Smoke Test """ 
#                        ================================================================================
__pysys_purpose__ = r""" Smoke test to verify the GoogleChatNotification block deploys and processes triggers correctly """ 
	
__pysys_created__ = "2025-05-18"

import pysys.basetest, pysys.mappers
from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')
		
		# engine_receive process listening on all channels.
		correlator.receive('all.evt')

		# Deploy model with a valid webhook URL and a default message parameter.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.GoogleChatNotification',
			{'webhookUrl': 'https://chat.googleapis.com/v1/spaces/test/messages?key=testkey&token=testtoken',
			 'message': 'Hello from test'})

		# Send a trigger pulse to fire the notification.
		self.sendEventStrings(correlator,
			self.timestamp(1),
			self.inputEvent('trigger', True, id=self.modelId),
			self.timestamp(2),
			self.timestamp(3))

		correlator.flush(10)

	def validate(self):
		# Verify model started in PRODUCTION mode.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		# Verify no ERROR-level log lines.
		self.assertLineCount(self.analyticsBuilderCorrelator.logfile, expr='.*ERROR.*', condition="==0")
		# Verify the block initialized its HTTP transport.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='GoogleChatNotification: Initialized HTTP transport for host chat.googleapis.com')
