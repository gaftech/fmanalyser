# -*- coding: utf-8 -*-
from ..utils.log import Loggable

class Analyser(Loggable):
    """Represents a physical device, triggers and stores its measurements"""

    def __init__(self, client_worker, channels=()):
        self._worker = client_worker
        self._channels = list(channels)
    
    def enqueue_updates(self):
        task = None
        for channel in self._channels:
            task = channel.enqueue_updates(self._worker)
        return task
    
        
        
        
        