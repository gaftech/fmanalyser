'''
Created on 18 mai 2012

@author: gabriel
'''
from matplotlib import mlab
import math
import numpy
import pylab
import rtlsdr
import time
import itertools


start = int(81e6)
stop = int(92e6)
step = 100000
samp_rate = 3100000
samp_count = 2**18
interlace = max
interlace_multipass = max
lock_time = 0.01

one_shot = False

fft_size=1024
fft_pad=None
fft_fscale = False

def main():
    sdr = rtlsdr.RtlSdr()
    sdr.set_sample_rate(samp_rate)
    sdr.set_manual_gain_enabled(True)
    sdr.set_gain(0)
    
    pylab.ion()
    pylab.figure()
    pylab.draw()
    
    bigdata = {}
    freq = start
    while freq <= stop:
        
        print 'cf = %s MHz' % (freq/1e6,)
        sdr.set_center_freq(freq)
        time.sleep(lock_time)

        samples = sdr.read_samples(samp_count)

        tmpdata = {}
        _levels, _freqs = mlab.psd(samples, NFFT=fft_size, Fs=sdr.sample_rate, pad_to=fft_pad, scale_by_freq=fft_fscale)
        for l, f in itertools.izip(_levels, _freqs):
            if abs(f) > step/2:
                continue
            l = 10*math.log10(l)
            tmpdata.setdefault(freq, []).append(l)
        
        for f, levels in tmpdata.items():
            bigdata.setdefault(f, []).append(levels)
        
        pylab.plot(_freqs+freq, 10*numpy.log10(_levels))
        pylab.draw()
        freq += step
        
        if one_shot:
            break
        
    flatdata = {}
    for f, all_levels in bigdata.items():
        l = []
        for levels in all_levels:
            l.append(interlace(levels))   # levels from same pass
        flatdata[f] = interlace_multipass(l)        # levels from different passes
    flatdata = flatdata.items()
    flatdata.sort() 
    pylab.plot(*zip(*flatdata))
        
    sdr.close()
    
    pylab.show()

if __name__ == '__main__':
    main()