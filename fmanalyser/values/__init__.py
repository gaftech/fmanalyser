# -*- coding: utf-8 -*-
from . import validators
from ..utils.datastructures import NOTSET
from ..utils.log import LoggableMixin
from .signals import ValueChangeEvent
from pydispatch import dispatcher
import threading

class Variable(LoggableMixin, object):
    
    change_event_cls = ValueChangeEvent
    
    def __init__(self, owner, descriptor, validator):
        
        assert isinstance(validator, validators.Validator)
        
        self._owner = owner
        self._descriptor = descriptor
        self._validator = validator
        
        self._value = NOTSET
        self._command = NOTSET
        self._lock = threading.Lock()

    def __str__(self):
        return '%s: %s' % (self._descriptor._key, self._descriptor.format_value(self._value))

    @property
    def descriptor(self):
        return self._descriptor
    
    @property
    def validator(self):
        return self._validator

    @property
    def value(self):
        return self._value

    def _get_enabled(self):
        return self._validator.enabled

    def _set_enabled(self, value):
        self._validator.enabled = value
    
    enabled = property(_get_enabled, _set_enabled)
    
    def get_value(self):
        return self._value
    
    def set_value(self, value):
        # TODO: Learn/understand more about locks to determine if locking has any interest
        with self._lock:
            event = self.change_event_cls(
                sender = self,
                descriptor = self.descriptor,
                key = self.descriptor.key,
                old_value = self._value,
                new_value = value
            )
            self._value = value
        event.fire()
    
    def get_command(self):
        return self._command
    
    def set_command(self, value, clean_value=True):
        if clean_value:
            value = self._validator.clean(value)
        self._command = value
    
    def connect_change_listener(self, listener, weak=True):
        self.change_event_cls.connect(listener, sender=self, weak=weak)
    
    def read(self, client):
        """Probes the device client to get actual value""" 
        with self._lock:
            return self._descriptor.read(client)
    
    def write(self, client):
        with self._lock:
            self._descriptor.write(client, self._command)
     
    def update(self, client):
        if self.enabled:
            self.set_value(self.read(client))
        else:
            self.logger.debug('%s measurement disabled' % self.descriptor)
    
    
    