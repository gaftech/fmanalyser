#!/usr/bin/env python
'''
Created on 21 juin 2012

@author: gabriel
'''
from fmanalyser.device.drivers.max3543 import Max3543
import logging
import time 
logging.basicConfig(level=logging.DEBUG)

def main():
    
    d = Max3543()
    print "F = %s MHz" % d.get_frequency_MHz()

    d.tune_MHz(107.7)
    print "F = %s MHz" % d.get_frequency_MHz()


    f = 100
    stop = 120
    step = 1
    while f <= stop:
        d.tune_MHz(f)
        print "F = %s MHz" % d.get_frequency_MHz()
        time.sleep(0.1)
        f += step
        
    d.close()

if __name__ == '__main__':
    main()