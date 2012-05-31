#!/usr/bin/env python
# -*- coding: utf-8 -*-

import buspirate
import logging
import time

def main():
    
    logging.basicConfig(level=logging.DEBUG)
    
    logging.debug('logging test')
    
    bp = buspirate.BusPirate(port='/dev/ttyUSB1')
    bp.reset()
    
    api = bp.bitbang()
    api.configure_miso(as_input=False)
    
    api.set_pins(0)
    
    api.set_pin(api.PINS['MISO'], high=True)
    api.psu()
    time.sleep(0.1)
    api.aux()
    time.sleep(0.1)
    
    api.spi()
    
#    time.sleep(0.5)
#    api.set_pin(api.PINS['MISO'], high=True)
#    api.psu(False)
#    api.aux(False)
#    
#    
#    
#    api.psu(True)
    
    
    bp.flush()












if __name__ == "__main__":
    main()
