# -*- coding: utf-8 -*-

from gnuradio import fcd
from fmanalyser.device.drivers.grblock import BaseGrBlock

class FcdBlock(BaseGrBlock):
    
    def make_source(self):
        source = fcd.source_c("hw:1")
        source.set_freq_corr(-120)
        return source
