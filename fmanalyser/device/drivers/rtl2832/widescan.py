#! /usr/bin/env python

from pylab import *
from rtlsdr import *
from itertools import *
import sys, math, time

if len(sys.argv) != 3:
    print "use: widescan.py <start> <stop>"
    print "    frequencies in hertz"
    print "    example: widescan.py 300e6 400e6"
    sys.exit(2)

sdr = RtlSdr()
sdr.sample_rate = 2.8e6
sdr.gain = 0
sample_count = 2**18

start = float(sys.argv[1])
stop  = float(sys.argv[2])

wide_data = {}

freq = start
jump = cycle([0.5e6, 1.5e6])
while start <= freq <= (stop+1.5e6):
    sdr.center_freq = freq
    time.sleep(0.04)
    samples = sdr.read_samples(sample_count)
    a,b = psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
    # interleave ranges to dodge 0 Hz peak
    # todo - average overlapping ranges
    for x,y in izip(b,a):
        if (freq - 3e6/4) < x*1e6 < (freq - 1e6/4):
            wide_data[x] = y
        if (freq + 1e6/4) < x*1e6 < (freq + 3e6/4):
            wide_data[x] = y
    freq += jump.next()

wide_data2 = []

for x in wide_data:
    if start <= x*1e6 <= stop:
        wide_data2.append((x, 10*math.log10(wide_data[x])))

wide_data2.sort()

#for xy in wide_data2:
#    print '%f, %f' % xy

clf()
plot(*zip(*wide_data2), linewidth=0.5)
xlabel('Frequency (MHz)')
ylabel('Relative power (dB)')
show()
