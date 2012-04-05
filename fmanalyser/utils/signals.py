# -*- coding: utf-8 -*-
from pydispatch import dispatcher

EMPTY = object()

class Signal(object):
    pass

class EventSignal(Signal):
    
    def __init__(self, event_class):
        self.name = event_class.__name__
    
    def __str__(self):
        return self.name

class EventBase(type):
    
    def __new__(cls, name, bases, attrs):
        new_class = super(EventBase, cls).__new__(cls, name, bases, attrs)
        if attrs.get('signal', None) is None:
            new_class.signal = EventSignal(new_class)
        return new_class

class BaseEvent(object):
    
    __metaclass__ = EventBase
    
    kwargs = ()
    
    @classmethod
    def connect(cls, receiver, sender=dispatcher.Any, weak=True):
        dispatcher.connect(receiver, signal=cls.signal, sender=sender, weak=weak)
    
    def __init__(self, sender, **kwargs):
        assert getattr(self, 'signal', None) is not None
        self.sender = sender
        for k in self.kwargs:
            setattr(self, k, kwargs.pop(k, EMPTY)) 
        if len(kwargs):
            raise ValueError('Unexpected kwargs : %s' % ', '.join(kwargs))
        
    def fire(self):
        kwargs = dict(
            signal = self.signal,
            sender = self.sender,
            event = self
        )
        return dispatcher.send(**kwargs)
        

