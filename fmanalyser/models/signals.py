# -*- coding: utf-8 -*-

from ..utils.signals import Event, Signal, EventSignal

class ValueChangeEvent(Event):
    
    def __init__(self, variable, old_value, new_value):
        self.variable = variable
        self.old_value = old_value
        self.new_value = new_value

value_changed = EventSignal(event_cls=ValueChangeEvent)