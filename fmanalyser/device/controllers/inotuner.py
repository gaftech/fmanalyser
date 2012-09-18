# -*- coding: utf-8 -*-
from fmanalyser.device.controllers.base import DeviceController
from fmanalyser.device.drivers.inotuner import ArduinoTuner

class ArduinoTunerController(DeviceController):
    
    device_class = ArduinoTuner
    
    def _probe_scan_level(self, worker):
        return worker.device.get_rf()