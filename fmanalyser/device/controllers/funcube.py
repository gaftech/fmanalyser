# -*- coding: utf-8 -*-
from fmanalyser.device.controllers.grcontroller import BaseGrController
from fmanalyser.conf import options
from fmanalyser.exceptions import DeviceNotFound

class FuncubeController(BaseGrController):
    
    samp_rate = options.IntOption(default=96000)
    port = options.IntOption(default=None,
        ini_help="Sound card number, as shown in /proc/asound/cards (0,1...). Leave unset to auto-detect")
    
    def get_source_block(self):
        from gnuradio import fcd
        port = self.port
        if port is None:
            port = self._autodetect()
            self.logger.debug("Fcd soundcard found at hw:%s" % port)
        source = fcd.source_c("hw:%s" % port)
        source.set_freq_corr(-120)
        return source

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
    
    