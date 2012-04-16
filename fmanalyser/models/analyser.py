# -*- coding: utf-8 -*-
from ..utils.datastructures import NOTSET
from ..client import tasks, RDS_MODE, MEASURING_MODE, STEREO_MODE

class Analyser(object):
    """Represents a physical device, triggers and stores its measurements"""

    def __init__(self, client_worker, channels=()):
        self._worker = client_worker
        self._channels = list(channels)
        
    def _trigger_channel_measurements(self, channel):
        """Enqueue all necessary tasks to perform all required measurements
        for a given channel
        """
        self._worker.acquire()
        try:
            # Tuning to the right frequency, if specified
            if channel.frequency is not NOTSET:
                self._worker.enqueue(channel.tune)
            
            variables = channel.get_variables_by_mode(enabled=True)
            
            for mode in (RDS_MODE, STEREO_MODE, MEASURING_MODE, None):
                if not variables.get(mode):
                    continue
            
            
            
            
            # RDS measurements
            if variables.get(RDS_MODE):
                self._worker.enqueue('set_rds_mode')
                # Locking on rds mode
                self._worker.enqueue_task(tasks.Sleep(channel.rds_lock_time))
                # Retrieving measurements
                self._worker.enqueue(channel.update_rds_data)
                
            # Stereo mode measurements
            if variables.get(STEREO_MODE):
                self._worker.enqueue('set_stereo_mode')
                self._worker.enqueue_task(tasks.Sleep(channel.stereo_lock_time))
                for var in variables[STEREO_MODE]:
                    self._worker.enqueue(var.update)
            
            # Measuring mode measurements
            if variables.get(MEASURING_MODE):
                self._worker.enqueue('set_measuring_mode')
                self._worker.enqueue_task(tasks.Sleep(channel.measuring_lock_time))
                
                
                
            
            
        finally:
            self._worker.release()
        
    def _lock_mode(self, channel, mode):
        self._worker.enqueue('set_mode', mode)
        timeout = getattr(channel, '%s_lock_time' % mode)
        self._worker.enqueue_task(tasks.Sleep(timeout))
        
        
        
        