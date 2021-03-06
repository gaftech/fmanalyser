# -*- coding: utf-8 -*-
from fmanalyser.exceptions import InvalidOption
from fmanalyser.utils.parse import parse_carrier_frequency,\
    parse_subcarrier_frequency
from copy import copy
from fmanalyser.utils.datastructures import NOTSET

class Option(object):
    
    def __init__(self, name=None, default=NOTSET, required=False):
        self.name = name
        self.default = default
        self._required = required
        self._holder = None

    def clone(self):
        clone = copy(self)
        clone._holder = None
        return clone 

    def __str__(self):
        return str(self.name)

    @property
    def required(self):
        return self._required and self.default is NOTSET 

    def contribute_to_class(self, cls, name):
        assert self._holder is None
        self._holder = cls
        if self.name is None:
            self.name = name

    def clean(self, value):
        """Returns the coerced value from a raw value"""
        return value

class BooleanOption(Option):
    
    true_values = set((True, 1, '1', 'on', 'true'))
    false_values = set((False, 0, '0', 'off', 'false'))
    
    def clean(self, value):
        if isinstance(value, basestring):
            value = value.lower()
        if value in self.true_values:
            return True
        if value in self.false_values:
            return False
        raise InvalidOption("%s can't be converted to a boolean" % value)
    
class IntOption(Option):
    def clean(self, value):
        return int(value)
    
class FloatOption(Option):
    def clean(self, value):
        return float(value)


class ChoiceOption(Option):
    
    def __init__(self, choices, **kwargs):
        self.choices = choices
        super(ChoiceOption, self).__init__(**kwargs)

    def clean(self, value):
        if value not in self.choices:
            raise InvalidOption('%s not in [%s]' % (value, ', '.join(self.choices)))
        return value

class CarrierFrequencyOption(Option):
    def clean(self, value):
        return parse_carrier_frequency(value)

class SubCarrierFrequencyOption(Option):
    def clean(self, value):
        return parse_subcarrier_frequency(value)