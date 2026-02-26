#
#  Copyright (c) 2019-present Cumulocity GmbH, Duesseldorf, Germany and/or its affiliates and/or their licensors.
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

__pysys_title__ = r'Python block: check pandas under restrictedpython'
__pysys_purpose__ = r''

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def execute(self):
		self.correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/python-blocks/', arguments=["--config", f"{self.project.SOURCE}/python-blocks/PythonFunction/", "-Dstreaminganalytics.pythonBlockRequirements=pandas\nstatsmodels\nscipy", "-Dstreaminganalytics.pythonBlockPackages=pandas numpy", "-Dstreaminganalytics.pythonBlockIsolation=none", '-v', 'plugins.PythonBlockPlugin=DEBUG'])

		self.modelId1 = self.createTestModel('apamax.analyticsbuilder.blocks.PythonFunction', {
			'label': 'Pandas Test Model',
			'param1': 'data',
			'pythonFunction':"""import pandas as pd\nimport numpy as np

def onInput(inputs, context):
    
    if inputs[0].value != None:
        queue = context.getState('queue',{})
        queue[inputs[0].timestamp] = inputs[0].value
        context.setState('queue', queue)


    if(inputs[1].value):
        queue = context.getState('queue', {})
        s = dict(sorted(queue.items()))
        s = { round(k,3):s[k] for k in s }
        signal_ts = pd.DataFrame(data=s.values(), index=s.keys(), columns=['value'])
        signal_ts.index = np.array(list(map(lambda x: int(x*1000), sorted(s.keys()))), dtype='datetime64[ms]')
        context.setState('queue', {})
        signal_ts.index = signal_ts.index.astype(str)
        return [Value(True,{'series': signal_ts.to_dict()})]"""
		})
		
		self.sendEventStrings(self.correlator,
								self.timestamp(1),
								self.inputEvent('value1', 12.25, id = self.modelId1),
								self.timestamp(2),
								self.inputEvent('value2', True, id = self.modelId1),
								self.timestamp(3),
							  )


	def validate(self):
		# Verifying that there are no errors in log file.
		self.checkLogs(warnIgnores=['Python path element does not exist'])
		
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId1 + '\" with PRODUCTION mode has started')
		
		# Verifying the result - output from the block.
		self.assertBlockOutput('result1', [True])

		self.assertThat("output == expected",
						expected=[{'series': {'value': {'1970-01-01 00:00:01': 12.25}}}],
						output=[x['properties'] for x in self.allOutputFromBlock(self.modelId1) if x['outputId']=='result1'])
