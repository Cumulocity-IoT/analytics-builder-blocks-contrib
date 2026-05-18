"""
Test ConstantRateOutput - Delayed and limit only mode.

Tests the case where:
- period = 1 second
- delayToEndOfPeriod = true (delay until end of period)
- limitOnly = true (no resend on idle)

Expected behavior:
- First input at t=0 is queued, no output
- Timer fires at t=1, outputs queued value (1.0)
- No input from t=1 to t=1.5
- Timer fires at t=2, NO output (limitOnly=true, no input in period)
- Second input at t=1.5 (time travel back - actually t=2.5) is queued
- Timer fires at t=3, outputs queued value (2.0)
"""

__pysys_title__   = r""" ConstantRateOutput - Delayed and limit only mode. """
__pysys_purpose__ = r""" ConstantRateOutput - Delayed and limit only mode. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/generated-blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploy model with period=1s, delayToEndOfPeriod=true, limitOnly=true
		self.modelId = self.createTestModel(
			'apamax.analyticsbuilder.blocks.ConstantRateOutput',
			{'period': 1.0, 'delayToEndOfPeriod': True, 'limitOnly': True},
			inputs={'value': 'float'},
			outputs={'output': 'float'}
		)
		
		self.sendEventStrings(correlator,
			self.timestamp(0),
			self.inputEvent('value', 1.0, id=self.modelId),  # t=0: first input -> queued, no output
			self.timestamp(1),                               # t=1: timer fires -> output queued value (1.0)
			self.timestamp(2),                               # t=2: timer fires -> NO output (limitOnly=true, no input)
			self.timestamp(2.5),
			self.inputEvent('value', 2.0, id=self.modelId),  # t=2.5: input -> queued
			self.timestamp(3),                               # t=3: timer fires -> output queued value (2.0)
			self.timestamp(4)                                # final flush
		)

	def validate(self):
		# Verify model started successfully
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')
		
		# Expected outputs: 1.0 at t=1, 2.0 at t=3 (no output at t=2)
		self.assertBlockOutput('output', [1.0, 2.0])
