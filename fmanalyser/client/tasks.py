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
    
    def __init__(self, worker, value):
        super(WriteChannelValue, self).__init__(worker)
        self.value = value
    
    def run(self):
        self.value.write(self.client)



