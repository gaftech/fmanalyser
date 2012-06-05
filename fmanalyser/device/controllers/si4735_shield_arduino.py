# -*- coding: utf-8 -*-
from fmanalyser.device.controllers.base import DeviceController
from fmanalyser.device.drivers.si4735_shield_arduino import Si4735ArduinoShield

class Si4735ArduinoShieldController(DeviceController):
    device_class = Si4735ArduinoShield
    
    def _probe_scan_level(self, worker):
        return worker.device.get_rf()