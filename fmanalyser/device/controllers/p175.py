# -*- coding: utf-8 -*-
from fmanalyser.device.controllers.base import DeviceController
from fmanalyser.device.drivers.p175 import P175, MEASURING_MODE, RDS_MODE
from fmanalyser.device.worker import tasks
from fmanalyser.conf import options

class P175Controller(DeviceController):
    
    device_class = P175
    
    rds_lock_time = options.FloatOption(default=5, 
        ini_help="Time during the program sleeps, waiting for the device to acquire measurements in rds mode.")
    mes_lock_time = options.FloatOption(default=5,
        ini_help="Time during the program sleeps, waiting for the device to acquire measurements in measuring mode.")
    stereo_lock_time = options.FloatOption(default=5,
        ini_help="Time during the program sleeps, waiting for the device to acquire measurements in stereo mode.")
    
    rds_data_keys = (
        'pi', 'ps', # TODO: yes, do it !
    )
    
    def update_channel_variables(self, device, channel, measuring=True, rds=True):
        for variable in channel.filter_variables(enabled=True):
            if not rds and variable.attname in self.rds_data_keys:
                continue 
            method = getattr(self.device, 'get_%s' % variable.attname)
            value = method()
            variable.update(value)

    def update_channel_rds_data(self, device, channel):
        data = device.get_rds_data()
        for k, v in data:
            channel.get_variable(k).set_value(v)
    
    def _enqueue_channel_update(self, channel):
        
        do_freq = False
        mes_vars, rds_vars = [], []
        for variable in channel.filter_variables(enabled=True):
            if variable.attname == 'frequency':
                do_freq = True
            elif variable.attname in self.rds_data_keys:
                rds_vars.append(variable)
            else:
                mes_vars.append(variable)
        
        task = None
        self.worker.acquire()
        try:
            
            # Tuning to the right frequency, if specified
            f = channel.get_frequency()
            if f:
                task = self.worker.enqueue('tune', f)
            
            if do_freq:
                task = self.worker.enqueue(self.update_channel_variable)
            
            if mes_vars:
                self._enqueue_mode_lock(MEASURING_MODE)
            
            if mes_vars or do_freq:
                task = self.worker.enqueue(self.update_channel_variables, channel, rds=False)
            
            if rds_vars:
                self._enqueue_mode_lock(RDS_MODE)
                task = self.worker.enqueue(self.update_channel_rds_data, channel)
                
        finally:
            self.worker.release()
            
        return task
        
    def _enqueue_mode_lock(self, mode):
        timeout = getattr(self, '%s_lock_time' % mode)
        self.logger.debug('enqueueing %s mode lock for %s s' % (mode, timeout))
        self.worker.enqueue('set_mode', mode)
        return self.worker.enqueue_task(tasks.Sleep(timeout))
    
        
    