#
#  Copyright (c) 2019-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'Python block: to check the basic working of the block'
__pysys_purpose__ = r''

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/python-blocks/', arguments=["--config", f"{self.project.SOURCE}/python-blocks/PythonFunction/", "-Dstreaminganalytics.pythonBlockRequirements=six", "-Dstreaminganalytics.pythonBlockPackages=six xml xml.etree xml.etree.ElementTree", '-v', 'plugins.PythonBlockPlugin=DEBUG'])

		self.modelId1 = self.createTestModel('apamax.analyticsbuilder.blocks.PythonFunction', {
			'label': 'Python Test Model',
			'param1': 'data',
			'pythonFunction':"import math, operator, json, six\nfrom base64 import b64encode, b64decode\nimport collections.abc\nfrom collections.abc import Iterable\nimport xml.etree#\nfrom xml import etree\nfrom xml.etree.ElementTree import Element"+"""
def onInput(inputs, context):
	context.logger.info("Processing inputs: " + str([i.value for i in inputs]))
	(a, b) = (inputs[0].value, inputs[1].value)
	context.setState("counter", context.getState("counter", 0.) + 1.)
	if a and b:
		return [
			math.fabs(a-b),
			operator.sub(a, b),
			Value(True, {'value1': inputs[0].properties['value1'], 'value2': inputs[1].properties['value2']}),
			Value(context.getState("counter")),
			context.params[0]
		]
	else:
		return None
"""
		})
		self.modelId2 = self.createTestModel('apamax.analyticsbuilder.blocks.PythonFunction', {})
		
		self.sendEventStrings(self.correlator,
								self.timestamp(1),
								self.inputEvent('value1', 12.25, id = self.modelId1, properties={'value1': 'value'}),
								self.timestamp(2),
								self.inputEvent('value2', 7.75, id = self.modelId1, properties={'value2': 'value'}),  #absolute Output at this point would be 4.5 (12.25-7.75)
								self.timestamp(2.1),
								self.inputEvent('value2', 17.25, id=self.modelId1, properties={'value2': 'value'}),  #signed Output at this point would be -5 (12.25-17.25)
								self.timestamp(2.5),
							  )


	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(errorIgnores=['InvalidParameterException - Python function must be provided and cannot be the default placeholder'], warnIgnores=['Python path element does not exist', 'InvalidParameterException is not localized'])
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='InvalidParameterException - Python function must be provided and cannot be the default placeholder')
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId1 + '\" with PRODUCTION mode has started')
		
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Processing inputs')
		
		# Verifying the result - output from the block.
		self.assertBlockOutput('result1', [4.5, 5])
		self.assertBlockOutput('result2', [4.5, -5])
		self.assertBlockOutput('result4', [2, 3])
		self.assertBlockOutput('result5', ["data", "data"])

		self.assertThat("output == expected",
						expected=[{'value1': 'value', 'value2': 'value'}, {'value1': 'value', 'value2': 'value'}],
						output=[x['properties'] for x in self.allOutputFromBlock(self.modelId1) if x['outputId']=='result3'])
