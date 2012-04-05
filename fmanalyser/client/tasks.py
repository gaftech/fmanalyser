# -*- coding: utf-8 -*-
from .worker import BaseTask
import time

class ReadChannelValues(BaseTask):
    
    def __init__(self, worker, channel):
        super(ReadChannelValues, self).__init__(worker)
        self.channel = channel
    
    def __str__(self):
        return 'Measurements : %s' % self.channel
    
    def run(self):
        self.channel.read(self.client)
            
    
class WriteChannelValue(BaseTask):
    
    def __init__(self, worker, variable):
        super(WriteChannelValue, self).__init__(worker)
        self.variable = variable
    
    def run(self):
        self.variable.write(self.client)

class TuneUpCommand(BaseTask):
    # TODO : Integrate this in channel variable (or alike stuff) to manage events
    def run(self):
        self.client.tune_up()
    
class TuneDownCommand(BaseTask):
    
    def run(self):
        self.client.tune_down()
    
    
    
    
    
    
    

