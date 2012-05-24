from fmanalyser.device.controllers.base import GrDeviceController
from fmanalyser.device.drivers.gr_rtl2832 import GrRtl2832

class GrRtl2832Controller(GrDeviceController):
    
    device_class = GrRtl2832
    


