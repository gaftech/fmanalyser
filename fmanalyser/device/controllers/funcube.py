# -*- coding: utf-8 -*-
from fmanalyser.device.controllers.grcontroller import BaseGrController
from fmanalyser.conf import options
from fmanalyser.exceptions import DeviceNotFound

class FuncubeController(BaseGrController):
    
    samp_rate = options.IntOption(default=96000)
    port = options.IntOption(default=None,
        ini_help="Sound card number, as shown in /proc/asound/cards (0,1...). Leave unset to auto-detect")
    
    def make_top_block(self):
        from gnuradio import fcd
        from fmanalyser.device.drivers.grblock import TopBlock
        port = self.port
        if port is None:
            port = self._autodetect()
        source = fcd.source_c("hw:%s" % port)
        source.set_freq_corr(-120)
        return TopBlock(samp_rate=self.samp_rate, source=source)

    def _autodetect(self):
        #TODO: something cleaner / regex ?
        with open('/proc/asound/cards') as fp:
            for line in fp:
                if "FUNcube Dongle" not in line:
                    continue
                try:
                    return int(line.split()[0])
                except ValueError:
                    pass
        raise DeviceNotFound("Can't find any funcube")
    
    