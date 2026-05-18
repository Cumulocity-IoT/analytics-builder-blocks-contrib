"""
Test ConstantRateOutput - Limit only mode.

Tests the case where:
- period = 1 second
- delayToEndOfPeriod = false (immediate output for first input)
- limitOnly = true (no resend on idle)

Expected behavior:
- First input at t=0 outputs immediately
- Second input at t=0.5 updates state but no output (already output in this period)
- Timer fires at t=1, outputs last value (input was received in this period)
- No input in period from t=1 to t=2
- Timer fires at t=2, NO output (limitOnly=true and no input in this period)
"""

__pysys_title__   = r""" ConstantRateOutput - Limit only mode (no resend). """
__pysys_purpose__ = r""" ConstantRateOutput - Limit only mode (no resend). """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/generated-blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploy model with period=1s, delayToEndOfPeriod=false, limitOnly=true
		self.modelId = self.createTestModel(
			'apamax.analyticsbuilder.blocks.ConstantRateOutput',
			{'period': 1.0, 'delayToEndOfPeriod': False, 'limitOnly': True},
			inputs={'value': 'float'},
			outputs={'output': 'float'}
		)
		
		self.sendEventStrings(correlator,
			self.timestamp(0),
			self.inputEvent('value', 1.0, id=self.modelId),  # t=0: first input -> output immediately
			self.timestamp(0.5),
			self.inputEvent('value', 2.0, id=self.modelId),  # t=0.5: second input -> no output (already output in period)
			self.timestamp(1),                               # t=1: timer fires -> output (input existed in this period)
			self.timestamp(2),                               # t=2: timer fires -> NO output (limitOnly=true, no input)
			self.timestamp(3)                                # final flush
		)

	def validate(self):
		# Verify model started successfully
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')
		
		# Expected outputs: 1.0 at t=0, 2.0 at t=1 (no output at t=2)
		self.assertBlockOutput('output', [1.0, 2.0])
