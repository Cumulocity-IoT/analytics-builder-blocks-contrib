__pysys_title__   = r""" CountBy block - count then reset. """
#                        =========================================================================
__pysys_purpose__ = r""" CountBy block - count then reset. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
    def execute(self):
        correlator = self.startAnalyticsBuilderCorrelator(
            blockSourceDir=f'{self.project.SOURCE}/generated-blocks/')

        # engine_receive process listening on all the channels.
        correlator.receive('all.evt')

        # Deploy the model.
        self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.CountBy', inputs={'input':'pulse', 'reset':'pulse'}, outputs={'count':'pulse'})

        self.sendEventStrings(correlator,
                              self.timestamp(0.1),  # Initial time setup
                              self.timestamp(1),
                              self.inputEvent('input', True, id=self.modelId),
                              self.timestamp(2),
                              self.inputEvent('input', True, id=self.modelId),
                              self.timestamp(3),
                              self.inputEvent('input', True, id=self.modelId),
                              self.timestamp(4),
                              self.inputEvent('reset', True, id=self.modelId),
                              self.timestamp(5),  # final flush  
                              )

    def validate(self):
        # Always verify the model started successfully.
        self.assertGrep(self.analyticsBuilderCorrelator.logfile,
                        expr='Model "' + self.modelId + '" with PRODUCTION mode has started')

        # Verify output: 3 counts followed by reset should output 3.0
        self.assertBlockOutput('count', [3.0])
