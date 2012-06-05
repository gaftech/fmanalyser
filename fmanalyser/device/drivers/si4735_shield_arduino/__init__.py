from fmanalyser.device.drivers.base import Device
from fmanalyser.conf import options
import serial
import time
from fmanalyser.exceptions import DeviceResponseError, BadResponseFormat

class Si4735ArduinoShield(Device):
    
#    # private parameters (TODO: make it configurable?)
#    _read_lines_timeout = 0.5
    
    port = options.Option(default='/dev/ttyACM0')
    baud = options.IntOption(default=9600)
    
    @property
    def serial(self):
        if getattr(self, '_serial', None) is None:
            self._open()
        return self._serial
    
    def _open(self):
        self.logger.info("Initializing device...")
        self._serial = serial.Serial(port=self.port, baudrate=self.baud)
        self._serial.write('\r\n')
        time.sleep(2)
        self.probe('*e')
        self.probe('*d')
        self.probe('*m')
#        time.sleep(2)
        self.logger.info("Device ready")
        
    def close(self):
        if getattr(self, '_serial', None) is not None:
            self._serial.close()
            
    def probe(self, command):
        """Do the write command / read lines cycle until the 'OK' or 'ERROR' line is found.
        
        Returns the lines (excl. last one) or raises a DeviceError
        """
#        tlimit = time.time() + self._read_lines_timeout
        if getattr(self, '_serial', None) is None:
            self._open()
        self.serial.flushInput()
        self.logger.debug('write: %r' % command)
        self.serial.write(command)
        lines = []
        for line in self.serial:
            self.logger.debug('read: %r' % line)
            if line == 'ERROR':
                raise DeviceResponseError('`ERROR` received')
            if line == 'OK\r\n':
                return lines
            lines.append(line)
        raise DeviceResponseError('No response end-line (`OK` or `ERROR`) received')
    
    def tune(self, freq):
#        fstr = str(freq/10)
        cmd = '%s*F' % (freq/10,)
        self.probe(cmd)
        
    def get_frequency(self):
        lines = self.probe('?F')
        try:
            return int(lines[0])*10
        except (IndexError, ValueError):
            raise BadResponseFormat()
        
    def get_rf(self):
        lines = self.probe('?R')
        try:
            return int(lines[0])
        except (IndexError, ValueError):
            raise BadResponseFormat()
        
        
        
        
        
        