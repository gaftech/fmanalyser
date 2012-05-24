from fmanalyser.device.drivers.base import GrDevice
from fmanalyser.utils.render import render_frequency

class Funcube(GrDevice):

    def get_block_cls(self):
        from .fcd_block import fcd_block
        return fcd_block


