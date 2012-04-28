# -*- coding: utf-8 -*-

from ..exceptions import DeviceNotFound, MultipleDevicesFound, PortLocked
from ..utils.conf import options, OptionHolder
from ..utils.log import Loggable
from ..utils.parse import parse_carrier_frequency, parse_subcarrier_frequency, \
    parse_int, parse_histogram_data, parse, parse_float
from ..utils.threads import Lockable, locking
from copy import copy
import fcntl
import serial
import threading
import time
from fmanalyser.exceptions import BadResponseFormat, SerialError
from serial.serialutil import SerialException

MEASURING_MODE = 'mes'
STEREO_MODE = 'stereo'
RDS_MODE = 'rds'
MODE_CHOICES = (MEASURING_MODE, RDS_MODE, STEREO_MODE)

class P175(Loggable, OptionHolder):
    
    config_section_name = 'device'
    
    port = options.Option()
    use_cache = options.BooleanOption(default=False)
    
    serial_options = {
        'baudrate': 19200,
        'timeout': 1,
    }
    
    @classmethod
    def _autodetect(cls):
        try:
            import pyudev
        except ImportError:
            raise ImportError("You must have pyudev installed to use device auto-detection feature")
        
        context = pyudev.Context()
        gen = context.list_devices(subsystem='tty', ID_VENDOR='P175')
        results = list(gen)
        if len(results) == 0:
            raise DeviceNotFound("Can't find any usb P175")
        if len(results) > 1:
            raise MultipleDevicesFound("Many P175 connected to the system")
        device = results[0]
        return device.device_node
    
    
    def __init__(self, *args, **kwargs):
        super(P175, self).__init__(*args, **kwargs)
        self._socket = None
        self._reset_cache()
        self._lock = threading.Lock()
    
    def _reset_cache(self):
        self._mode = None
    
    @property
    def socket(self):
        if self._socket is None:
            self._open()
        return self._socket
    
    def _open(self, timeout=1):
        
        self.logger.debug('opening serial port...')

        self._reset_cache()

        opts = copy(self.serial_options)
        if self.port is not None:
            opts['port'] = self.port
        elif opts.get('port') is None:
            opts['port'] = self._autodetect()
        socket = serial.Serial(**opts)

        self._lock_device(socket)
        
        self._socket = socket
        
        self.logger.info('device opened on port %s' % self._socket.port)
    
    def _lock_device(self, socket, timeout=1):
        limit = time.time() + timeout
        while time.time() < limit:
            try:
                return fcntl.flock(socket, fcntl.LOCK_EX|fcntl.LOCK_NB)
            except IOError:
                pass
        raise PortLocked('serial port seems to be locked')
    
    def close(self):
        self._reset_cache()
        if self._socket is None:
            self.logger.debug('serial port already closed')
        else:
            self.logger.debug('closing serial port %s...' % self._socket)
            fcntl.flock(self._socket, fcntl.LOCK_UN)
            self._socket.close()
            self._socket = None
            self.logger.debug('serial port closed')
        self.logger.info('device released')
    
    @property
    def online(self):
        return self._socket is not None and self._socket.isOpen()
    
    def _probe_line(self, command, index=1, eof='\r\n', size=None, formatter=lambda x: x):
        lines = self._probe_lines(command, eof, size)
        # Extracting and formatting response
        try:
            return formatter(lines[index])
        except Exception, e:
            msg = 'error while formatting response: %s:%s' % (e.__class__.__name__, e)
            self.logger.warning(msg, exc_info=True)
            raise BadResponseFormat(msg)
    
    def _probe_lines(self, command, eof='\r\n', size=None):
        self._write(command)
        return self._read_lines(eof, size)
    
    def _write(self, command):
        self.logger.debug('writing: %s' % command)
        try:
            self.socket.write(command)
        except SerialException, e:
            raise SerialError(origin=e)
    
    def _read_lines(self, eof='\r\n', size=None):
        lines = []
        try:
            for line in self.socket:
                lines.append(line)
                if size is None:
                    if line == eof:
                        break
                elif len(lines) >= size:
                    break
        except SerialException, e:
            raise SerialError(origin=e)
        self.logger.debug('response : %s' % ' '.join(l.strip() for l in lines))
        return lines

    def is_readable(self, key):
        return hasattr(self, 'get_%s' % key.lower())

    def is_writable(self, key):
        return hasattr(self, 'set_%s' % key.lower())

    def read(self, key):
        method = getattr(self, 'get_%s' % key.lower(), None)
        if method is not None:
            return method()
        raise ValueError("Unknown readable value for this key : %s" % key)
            
    def write(self, key, value):
        method = getattr(self, 'set_%s' % key.lower(), None)
        if method is not None:
            return method(value)
        raise ValueError("Unknown writable value for this key : %s" % key)
    
    def get_frequency(self):
        """Returns the current frequency, an an integer, in kHz"""
        return self._probe_line('?F', formatter=parse_carrier_frequency)
    
    def set_frequency(self, f, force=False):
        """Sets the device frequency to f (kHz)
        
        :param boolean force:
            If true, the set-frequency command will be send, whatever is the
            actual frequency. Setting this to false can avoid to lose device-side
            data if it is already tuned to the requested frequency. 
        """
        if not force and self.get_frequency() == int(f):
            return
        self._write('%s*F' % str(f).zfill(6))
    
    #: alias for :meth:`set_frequency`
    tune = set_frequency
    
    def tune_up(self):
        self._write('*+')
    
    def tune_down(self):
        self._write('*-')
    
    def get_rf(self):
        return self._probe_line('?U', formatter=parse_float)
    
    def get_quality(self):
        return self._probe_line('?Q', formatter=parse)
    
    def get_rds(self):
        return self._probe_line('?R', formatter=parse_subcarrier_frequency)
    
    def get_pilot(self):
        return self._probe_line('?L', formatter=parse_subcarrier_frequency)
    
    def get_rds_data(self):
        # TODO: implement me !
        return {}
        
    def get_basic_data(self):
        # It seems that working on line count and line numbers is not reliable
        raise NotImplementedError('Work to do !')
        lines = self._probe_lines('?B', size=221)
        data = {
            'frequency': parse_carrier_frequency(lines[1]),
            'quality': parse_int(lines[4]),
            'pilot': parse_subcarrier_frequency(lines[7]),
            'rds': parse_subcarrier_frequency(lines[10]),
            'rds_phase': parse_int(lines[13]),
            'mod_power': parse_float(lines[16]),
            'histo': parse_histogram_data(lines[19:141]),
            'PS': parse(lines[143]),
            'PI': parse(lines[145]),
            'PTY': parse_int(lines[149]),
            'TP': parse_int(lines[152]),
            'TA': parse_int(lines[155]),
            'MS': parse_int(lines[158]),
            'DI': parse_int(lines[161]),
            'RT': parse(lines[164]),
            'CT': parse(lines[167]),
            'LTO': parse(lines[170]),
            'AF': parse(lines[173]),
            'ECC': parse(lines[175]),
            'LIC': parse(lines[178]),
            'PIN': parse(lines[181]),
            'PTYN': parse(lines[184]),
            'EON': None, # TODO: seems to be empty !
        }
        return data
        
    def activate_modulation_power_sending(self):
        self._write('*P')
    
    def deactivate_modulation_power_sending(self):
        self._write('*p')        
    
    def activate_max_value_sending(self):
        self._write('*M')
    
    def deactivate_max_value_sending(self):
        self._write('*m')    
        
    def activate_rds_groups_sending(self):
        self._write('*R')

    def deactivate_rds_groups_sending(self):
        self._write('*r')    
    
    def get_mode(self):
        """Returns the current device mode or None if unknown.
        Returned value relies on cache so it may not correspond to the real device mode.
        Use this method only if you're sure that mode can't be changed manually or by another software or client instance.
        
        :returns string: one of the `*_MODE` constants or None if :meth:`set_mode` has not already been called 
        """
        return self._mode
    
    def set_measuring_mode(self):
        self.set_mode(MEASURING_MODE)
        
    def set_rds_mode(self):
        self.set_mode(RDS_MODE)
        
    def set_stereo_mode(self):
        self.set_mode(STEREO_MODE)

    def set_mode(self, mode, force=False):
        if force or self._mode != mode:
            cmd = {
                MEASURING_MODE: '*E',
                RDS_MODE: '*D',
                STEREO_MODE: '*B',
            }[mode]
            self._write(cmd)
            self._mode = mode
        
    def save_to_eeprom(self):
        self._write('*S')
        
    def clear_device_data(self):
        self._write('*C')    
    
    def reset_device(self):
        self._write('RESET*X')
    
    def activate_lcd_light(self):
        self._write('*0')

    def set_auto_lcd_light(self, save=False):
        self._set_dip_switch(0, 0)
    
    def set_manual_lcd_light(self, save=False):
        self._set_dip_switch(0, 1)
    
    def switch_on_manual_lcd_light(self, save=False):
        self._set_dip_switch(1, 1)
    
    def switch_off_manual_lcd_light(self, save=False):
        self._set_dip_switch(1, 0)
    
    def activate_fine_tuning(self, save=False):
        self._set_dip_switch(2, 0)
    
    def deactivate_fine_tuning(self, save=False):
        self._set_dip_switch(2, 1)
    
    def set_low_scan_sensitivity(self, save=False):
        self._set_dip_switch(3, 0)
    
    def set_high_scan_sensitivity(self, save=False):
        self._set_dip_switch(3, 1)
    
    def _set_dip_switch(self, switch, state, save):
        if isinstance(state, bool):
            state = {True: 1, False: 0}[state]
        self._write('DIP%s:%s*X' % (switch, state))
        if save:
            self.save_to_eeprom()
        
    def set_lcd_page(self, n):
        self._write('*%s' % n)
        

