# -*- coding: utf-8 -*-
from fmanalyser.conf import OptionHolder
from fmanalyser.utils.log import Loggable
from fmanalyser.utils.render import render_frequency
import math

class Device(Loggable, OptionHolder):
    pass

class GrDevice(Device):
    
    def __init__(self, *args, **kwargs):
        super(GrDevice, self).__init__(*args, **kwargs)
        self._block = None
        self._block_running = False
        
    @property
    def block(self):
        if self._block is None:
            self._open()
        if not self._block_running:
            self._start_block()
        return self._block
    
    def _open(self):
        self.logger.info('creating gnuradio block')
        self._block = self.get_block_cls()()
            
    def _start_block(self):
        self.logger.info('starting gnuradio block')
        assert not self._block_running
        try:
            self._block.start()
            self._block_running = True
        except:
            self.close()
            raise
            
    def close(self):
        self.stop_block()
        self._block = None
    
    def stop_block(self):
        if self._block is not None:
            self._stop_block()
    
    def _stop_block(self):
        self._block.stop()
        self._block.wait()
        self._block_running = False
    
    def tune(self, f):
        self.tune_hz(f*1000)
    
    def tune_hz(self, f):
        self.logger.debug('tune: %s MHz' % (f/1e6,))
        self.block.set_freq(f)
    
    def get_signal_level(self):
        return 10*math.log(self.get_signal_power())
    
    def get_signal_power(self):
        l = self.block.power_probe.level()
        self.logger.debug("signal power: %s" % l)
        return l