from fmanalyser.device.drivers.base import GrDevice

class GrRtl2832(GrDevice):
    
    def get_block_cls(self):
        from . import gr_rtl
        return gr_rtl.gr_rtl
#    
#    def _start_block(self):
#        self.logger.info('starting gnuradio block')
#        assert not self._block_running
#        self._block.Run(True)
#        self._block_running = True