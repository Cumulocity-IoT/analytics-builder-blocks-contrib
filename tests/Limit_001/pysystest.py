__pysys_title__   = r""" Limit block - both limits, value within range. """
#                        =========================================================================
__pysys_purpose__ = r""" Limit block - both limits, value within range. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
    def execute(self):
        correlator = self.startAnalyticsBuilderCorrelator(
            blockSourceDir=f'{self.project.SOURCE}/blocks')

        # engine_receive process listening on all the channels.
        correlator.receive('all.evt')

        # Deploy the model with both limits.
        self.modelId = self.createTestModel(
            'apamax.analyticsbuilder.blocks.Limit',
            {'lower': 10.0, 'upper': 100.0},
            inputs={'value': 'float'},
            outputs={'output': 'float'},
        )

        self.sendEventStrings(correlator,
                              self.timestamp(0.1),  # Initial time setup
                              self.timestamp(1),
                              self.inputEvent('value', 50.0, id=self.modelId),
                              self.timestamp(2),  # final flush
                              )

    def validate(self):
        # Always verify the model started successfully.
        self.assertGrep(self.analyticsBuilderCorrelator.logfile,
                        expr='Model "' + self.modelId + '" with PRODUCTION mode has started')

        # Verify output: value within limits should pass through unchanged
        self.assertBlockOutput('output', [50.0])
