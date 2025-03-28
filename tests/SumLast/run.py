#
#  $Copyright (c) 2019 Software AG, Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA, and/or its subsidiaries and/or its affiliates and/or their licensors.$
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#
from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/cumulocity-blocks/')
		modelId = self.createTestModel('apamax.analyticsbuilder.customblocks.SumLast')
		self.sendEventStrings(
			correlator,
			self.timestamp(1),
			self.inputEvent('value', 5.0,  id = modelId),
			self.timestamp(2),
			self.inputEvent('value', 10.0, id = modelId),
			self.timestamp(3),
			self.inputEvent('value', -10.0, id = modelId),
			self.timestamp(4),
			self.inputEvent('value', -10.0, id = modelId),
			self.inputEvent('reset', True, id = modelId),
			self.timestamp(5),
			)
	def validate(self):

		# Verifying the result - output from the block.

		self.assertGrep('output.evt', expr=self.outputExpr('sum', 5))
		self.assertGrep('output.evt', expr=self.outputExpr('lastValue', 0))
		self.assertGrep('output.evt', expr=self.outputExpr('sum', 15))
		self.assertGrep('output.evt', expr=self.outputExpr('lastValue', 5))
		self.assertGrep('output.evt', expr=self.outputExpr('sum', 5))
		self.assertGrep('output.evt', expr=self.outputExpr('lastValue', 10))
		self.assertGrep('output.evt', expr=self.outputExpr('sum', 0))
		self.assertGrep('output.evt', expr=self.outputExpr('lastValue', 5))

