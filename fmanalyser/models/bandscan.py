# -*- coding: utf-8 -*-

from fmanalyser.client.tasks import BaseTask
from fmanalyser.exceptions import BadOptionValue
from fmanalyser.models.signals import scan_updated
from fmanalyser.utils import freqlist
from fmanalyser.utils.conf import options, OptionHolder
from fmanalyser.utils.datastructures.ordereddict import OrderedDict
import threading
import time
import os
from fmanalyser.utils.log import Loggable

class UpdateTask(BaseTask):
    
    def __init__(self, scan):
        super(UpdateTask, self).__init__()
        self.scan = scan

    def run(self, worker):
        
        worker.client.set_measuring_mode()

        f = self.scan.get_current_frequency()
        stop = self.scan.stop
        if self.scan.partial:
            stop = min(f + self.scan.step * (self.scan.partial - 1), stop)
        
        while not self._stop.is_set() and f <= stop:
            worker.client.set_frequency(f)
            self.sleep(self.scan.acq_delay)
            l = worker.client.get_rf()
            self.scan.update(f,l)
            f += self.scan.step

class Bandscan(Loggable, OptionHolder):
    
    config_section_name = 'scan'
    
    start = options.CarrierFrequencyOption(default=87500)
    stop = options.CarrierFrequencyOption(default=108000)
    step = options.IntOption(default=100)
    partial = options.IntOption(default=10)
    acq_delay = options.FloatOption(default=3)
    ref_file = options.DataFileOption(default='scan.ref')
    
    def __init__(self, **kwargs):
        
        super(Bandscan, self).__init__(**kwargs)
        
        if self.start >= self.stop:
            raise BadOptionValue("start option (%s) must be lower than stop option (%s)" % (self.start, self.stop))
        self._lock = threading.Lock()
        self.reset()
        

    def reset(self):
        self._data = OrderedDict()
    
    def items(self):
        return self._data.items()
       
    def is_complete(self):
        return self.get_current_frequency() >= self.stop
    
    def get_current_frequency(self):
        if self._data:
            return max(self._data.keys())
        else:
            return self.start
    
    def enqueue_update(self, worker):
        return worker.enqueue_task(UpdateTask(self))

    def update(self, f, l):
        with self._lock:
            self._data[f] = l
            scan_updated.send(self, f, l)

    def save_ref(self):
        assert self.is_complete()
        with open(self.ref_file, 'w') as fp:
            self.dump(fp)
        self.logger.info('scanning reference file saved: %s' % self.ref_file)

    def dump(self, fileobj):
        for f, l in self._data.items():
            fileobj.write('%s %s\n' % (f, l))

 
        