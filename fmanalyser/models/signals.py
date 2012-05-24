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
    def __init__(self, freq_levels):
        self.freq_levels = freq_levels
scan_updated = EventSignal(ScanUpdateEvent)

class ScanCompletedEvent(Event):
    pass
scan_completed = EventSignal(ScanCompletedEvent)

class FftScanUpdateEvent(Event):
    def __init__(self, center_freq, rel_freqs, levels):
        self.center_freq = center_freq
        self.rel_freqs = rel_freqs
        self.levels = levels
fft_scan_updated = EventSignal(FftScanUpdateEvent)