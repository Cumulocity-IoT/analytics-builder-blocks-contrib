"""
Test ConstantRateOutput - Delayed output mode.

Tests the case where:
- period = 1 second
- delayToEndOfPeriod = true (delay output until end of period)
- limitOnly = false (resend value every period)

Expected behavior:
- First input at t=0 is queued, no immediate output
- Second input at t=0.5 updates queue
- Timer fires at t=1, outputs last queued value (2.0)
- Third input at t=1.2 is queued
- Timer fires at t=2, outputs queued value (3.0)
- Timer fires at t=3, no new input but limitOnly=false, so resend (3.0)
"""

__pysys_title__   = r""" ConstantRateOutput - Delayed output (delayToEndOfPeriod). """
__pysys_purpose__ = r""" ConstantRateOutput - Delayed output (delayToEndOfPeriod). """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/generated-blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploy model with period=1s, delayToEndOfPeriod=true, limitOnly=false
		self.modelId = self.createTestModel(
			'apamax.analyticsbuilder.blocks.ConstantRateOutput',
			{'period': 1.0, 'delayToEndOfPeriod': True, 'limitOnly': False},
			inputs={'value': 'float'},
			outputs={'output': 'float'}
		)
		
		self.sendEventStrings(correlator,
			self.timestamp(0),
			self.inputEvent('value', 1.0, id=self.modelId),  # t=0: first input -> queued, no output
			self.timestamp(0.5),
			self.inputEvent('value', 2.0, id=self.modelId),  # t=0.5: second input -> update queue
			self.timestamp(1),                               # t=1: timer fires -> output queued value (2.0)
			self.inputEvent('value', 3.0, id=self.modelId),  # t=1: third input (same timestamp as timer) -> queue it
			self.timestamp(2),                               # t=2: timer fires -> output queued value (3.0)
			self.timestamp(3),                               # t=3: timer fires -> no input in period, resend last (3.0)
			self.timestamp(4)                                # final flush
		)

	def validate(self):
		# Verify model started successfully
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')
		
		# Expected outputs: 2.0 at t=1, 3.0 at t=2, 3.0 at t=3
		self.assertBlockOutput('output', [2.0, 3.0, 3.0])
