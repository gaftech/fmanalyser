from fmanalyser.conf import options
from fmanalyser.device.controllers.base import DeviceController
from fmanalyser.device.drivers.rtl2832 import Rtl2832
from matplotlib import mlab
import numpy

class Rtl2832Controller(DeviceController):
    
    device_class = Rtl2832

    fft_size = options.IntOption(default=1024)
    sample_count = options.IntOption(default=2**18)

    def _probe_fft(self, worker):
        span = worker.device.get_sample_rate()
        samples = worker.device.read_samples(self.sample_count)
        levels, freqs = mlab.psd(samples,
            NFFT = self.fft_size,
            Fs = span*1000,
            scale_by_freq = False
        )
        return freqs/1e3, (10*numpy.log10(levels),)