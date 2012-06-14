# -*- coding: utf-8 -*-
from fmanalyser.device.drivers.base import BaseDevice

class GrDevice(BaseDevice):
    
    def __init__(self, top_block):
        self._block = top_block
        self._started = False
        
    @property
    def block(self):
        if not self._started:
            self._open()
        return self._block
    
    def _open(self):
        self.logger.info('starting gnuradio block')
        assert not self._started
        try:
            self._block.start()
            self._started = True
        except:
            self.close()
            raise
    
    def close(self):
        self._block.stop()
        self._block.wait()
    
    def tune(self, f):
        self.tune_hz(f*1000)
    
    def tune_hz(self, f):
        self.logger.debug('tune: %s MHz' % (f/1e6,))
        self.block.set_freq(f)