#
#  $Copyright (c) 2019 Software AG, Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA, and/or its subsidiaries and/or its affiliates and/or their licensors.$
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/',initialCorrelatorTime=1582902000)
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploying a new model with correct parameter.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.RootMeanSquare', {'setSize':3})
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1582902000),
		                      self.inputEvent('value', 5.0, id = self.modelId),
		                      self.timestamp(1582903000),
		                      self.inputEvent('value', 8, id = self.modelId),
		                      self.timestamp(1582903010),
		                      self.inputEvent('value', 10.5, id = self.modelId),
		                      self.timestamp(1582903910),
		                      self.inputEvent('value', 12, id = self.modelId),
		                      self.timestamp(1582904000),
		                      self.inputEvent('value', 2.2, id = self.modelId),
		                      self.timestamp(1582904500),
		                      )

	def validate(self):

		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		self.assertGrep('output.evt', expr=self.outputExpr('rootMeanSquareOutput',5))
		self.assertGrep('output.evt', expr=self.outputExpr('rootMeanSquareOutput',6.670832032063167))
		self.assertGrep('output.evt', expr=self.outputExpr('rootMeanSquareOutput',8.149642118931768))
		self.assertGrep('output.evt', expr=self.outputExpr('rootMeanSquareOutput',10.29967637032025))
		self.assertGrep('output.evt', expr=self.outputExpr('rootMeanSquareOutput',9.29318746896528))
