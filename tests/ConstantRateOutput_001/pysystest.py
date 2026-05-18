"""
Test ConstantRateOutput - Basic rate limiting with immediate output.

Tests the case where:
- period = 2 seconds
- delayToEndOfPeriod = false (immediate output for first input)
- limitOnly = false (resend value every period)

Expected behavior:
- First input at t=0 outputs immediately
- Subsequent input in same period (t=0.5, t=1.5) updates state but no output
- Timer fires at t=2, outputs last received value
- Timer fires at t=4, resends last value (no new input in period)
"""

__pysys_title__   = r""" ConstantRateOutput - Basic rate limiting (immediate, not limitOnly). """
__pysys_purpose__ = r""" ConstantRateOutput - Basic rate limiting (immediate, not limitOnly). """

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
			self.timestamp(0),
			self.inputEvent('value', 1.0, id=self.modelId),  # t=0: first input -> output immediately
			self.timestamp(0.5),
			self.inputEvent('value', 2.0, id=self.modelId),  # t=0.5: second input in same period -> no output
			self.timestamp(1.5),
			self.inputEvent('value', 3.0, id=self.modelId),  # t=1.5: third input in same period -> no output
			self.timestamp(2),                               # t=2: timer fires -> no output (already output on input)
			self.timestamp(4),                               # t=4: timer fires -> output last value (3.0)
			self.timestamp(5)                                # final flush (before next timer at t=6)
		)

	def validate(self):
		# Verify model started successfully
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')
		
		# Expected outputs: 1.0 at t=0 (first input output immediate),
		# 3.0 at t=2 (timer, outputs last queued input),
		# 3.0 at t=4 (timer, resends because no new input in period)
		self.assertBlockOutput('output', [1.0, 3.0, 3.0])
