# -*- coding: utf-8 -*-
from fmanalyser.device.controllers.grcontroller import BaseGrController
from fmanalyser.conf import options

class FuncubeController(BaseGrController):
    
    samp_rate = options.IntOption(default=96000)
    
    def make_top_block(self):
        from fmanalyser.device.drivers.funcube.fcd_block import FcdBlock
        return FcdBlock(samp_rate=self.samp_rate)

    