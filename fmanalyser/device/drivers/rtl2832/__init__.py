from fmanalyser.conf import options
from fmanalyser.device.drivers.base import Device
import rtlsdr

class Rtl2832(Device):
    
    sample_rate = options.IntOption(default=3100000)
    gain = options.IntOption(default=0)
    auto_gain = options.BooleanOption(default=False)
    
    def __init__(self, *args, **kwargs):
        super(Rtl2832, self).__init__(*args, **kwargs)
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            self._open()
        return self._client
    
    def _open(self):
        self._client = sdr = rtlsdr.RtlSdr()
        sdr.sample_rate = self.sample_rate
        sdr.set_manual_gain_enabled(self.auto_gain)
        if not self.auto_gain:
            sdr.set_gain(self.gain)

    def close(self):
        if self._client is not None:
            self._client.close()
            self._client = None

    def tune(self, f):
        self.tune_hz(f*1000)
        
    def tune_hz(self, f):
        self.logger.debug('tune: %s MHz' % (f/1e6,))
        self.client.set_center_freq(f)
    
    def get_sample_rate(self):
        return self.client.get_sample_rate()/1000
      
    def set_sample_rate(self, khz):
        self.client.set_sample_rate(khz*1000)
        
    def read_samples(self, count):
        return self.client.read_samples(count)
        