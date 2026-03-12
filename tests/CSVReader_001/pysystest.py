#
#  $Copyright (c) 2019 Software AG, Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA, and/or its subsidiaries and/or its affiliates and/or their licensors.$
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#
__pysys_title__   = r""" CSVReader block - touch test. """
#                        ================================================================================
__pysys_purpose__ = r""" CSVReader block - touch test. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploying a new model with correct parameter.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.CSVReader',{'fragmentName':'infile'})
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1),
		                      self.inputEvent('csv', 'field1,field2,field3\n11,12,13\n21,22,23\n31,32,33', id = self.modelId),
		                      self.timestamp(2)
							  )

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr=re.escape('jsonOutput = {"infile":[{"field1":any(float,11),"field2":any(float,12),"field3":any(float,13)},{"field1":any(float,21),"field2":any(float,22),"field3":any(float,23)},{"field1":any(float,31),"field2":any(float,32),"field3":any(float,33)}]}'))
		
