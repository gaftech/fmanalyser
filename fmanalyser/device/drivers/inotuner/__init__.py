# -*- coding: utf-8 -*-
from fmanalyser.device.drivers.base import Device
from fmanalyser.conf import options
import serial
from serial.serialutil import SerialException
from fmanalyser.exceptions import DeviceResponseError, DeviceTimeout,\
    ConfigError
import time
import math

COMMAND_MODE_RESPONSE = "COMMAND MODE"
COMMAND_MODE_TIMEOUT = 1
DEVICE_READY_RESPONSE = "DEVICE READY"
DEVICE_INIT_TIMEOUT = 2
#: default timeout when waiting for a particular line
TIMEOUT = 10
#: timeout for serial.Serial object
SERIAL_TIMEOUT = 0.1

# Arduino analog inputs reference
REF_VOLTAGE = 3.3

# Choices for RF level voltage source
LEVEL_SOURCE_MAX2016 = 'max2016'
LEVEL_SOURCE_AD8307 = 'ad8307'
LEVEL_SOURCE_CHOICES = (
    LEVEL_SOURCE_MAX2016,
    LEVEL_SOURCE_AD8307,
)

# voltage source spec
MAX2016_MV_PER_DB = 18
AD8307_MV_PER_DB = 25

class ArduinoTuner(Device):
    
    port = options.Option(default="/dev/ttyACM0",
        ini_help="Serial port")
    baudrate = options.IntOption(default=9600)
    level_src = options.Option(choices=LEVEL_SOURCE_CHOICES, default=LEVEL_SOURCE_MAX2016)
    
    def __init__(self, *args, **kwargs):
        super(ArduinoTuner, self).__init__(*args, **kwargs)
        self._open()
        
    
    def _open(self):
        self.serial = serial.Serial(port=self.port, baudrate=self.baudrate,
                                    timeout=SERIAL_TIMEOUT)
        # Note: above line triggers an arduino reset with Uno rev. 2 but not with Pro 3.3 V.
        # TODO: Validate code to work with both devices (and other eventually)
        
        # Are we already in command mode ?
        if not self.ping():
            # No, we are not
            try:
                # Maybe the device has just been reset
                self.wait_line(DEVICE_READY_RESPONSE, DEVICE_INIT_TIMEOUT)
            except DeviceTimeout:
                self.write("+++")
                self.wait_line(COMMAND_MODE_RESPONSE, COMMAND_MODE_TIMEOUT)
        
    def close(self):
        try:
            self.serial.close()
        except SerialException:
            self.logger.debug('serial port already closed')

    def ping(self):
        self.serial.flushInput()
        self.write('?p')
        try:
            self.wait_line(COMMAND_MODE_RESPONSE, COMMAND_MODE_TIMEOUT)
            return True
        except DeviceTimeout:
            return False
    
    def tune(self, f):
        self.probe("%sk*f" % f)
    
    def get_rf(self):
        lines = self.probe("?l")
        try:
            l = float(lines[-1])
        except IndexError:
            raise DeviceResponseError("response missing rf level value line")
        except ValueError, e:
            raise DeviceResponseError("bad rf level response format: %s" % (e,))
        return self._get_rf_level(l)
        
#        if l <= 0:
#            l = 1;
#        step_uv = REF_VOLTAGE * 10**6 / 1024
#        l_uv = l * step_uv
#        l_db = 20 * math.log10(l_uv)
#        return l_db
    
    def _get_rf_level(self, byte_value):
        """Returns RF level corresponding to the raw voltage info delivered by the arduino adc (0-1023).
        Calculation from this raw value depends on the `level_src` option.
        """
        voltage = self._get_voltage(byte_value)
        if self.level_src in (LEVEL_SOURCE_MAX2016, LEVEL_SOURCE_AD8307) :
            if self.level_src == LEVEL_SOURCE_MAX2016:
                # reference : 2V => 10 dBm
                vref = 2
                pref = 10
                mv_per_db = MAX2016_MV_PER_DB
            elif self.level_src == LEVEL_SOURCE_AD8307:
                vref = 2.65
                pref = 16
                mv_per_db = AD8307_MV_PER_DB
            vdif = vref - voltage
            pdif = vdif / (float(mv_per_db) / 1000)
            pdbm = pref - pdif
            return pdbm
        elif self.level_src == LEVEL_SOURCE_AD8307:
            vdif = REF_VOLTAGE - voltage
            
        else:
            raise ConfigError("unknown level voltage source: %s" % self.level_src)
        
    def _get_voltage(self, byte_value):
        return REF_VOLTAGE / 1023 * byte_value
    
    def probe(self, command, timeout=TIMEOUT):
        """Do the write command / read lines cycle until the 'OK' or 'ERROR' line is found or timeout is reached.
        
        Returns the lines (excl. last one) or raises a DeviceError
        """
        self.serial.flushInput()
        self.write(command)
        lines = []
        limit = time.time() + timeout
        while time.time() < limit:
            line = self.readline()
            if line == "ERROR":
                raise DeviceResponseError('`ERROR` received')
            if line == 'OK':
                return lines
            lines.append(line)
        raise DeviceTimeout("did not get 'OK' or 'ERROR'")

    def wait_line(self, line, timeout, check_ok=True):
        limit = time.time() + timeout
        while time.time() < limit:
            if self.readline() != line:
                continue
            if check_ok:
                ok = self.readline()
                if ok != "OK":
                    raise DeviceResponseError("expected: 'OK', got: %r" % ok)
            return
        raise DeviceTimeout("did not get expected response: %s" % (line,))

    def write(self, data):
        self.logger.debug('write: %r' % data)
        self.serial.write(data)
    
    def readline(self):
        l = self.serial.readline()
        l = l.strip()
        self.logger.debug('read: %r' % l)
        return l
        
    