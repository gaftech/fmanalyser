"""
(c) Gabriel Fournier 2012

..see:: http://gitorious.org/rtl2832

"""
from fmanalyser.device.drivers.base import Device
from buspirate.i2c import I2C
from fmanalyser.exceptions import DeviceError, DeviceResponseError
from fmanalyser.conf import options

class BusPirateI2CBackend(object):
    
    def __init__(self, write_address, read_address):
        self.write_address = write_address
        self.read_address = read_address
        self.i2c = I2C()

    def close(self):
        self.i2c.close()
    
    def write_registers(self, data, start):
        self.i2c.send_start_bit()
        try:
            self.i2c.send_check(self.write_address, start, *data)
        finally:
            self.i2c.send_stop_bit()

    def read_register(self, addr):
        return self.read_registers(addr, addr)[0]
    
    def read_registers(self, start=0x00, stop=0x15):
        self.i2c.send_start_bit()
        try:
            self.i2c.send_check(self.write_address, start)
            self.i2c.send_start_bit()
            r = self.i2c.send_receive(self.read_address, stop - start + 1)
        finally:
            self.i2c.send_stop_bit()
        return [ord(b) for b in r]   



class Max3543(Device):

    IFOUT_DTV_DIFF = 0x00
    IFOUT_DTV_SINGLE = 0x01
    IFOUT_ATV = 0x02

    # TFS and TFP: for now, fixed values are used (107,7 MHz values from Windows software).
    # TODO: Get/adapt/use Maxim code mentioned in datasheet
    TFS = 0x86
    TFP = 0x14
    

    f_ref = options.IntOption(default=16,
        ini_help = "Reference frequency (MHz)")
    f_if = options.IntOption(default=36,
        ini_help = "IF frequency (MHz)")
    lna_gain = options.BooleanOption(default=True,
        ini_help = "LNA gain. True: nominal. False: -2.5 dB")
    if_bw_8MHz = options.BooleanOption(default=False,
        ini_help = "Set bandwidth mode to 8 MHz (True) or 7 MHz (False).")
    if_sel = options.IntOption(choices=(IFOUT_DTV_DIFF, IFOUT_DTV_SINGLE, IFOUT_ATV), default=IFOUT_DTV_DIFF,
        ini_help = "Selects IF output between 'DTV differential' (%s), 'DTV single-ended' (%s) and 'ATV single-ended' (%s)" % (
                    IFOUT_DTV_DIFF, IFOUT_DTV_SINGLE, IFOUT_ATV))
    ref_out_div = options.BooleanOption(default=True,
        ini_help = "Sets REFOUT signal frequency to XTAL/4 (True) or XTAL (False)")
    write_address = options.IntOption(default=0xC2)
    read_address = options.IntOption(default=0xC3)
    
    def __init__(self, *args, **kwargs):
        super(Max3543, self).__init__(*args, **kwargs)
        self.i2c_backend = BusPirateI2CBackend(write_address=self.write_address,
                                               read_address=self.read_address)
        self.init_device()
    
    def close(self):
        self.i2c_backend.close()

    def init_device(self):
        """Write all registers to initial state"""

        self.logger.debug("Initializing register cache...")
        self._registers = self.i2c_backend.read_registers()
        
        self._logger.debug("Loading ROM params...")
