from fmanalyser.device.controllers.grcontroller import BaseGrController
from fmanalyser.conf import options

class GrRtl2832Controller(BaseGrController):
    
    samp_rate = options.IntOption(default=3200000)
    
    def make_top_block(self):
        from fmanalyser.device.drivers.gr_rtl2832.rtl_block import RtlBlock
        b = RtlBlock(samp_rate=self.samp_rate)
        return b


