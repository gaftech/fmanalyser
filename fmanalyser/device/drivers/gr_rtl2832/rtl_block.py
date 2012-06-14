# -*- coding: utf-8 -*-
from fmanalyser.device.drivers.grblock import BaseGrBlock


class RtlBlock(BaseGrBlock):
    
    _osmo = True
    
    def make_source(self):
        if self._osmo:
            return self._make_osmo_source()
        else:
            return self._make_rtl_source()
    
    def _make_rtl_source(self):
        try:
            import baz
        except ImportError:
            raise ImportError("Gnuradio baz must be installed. Otherwise, try osmosdr")
        source = baz.rtl_source_c(defer_creation=True)
        source.set_verbose(True)
        source.set_vid(0x0)
        source.set_pid(0x0)
        source.set_tuner_name("")
        source.set_default_timeout(0)
        source.set_use_buffer(True)
        source.set_fir_coefficients(([]))

        if source.create() == False:
            raise RuntimeError("Failed to create RTL2832 Source: source")
        
        source.set_sample_rate(self.samp_rate)
#        self.source.set_frequency(freq)
        source.set_auto_gain_mode(False)
        source.set_relative_gain(True)
        source.set_gain(0)
        
        return source
    
    def _make_osmo_source(self):
        try:
            import osmosdr
        except ImportError:
            raise ImportError("Gnuradio osmo-sdr must be installed. Otherwise, try gr-baz")
        import osmosdr
        source = osmosdr.source_c( args="nchan=" + str(1) + " " + ""  )
        source.set_sample_rate(self.samp_rate)
#        self.osmosdr_source_c_0.set_center_freq(freq, 0)
        source.set_freq_corr(0, 0)
        source.set_gain_mode(0, 0)
        g = source.set_gain(0, 0)
        
        print "gain: %s" % g
        
        return source
    
    def set_freq(self, hz):
        if self._osmo:
            self.source.set_center_freq(hz,0)
        else:
            self.source.set_frequency(hz)
        
        
        