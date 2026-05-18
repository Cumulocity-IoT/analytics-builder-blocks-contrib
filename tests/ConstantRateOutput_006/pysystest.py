"""
Test ConstantRateOutput - No input received.

Tests the case where no input is ever received.

Expected behavior:
- Timer would fire, but with no input, no state exists
- No output should be produced
"""

__pysys_title__   = r""" ConstantRateOutput - No input received. """
__pysys_purpose__ = r""" ConstantRateOutput - No input received. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):

	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/generated-blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploy model with period=1s, delayToEndOfPeriod=false, limitOnly=false
		# Even with limitOnly=false, no output should occur if no input was ever received
		self.modelId = self.createTestModel(
			'apamax.analyticsbuilder.blocks.ConstantRateOutput',
			{'period': 1.0, 'delayToEndOfPeriod': False, 'limitOnly': False},
			inputs={'value': 'float'},
			outputs={'output': 'float'}
		)
		
		self.sendEventStrings(correlator,
			self.timestamp(1),  # Time passes but no input
			self.timestamp(2),  # More time passes
			self.timestamp(3)   # final flush
		)

	def validate(self):
		# Verify model started successfully
		self.assertGrep(self.analyticsBuilderCorrelator.logfile,
			expr='Model "' + self.modelId + '" with PRODUCTION mode has started')
		
		# Expected: no output at all
		self.assertBlockOutput('output', [])
