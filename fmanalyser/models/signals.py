# -*- coding: utf-8 -*-

from ..utils.signals import Event, EventSignal

# Variable signals
class ValueChangeEvent(Event):
    def __init__(self, old_value, new_value):
        self.old_value = old_value
        self.new_value = new_value
value_changed = EventSignal(event_cls=ValueChangeEvent)

# Bandscan signals
class ScanUpdateEvent(Event):
    def __init__(self, frequency, level):
        self.frequency = frequency
        self.level = level
scan_updated = EventSignal(ScanUpdateEvent)