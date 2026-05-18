"""
Test ConstantRateOutput - Multiple inputs in a single period.

Tests the case where:
- period = 2 seconds
- delayToEndOfPeriod = false (immediate output for first input)
- limitOnly = false (resend value every period)

Scenario with multiple inputs within the same period to verify rate limiting works correctly.

Expected behavior:
- First input (1.0) at t=0.1 outputs immediately
- Second input (2.0) at t=0.5 updates state, no output
- Third input (3.0) at t=1.9 updates state, no output
- Timer fires at t=2, outputs last value (3.0)
- Fourth input (4.0) at t=2.1 updates state, no output (different period)
- Timer fires at t=4, outputs last value (4.0)
- Timer fires at t=6, resends (4.0)
"""

__pysys_title__   = r""" ConstantRateOutput - Multiple inputs in single period. """
__pysys_purpose__ = r""" ConstantRateOutput - Multiple inputs in single period. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/generated-blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploy model with period=2s, delayToEndOfPeriod=false, limitOnly=false
		self.modelId = self.createTestModel(
			'apamax.analyticsbuilder.blocks.ConstantRateOutput',
			{'period': 2.0, 'delayToEndOfPeriod': False, 'limitOnly': False},
			inputs={'value': 'float'},
			outputs={'output': 'float'}
		)
		
		self.sendEventStrings(correlator,
			self.timestamp(0.1),
			self.inputEvent('value', 1.0, id=self.modelId),  # t=0.1: first input -> output immediately
			self.timestamp(0.5),
			self.inputEvent('value', 2.0, id=self.modelId),  # t=0.5: second input in same period -> no output
			self.timestamp(1.9),
			self.inputEvent('value', 3.0, id=self.modelId),  # t=1.9: third input in same period -> no output
			self.timestamp(2),                               # t=2: timer fires -> no output (already output on input)
			self.timestamp(2.1),
			self.inputEvent('value', 4.0, id=self.modelId),  # t=2.1: first input in new period -> output immediately
			self.timestamp(4),                               # t=4: timer fires -> no output (already output on input at 2.1)
			self.timestamp(6),                               # t=6: timer fires -> resend (4.0)
			self.timestamp(7)                                # final flush (before next timer at t=8)
		)

	def validate(self):
		# Verify model started successfully
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')
		
		# Expected outputs: 1.0 at t=0.1 (first input), 4.0 at t=2.1 (first input of period 2), 4.0 at t=6 (timer, no input)
		self.assertBlockOutput('output', [1.0, 4.0, 4.0])
