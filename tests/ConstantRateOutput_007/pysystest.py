"""
Test ConstantRateOutput - 10 second period, rate limit verification.

Tests the case where:
- period = 10 seconds
- delayToEndOfPeriod = false (immediate output for first input)
- limitOnly = false (resend value every period)

Scenario verifies that rate limiting works correctly: outputs occur at timer
boundaries, not immediately on subsequent inputs within a period.

Expected behavior:
- First input (1.0) at t=3 outputs immediately
- Second input (2.0) at t=7 (within same period) has no output
- Timer fires at t=13 (3 + 10s period), outputs last value in period (2.0)
- Third input (4.0) at t=16 (within period starting at t=13) has no output
- Timer fires at t=23 (13 + 10s period), outputs last value in period (4.0)
- Timer fires at t=33 (23 + 10s period), resends last value (4.0)
"""

__pysys_title__   = r""" ConstantRateOutput - 10s period rate limiting. """
__pysys_purpose__ = r""" ConstantRateOutput - 10s period rate limiting. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/generated-blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploy model with period=10s, delayToEndOfPeriod=false, limitOnly=false
		self.modelId = self.createTestModel(
			'apamax.analyticsbuilder.blocks.ConstantRateOutput',
			{'period': 10.0, 'delayToEndOfPeriod': False, 'limitOnly': False},
			inputs={'value': 'float'},
			outputs={'output': 'float'}
		)
		
		self.sendEventStrings(correlator,
			self.timestamp(3),
			self.inputEvent('value', 1.0, id=self.modelId),   # t=3: first input -> output immediately
			self.timestamp(7),
			self.inputEvent('value', 2.0, id=self.modelId),   # t=7: second input in same period -> no output
			self.timestamp(10),                                # t=10: no timer trigger, no output
			self.timestamp(13),                                # t=13: timer fires (period started at t=3) -> output 2.0
			self.timestamp(16),                                # t=16: new input, no output (within period)
			self.inputEvent('value', 4.0, id=self.modelId),   # t=16: new input -> output 4.0 immediately
			self.timestamp(23),                                # t=23: timer fires (13+10) -> no output (already output in period)
			self.timestamp(33),                                # t=33: timer fires (23+10) -> resend 4.0
			self.timestamp(34)                                 # final flush
		)

	def validate(self):
		# Verify model started successfully
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')
		
		# Expected outputs: 1.0 at t=3, 2.0 at t=13, 4.0 at t=16, 4.0 at t=33
		self.assertBlockOutput('output', [1.0, 2.0, 4.0, 4.0])
		
		# Verify outputs occur at the correct timestamps
		self.assertGrep('output.evt', expr=self.outputExpr('output', 1.0, time=3))
		self.assertGrep('output.evt', expr=self.outputExpr('output', 2.0, time=13))
		self.assertGrep('output.evt', expr=self.outputExpr('output', 4.0, time=16))
		self.assertGrep('output.evt', expr=self.outputExpr('output', 4.0, time=33))
