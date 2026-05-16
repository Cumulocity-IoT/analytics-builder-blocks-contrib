__pysys_title__   = r""" Limit block - both limits, value above upper. """
#                        =========================================================================
__pysys_purpose__ = r""" Limit block - both limits, value above upper. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
    def execute(self):
        correlator = self.startAnalyticsBuilderCorrelator(
            blockSourceDir=f'{self.project.SOURCE}/generated-blocks/')

        # engine_receive process listening on all the channels.
        correlator.receive('all.evt')

        # Deploy the model with both limits.
        self.modelId = self.createTestModel(
            'apamax.analyticsbuilder.custom.Limit',
            {'lowerLimit': 10.0, 'upperLimit': 100.0},
            inputs={'value': 'float'},
            outputs={'limited': 'float'},
        )

        self.sendEventStrings(correlator,
                              self.timestamp(0.1),  # Initial time setup
                              self.timestamp(1),
                              self.inputEvent('value', 150.0, id=self.modelId),
                              self.timestamp(2),  # final flush
                              )

    def validate(self):
        # Always verify the model started successfully.
        self.assertGrep(self.analyticsBuilderCorrelator.logfile,
                        expr='Model "' + self.modelId + '" with PRODUCTION mode has started')

        # Verify output: value above upper limit should be clamped to upper limit
        self.assertBlockOutput('limited', [100.0])
