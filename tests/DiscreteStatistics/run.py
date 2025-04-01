#
#  $Copyright (c) 2019 Software AG, Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA, and/or its subsidiaries and/or its affiliates and/or their licensors.$
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest


class PySysTest(AnalyticsBuilderBaseTest):
    def execute(self):
        correlator = self.startAnalyticsBuilderCorrelator(
            blockSourceDir=f'{self.project.SOURCE}/blocks/')
        modelId = self.createTestModel('apamax.analyticsbuilder.blocks.DiscreteStatistics', inputs={'value':'float', 'sample':'pulse', 'reset':'pulse'})
        self.sendEventStrings(correlator,
                              self.timestamp(1),
                              self.inputEvent('value', 100, id=modelId),
                              self.inputEvent('sample', 'true', id=modelId, eplType = 'boolean'),
                              self.timestamp(2),
                              self.inputEvent('value', 110, id=modelId),
                              self.inputEvent('sample', 'true', id=modelId, eplType = 'boolean'),
                              self.timestamp(3),
                              self.inputEvent('value', 120, id=modelId),
                              self.inputEvent('sample', 'true', id=modelId, eplType = 'boolean'),
                              self.timestamp(4),
                              self.inputEvent('value', 30, id=modelId),
                              self.inputEvent('sample', 'true', id=modelId, eplType = 'boolean'),
                              self.inputEvent('reset', 'true', id=modelId, eplType = 'boolean'),  # reset and sample at same time : sum = mean = value
                              self.timestamp(5),
                              self.inputEvent('reset', 'true', id=modelId, eplType = 'boolean'),  # reset on its own : sum = count = 0 (mean and std dev are NaN!)
                              self.timestamp(6),
                              )

    def validate(self):
        self.assertGrep('output.evt', expr=self.outputExpr('sum', 100, time=1))
        self.assertGrep('output.evt', expr=self.outputExpr('count', 1, time=1))
        self.assertGrep('output.evt', expr=self.outputExpr('sum', 100, time=1))
        self.assertGrep('output.evt', expr=self.outputExpr('sum', 210, time=2))
        self.assertGrep('output.evt', expr=self.outputExpr('sum', 330, time=3))
        self.assertGrep('output.evt', expr=self.outputExpr('min', 100, time=3))
        self.assertGrep('output.evt', expr=self.outputExpr('max', time=3))
        self.assertGrep('output.evt', expr=self.outputExpr('mean', 110, time=3))
        self.assertGrep('output.evt', expr=self.outputExpr('standardDeviation', 8.164965809277223, time=3))
        self.assertGrep('output.evt', expr=self.outputExpr('sum', 30, time=3.9999999999999996))
        self.assertGrep('output.evt', expr=self.outputExpr('count', 1, time=3.9999999999999996))
        self.assertGrep('output.evt', expr=self.outputExpr('mean', 30, time=3.9999999999999996))
        self.assertGrep('output.evt', expr=self.outputExpr('standardDeviation', 0, time=3.9999999999999996))

        self.assertGrep('output.evt', expr=self.outputExpr('sum', 0, time=5))
