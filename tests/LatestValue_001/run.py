# Copyright (c) 2025 Cumulocity GmbH, Düsseldorf, Germany and/or its licensors
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except 
# in compliance with the License. You may obtain a copy of the License at 
# http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, 
# software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES 
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language 
# governing permissions and limitations under the License.


from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest
import json

class PySysTest(AnalyticsBuilderBaseTest):

	def inputManagedObject(self, id, type, name, supportedOperations=[], supportedMeasurements=[], childDeviceIds=[], childAssetIds=[],deviceParentIds=[], assetParentIds=[], position={}, params={}):
		"""
		Generate the string form of a managed object event.
		:param id: Unique device identifier of the device.
		:param name: Name of the device.
		:param supportedOperations: A list of supported operations for this device.
		:param supportedMeasurements: A list of supported measurements for this device.
		:param childDeviceIds: The identifiers of the child devices.
		:param childAssetIds: The identifiers of the child assets.
		:param deviceParentIds: The identifiers of the parent devices.
		:param assetParentIds: The identifiers of the parent assets.
		:param position: Contains 'lat', 'lng', 'altitude' and 'accuracy'.
		:param params: Other fragments for the managed object.
		"""
		managedObjectParams = ', '.join([json.dumps(id), json.dumps(type), json.dumps(name), json.dumps(supportedOperations), json.dumps(supportedMeasurements),
								json.dumps(childDeviceIds), json.dumps(childAssetIds), json.dumps(deviceParentIds),
								json.dumps(assetParentIds),
								json.dumps(json.dumps(position)),
								json.dumps(json.dumps(params))])
		return f'apamax.analyticsbuilder.test.SendManagedObject({managedObjectParams})'

	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/cumulocity-blocks/')
		
		correlator.injectEPL(self.input + '/SendC8yObjects.mon')

		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploying a new model with correct parameter.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.blocks.cumulocity.LatestValue',
									  {'deviceId':'d123', 'fragmentSeries': 'c8y_Acceleration.X'})
		
		self.sendEventStrings(correlator,
							self.inputManagedObject('d123', '' ,'',[],[],[],[],[],[],{},{'c8y_IsDevice':{}}))

		self.sendEventStrings(correlator,
		                      self.timestamp(1),
							  self.timestamp(10),
							  )

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		self.assertGrep("waiter.out", expr='apamax.analyticsbuilder.test.Output\("latest","model_0","apama.analyticsbuilder.Partition_Default\(\)",0,any\(float,12\),{}\)')
		