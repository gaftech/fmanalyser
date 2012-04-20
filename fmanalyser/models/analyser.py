# -*- coding: utf-8 -*-
from ..client import tasks, RDS_MODE, MEASURING_MODE, STEREO_MODE
from ..utils.datastructures import NOTSET
from ..utils.log import LoggableMixin

class Analyser(LoggableMixin):
    """Represents a physical device, triggers and stores its measurements"""

    def __init__(self, client_worker, channels=()):
        self._worker = client_worker
        self._channels = list(channels)
    
    def enqueue_updates(self):
        task = None
        for channel in self._channels:
            task = channel.enqueue_updates(self._worker)
        return task
    
        
        
        
        