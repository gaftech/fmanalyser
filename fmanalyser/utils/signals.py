# -*- coding: utf-8 -*-

from pydispatch import dispatcher

class Event(object):
    """Base class for events.
    
    Currently, its only purpose is to identify subclass instances as being an
    event.
    """
    
class Signal(object):
    
    def connect(self, receiver, sender=dispatcher.Any, weak=True):
        dispatcher.connect(receiver, signal=self, sender=sender, weak=weak)

class EventSignal(Signal):
    
    def __init__(self, event_cls):
        self.event_cls = event_cls
        
    def send(self, sender, *event_args, **event_kwargs):
        event = self.event_cls(*event_args, **event_kwargs)
        dispatcher.send(signal=self, sender=sender, event=event)
    
    
