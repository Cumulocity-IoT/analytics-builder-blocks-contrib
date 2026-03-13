__pysys_title__   = r""" CSVReader block - touch test. """
#                        ================================================================================
__pysys_purpose__ = r""" CSVReader block - touch test. """

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# Deploying a new model with correct parameter.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.custom.CSVReader',{'fragmentName':'infile','isHeaderProvided':'false'})
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1),
		                      self.inputEvent('csv', 'field1,field2,field3\n11,12,13\n21,22,23\n31,32,33', id = self.modelId),
		                      self.timestamp(2)
							  )

	def validate(self):
		# Verifying that the model is deployed successfully.
		self.assertGrep(self.analyticsBuilderCorrelator.logfile, expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')
		self.assertBlockOutput("jsonOutput",['{"infile":[{"col1":any(string,"field1"),"col2":any(string,"field2"),"col3":any(string,"field3")},{"col1":any(float,11),"col2":any(float,12),"col3":any(float,13)},{"col1":any(float,21),"col2":any(float,22),"col3":any(float,23)},{"col1":any(float,31),"col2":any(float,32),"col3":any(float,33)}]}'])
