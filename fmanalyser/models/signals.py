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
    def __init__(self, center_freq, raw_freqs, raw_levels, cleaned_freqs, cleaned_levs):
        self.center_freq = center_freq
        self.raw_freqs = raw_freqs
        self.raw_levels = raw_levels
        self.cleaned_freqs = cleaned_freqs
        self.cleaned_levs = cleaned_levs
fft_scan_updated = EventSignal(FftScanUpdateEvent)