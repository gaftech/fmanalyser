# -*- coding: utf-8 -*-
from fmanalyser.device.controllers.base import BaseDeviceController
from fmanalyser.conf import options
import numpy as np
from fmanalyser.device.drivers.grdevice import GrDevice

class BaseGrController(BaseDeviceController):

    samp_rate = options.IntOption(required=True)    
    scan_samples = options.IntOption(default=10,
        ini_help="Number of signal strength or fft acquirement per frequency while scanning")
    
    def make_device(self):
        tb = self.make_top_block()
        return GrDevice(tb)
    
    def make_top_block(self):
        raise NotImplementedError()
    
    def _probe_scan_level(self, worker):
        tb = worker.device.block
        
        levels = []
        while True:
            l = tb.power_probe.level()
            levels.append(l)
            if len(levels) < self.scan_samples:
                worker.short_sleep()
            else:
                break
        return max(levels)

    def _probe_fft(self, worker):
        tb = worker.device.block
        q = tb.msg_q
        
        q.flush()
        
        level_arrays = []
        for i in range(self.scan_samples):
            
            # ..see:: gr-wxgui.fftsink_nongl
            msg = q.delete_head()
            itemsize = int(msg.arg1())
            nitems = int(msg.arg2())
            s = msg.to_string()
            
            # There may be more than one FFT frame in the message.
            # If so, we take only the last one
            if nitems > 1:
                start = itemsize * (nitems - 1)
                s = s[start:start+itemsize]
    
            levs = np.fromstring (s, np.float32)
        
            # FFT shift
            nlevs = len(levs)
            levs = np.concatenate((levs[nlevs/2:], levs[:nlevs/2]))
        
            level_arrays.append(levs)
        
        # Freq values
        span = tb.samp_rate / 1000
        freqs = np.linspace(-span/2, span/2, len(levs))
        
        return freqs, level_arrays
    
    
    