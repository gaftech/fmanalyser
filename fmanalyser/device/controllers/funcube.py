# -*- coding: utf-8 -*-
from fmanalyser.device.controllers.base import DeviceController
from fmanalyser.conf import options
from fmanalyser.device.drivers.funcube import Funcube

class FuncubeController(DeviceController):
    
    device_class = Funcube
    
    scan_samples = options.IntOption(default=10,
        ini_help="Number of signal strength measurement to perform per frequency while scanning")
    scan_sample_delay = options.FloatOption(default=0.1,
        ini_help="Delay (s) between two samples")
    
    def _probe_scan_level(self, worker):
        levels = []
        while True:
            l = worker.device.get_signal_power()
            levels.append(l)
            if len(levels) < self.scan_samples:
                worker.sleep(self.scan_sample_delay)
            else:
                break
        return max(levels)
        
    
    
    