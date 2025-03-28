#
#  $Copyright (c) 2019 Software AG, Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA, and/or its subsidiaries and/or its affiliates and/or their licensors.$
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

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
		self.modelId = self.createTestModel('apamax.analyticskit.blocks.cumulocity.CreateMultiMeasurement',
									  {'deviceId':'d123', 'measurementType': 'c8y_Acceleration'},
									  inputs={'time': None})
		
		self.sendEventStrings(correlator,
							self.inputManagedObject('d123', '' ,'',[],[],[],[],[],[],{},{'c8y_IsDevice':{}}))

		self.sendEventStrings(correlator,
		                      self.timestamp(1),
		                      self.inputEvent('value', True, id = self.modelId, 
										properties={'c8y_Acceleration.x':{'value':1.0,'unit':'m/s2'},'c8y_Acceleration.y':{'value':0.0,'unit':'m/s2'},'c8y_Acceleration.z':{'value':3.0,'unit':'m/s2'}}),
		                      self.timestamp(2)
							  )

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		self.assertGrep("waiter.out", expr='com.apama.cumulocity.Measurement\("","c8y_Acceleration","d123",1,{"c8y_Acceleration":{"x":com.apama.cumulocity.MeasurementValue\(1,"m/s2",{}\),"y":com.apama.cumulocity.MeasurementValue\(0,"m/s2",{}\),"z":com.apama.cumulocity.MeasurementValue\(3,"m/s2",{}\)}},{"apama_analytics_modelName":any\(string,"model_0"\)}\)')
		