#        self._if_adj = self._read_rom(0xA) & 0x3f

        # Regs set from ROM
        regs = []
        regs.append(self._read_rom(0xA) & 0x3f) # 0x0D
        regs.append(0x00) # 0x0E (0x00 -> not reading ROM)
        regs.append(self._read_rom(0xB)) # 0x0F
        self.write_registers(regs, 0x0D)
        
        # 0x13: BIAS adjustments
        self.write_registers([self._bias_adj_register()], 0x13)
        
        # 0x00 to 0x0C
        regs = []
        regs.extend(self._tune_registers(47)) # Regs 0x00 to 0x07
        regs.append(self._shutdown_register(standby=False)) # 0x08
        regs.append(0x0A | (not self.ref_out_div)) # 0x09
        regs.append(self._vas_config_register()) #0x0A
        regs.extend(self._pwrdet_registers()) # 0x0B and 0x0C
        self.write_registers(regs)
    
    def _shutdown_register(self, standby=False):
        r = bool(standby) << 8
        if self.if_sel == self.IFOUT_ATV:
            r |= 1 << 3
        return r
    
    def _vas_config_register(self):
        """For now, returns default values except for LFDIV
        TODO: add params
        """
        r = 0x17
        if self.f_ref > 28:
            r |= 2 << 6
        elif self.f_ref > 20:
            r |= 1 << 6
        return r
    
    def _pwrdet_registers(self):
        """For now returns default values for 0x0B and 0x0C registers
        TODO: add params
        """
        return [0x43,0x01]
    
    def _bias_adj_register(self):
        #TODO: yes, do it !
        return 0x56
    
    def tune_MHz(self, f):
        self.write_registers(self._tune_registers(f))
    
    def get_frequency_MHz(self):
        vdiv = 4 * 2 ** (self._registers[0x00] & 0x3)   
        ndiv_i = self._registers[0x01]
        rdiv = ((self._registers[0x2] >> 4) & 0x3) + 1
        ndiv_f = ((self._registers[0x2] & 0xf) << 16) \
                | ((self._registers[0x3]) << 8) \
                | self._registers[0x4]
        ndiv = ndiv_i + float(ndiv_f) / 2**20
        
        f_vco = self.f_ref / rdiv * ndiv * 4
        f_lo = f_vco / vdiv
        
        return f_lo - self.f_if
    
    def _tune_registers(self, f):
        """Returns appropriate 0x00 to 0x07 register values to tune device at `f` MHz"""
        
        regs = self._registers[:8]
        
        f_lo = float(f) + self.f_if
        
        # VCO Divider
        if f_lo < 137.5:
            vdiv_b = 3
        elif f_lo < 275:
            vdiv_b = 2
        elif f_lo < 550:
            vdiv_b = 1
        else:
            vdiv_b = 0
        vdiv = 4 * 2 ** vdiv_b
        regs[0x00] = (regs[0x00] & 0xf0) | vdiv_b

        # Reference divider
        rdiv = 1 # TODO: make it configurable
        rdiv_b = rdiv - 1 
        
        # PLL divider
        ndiv = (f_lo * vdiv) / (self.f_ref / rdiv * 4)
        # integer part
        ndiv_i = int(ndiv)
        regs[0x01] = ndiv_i
        # 20 bits frac part
        ndiv_f = int((ndiv-int(ndiv))*2**20)
        regs[0x02] = 0x80 | (regs[0x02] & 0x40) | (rdiv_b << 4) | (ndiv_f >> 16)
        regs[0x03] = (ndiv_f >> 8) & 0xff
        regs[0x04] = 0xff & ndiv_f

        # Mode control (lna gain...)
        r5 = 0x00
        if self.lna_gain:
            r5 |= 0x80
        if f > 345:
            r5 |= 0x40
        if f < 110:
            r5 |= 0x20
        if self.if_bw_8MHz:
            r5 |= 0x10
        if f > 440:
            r5 |= 0x02 << 2
        elif f > 196:
            r5 |= 0x01 << 2
        r5 |= self.if_sel
        regs[0x05] = r5
        
        regs[0x06] = self.TFS
        regs[0x07] = self.TFP
        
        return regs
    
    def write_registers(self, data, start=0x00):
        """Write bytes in `data` to device registers and update the local cache"""
        self.logger.debug("Updating registers 0x%02X to 0x%02X..." % (start, start+len(data)-1))
        self.i2c_backend.write_registers(data, start)
        self._registers[start:start+len(data)] = data
    
    def _read_rom(self, addr):
        assert addr >= 0x0 and addr <= 0xC
        self.i2c_backend.write_registers([addr], 0x0E)
        return self.i2c_backend.read_register(0x10)
        