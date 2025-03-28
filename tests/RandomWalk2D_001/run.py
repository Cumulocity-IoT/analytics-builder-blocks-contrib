#
#  $Copyright (c) 2019 Software AG, Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA, and/or its subsidiaries and/or its affiliates and/or their licensors.$
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def test_range(value,min,max):
		if value in range(min,max):
			return True
		else :
			return False
	
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/simulation-blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploying a new model with correct parameter.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.RandomWalk2D', {'startingXPosition':5, 'startingYPosition':0})
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1),
		                      self.inputEvent('trigger', True, id = self.modelId),
		                      self.timestamp(2),
		                      self.inputEvent('trigger', True, id = self.modelId),
							  self.timestamp(3),
							  self.inputEvent('trigger', True, id = self.modelId),
		                      self.timestamp(4),
		                      self.inputEvent('trigger', True, id = self.modelId),
							  self.timestamp(5),
							  self.inputEvent('trigger', True, id = self.modelId),
		                      self.timestamp(6),
		                      self.inputEvent('trigger', True, id = self.modelId),
							  self.timestamp(7),
							  self.inputEvent('trigger', True, id = self.modelId),
		                      self.timestamp(8),
		                      self.inputEvent('trigger', True, id = self.modelId),
							  self.timestamp(20)
							  )

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		self.assertEval('4 <= {currentPosition} <= 6', currentPosition=float(self.getExprFromFile('output.evt', '"currentXPosition","model_0",".*",1,any[(]float,(.*)[)],')))
		self.assertEval('-1 <= {currentPosition} <= 1', currentPosition=float(self.getExprFromFile('output.evt', '"currentYPosition","model_0",".*",1,any[(]float,(.*)[)],')))
		self.assertEval('3 <= {currentPosition} <= 7', currentPosition=float(self.getExprFromFile('output.evt', '"currentXPosition","model_0",".*",2,any[(]float,(.*)[)],')))
		self.assertEval('-2 <= {currentPosition} <= 2', currentPosition=float(self.getExprFromFile('output.evt', '"currentYPosition","model_0",".*",2,any[(]float,(.*)[)],')))
		self.assertEval('2 <= {currentPosition} <= 8', currentPosition=float(self.getExprFromFile('output.evt', '"currentXPosition","model_0",".*",3,any[(]float,(.*)[)],')))
		self.assertEval('-3 <= {currentPosition} <= 3', currentPosition=float(self.getExprFromFile('output.evt', '"currentYPosition","model_0",".*",3,any[(]float,(.*)[)],')))
		