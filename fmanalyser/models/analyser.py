# -*- coding: utf-8 -*-
from ..client import tasks, RDS_MODE, MEASURING_MODE, STEREO_MODE
from ..utils.datastructures import NOTSET
from ..utils.log import LoggableMixin

class Analyser(LoggableMixin):
    """Represents a physical device, triggers and stores its measurements"""

    def __init__(self, client_worker, channels=()):
        self._worker = client_worker
        self._channels = list(channels)
    
    def trigger_measurements(self):
        task = None
        for channel in self._channels:
            self._worker.acquire()
            try:
                task = self._trigger_channel_measurements(channel)
            finally:
                self._worker.release()
        return task
    
    def _trigger_channel_measurements(self, channel):
        """Enqueue all necessary tasks to perform all required measurements
        for a given channel
        """
        task = None
        # Tuning to the right frequency, if specified
        if channel.frequency is not NOTSET:
            task = self._worker.enqueue(channel.tune)
        
        variables = channel.get_variables_by_mode(enabled=True)
        
        # RDS measurements
        if RDS_MODE in variables:
            # Locking for a while on rds mode
            self._lock_mode(channel, RDS_MODE)
            # Retrieving measurements
            task = self._worker.enqueue(channel.update_rds_variables)
            
        # Stereo mode measurements
        if STEREO_MODE in variables:
            self._lock_mode(channel, STEREO_MODE)
            for var in variables[STEREO_MODE]:
                task = self._worker.enqueue(var.update)
        
        # Measuring mode measurements
        if MEASURING_MODE in variables:
            self._lock_mode(channel, MEASURING_MODE)
            for var in variables[MEASURING_MODE]:
                task = self._worker.enqueue(var.update)                
        
        # Other measurements
        if None in variables:
            for var in variables[None]:
                task = self._worker.enqueue(var.update)
            
        return task
        
    def _lock_mode(self, channel, mode):
        timeout = getattr(channel, '%s_lock_time' % mode)
        self.logger.debug('locking on %s mode for %s s' % (mode, timeout))
        self._worker.enqueue('set_mode', mode)
        return self._worker.enqueue_task(tasks.Sleep(timeout))
        
        
        
        