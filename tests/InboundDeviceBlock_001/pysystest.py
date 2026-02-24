#
#  Copyright (c) 2019-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'InboundDeviceBlock: to check the basic working of the block'
__pysys_purpose__ = r''

import json
from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def _injectCumulocitySupport(self, corr):
		AnalyticsBuilderBaseTest._injectCumulocitySupport(self, corr)
		self._injectEPLOnce(corr, [self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['Base64']])  
		self._injectEPLOnce(corr, [self.project.testRootDir+'/utils/DeviceServiceMock.mon'])

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/cumulocity-blocks/')
		
		self.modelId = self.createTestModel('apamax.analyticskit.blocks.cumulocity.DeviceInput', {
			'transport': 'mqtt',
			'topic': 'topicName',
		}, id="model1")
		
		self.sendEventStrings(self.correlator, self.timestamp(1))
		# correct (first client)
		self.correlator.sendEventStrings('com.apama.cumulocity.devices.DeviceMessage("mqtt","clientFoo","topicName",{},any(string,"SGVsbG8gV29ybGQ="))', channel="devicesubscribechannel0")
		# wrong transport
		self.correlator.sendEventStrings('com.apama.cumulocity.devices.DeviceMessage("badTransport","clientFoo","topicName",{},any(string,"SGVsbG8gV29ybGQ="))', channel="devicesubscribechannel0")
		# wrong topic
		self.correlator.sendEventStrings('com.apama.cumulocity.devices.DeviceMessage("mqtt","clientFoo","badTopic",{},any(string,"SGVsbG8gV29ybGQ="))', channel="devicesubscribechannel0")
		# correct (second client)
		self.correlator.sendEventStrings('com.apama.cumulocity.devices.DeviceMessage("mqtt","clientBar","topicName",{},any(string,"SGVsbG8gV29ybGQ="))', channel="devicesubscribechannel1")
		self.sendEventStrings(self.correlator, self.timestamp(2))

	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs()
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')

		output = self.allOutputFromBlock(self.modelId)

		self.assertThat("len(output) == 2", output=output)
		self.assertThat("output[0]['value'] == 'SGVsbG8gV29ybGQ='", output=output)
		self.assertThat("output[0]['properties'] == {'clientID': 'clientFoo', 'topic': 'topicName', 'transport': 'mqtt', 'transportProperties': {}}", output=output)
		self.assertThat("output[1]['value'] == 'SGVsbG8gV29ybGQ='", output=output)
		self.assertThat("output[1]['properties'] == {'clientID': 'clientBar', 'topic': 'topicName', 'transport': 'mqtt', 'transportProperties': {}}", output=output)
	
