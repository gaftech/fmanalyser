# -*- coding: utf-8 -*-
from copy import copy
from fmanalyser.exceptions import InvalidOption, MissingOption
from fmanalyser.utils.parse import parse_carrier_frequency, \
    parse_deviation_level
import math
import os
import json

class BaseOption(object):
    _creation_counter = 0
    
    def __init__(self, required=None, default=None, choices=None,
                 value_type=lambda x: x, null=True, null_value=None,
                 ini_help=''):
        
        self._creation_order = Option._creation_counter
        Option._creation_counter += 1
        
        self._required = required
        self.default = default
        self.choices = choices
        self.value_type = value_type
        self.null = null
        self.null_value = null_value
        self.ini_help = ini_help
        
        self._holder = None
        self._attname = None
    
    def __str__(self):
        return '%s: %s.%s' % (self.__class__.__name__, 
                              getattr(self._holder, '__name__', self._holder),
                              self.attname)

    def clone(self):
        #TODO: Implement in a way that __copy__ can be used
        other = copy(self)
        other._creation_order = Option._creation_counter
        Option._creation_counter += 1
        other._holder = None
        other._attname = None
        return other
    
    @property
    def required(self):
        return self._required and self.default is None 

    @property
    def attname(self):
        return self._attname

    @property
    def holder(self):
        return self._holder

    def contribute_to_class(self, cls, name):
        assert self._holder is None
        self._holder = cls
        self._attname = name

    def pop_val_from_dict(self, d):
        assert self._attname is not None
        if self.required and self._attname not in d:
            raise MissingOption(self._attname)
        return d.pop(self._attname, self.default)

    def clean(self, value):
        """Returns the parsed value from a user input raw value
        
        :raise: OptionError
        """
        if value is None:
            if self.required:
                raise MissingOption("%s required, can't be `None`" % self)
        else:
            value = self.value_type(value)
        if self.choices is not None and value not in self.choices:
            raise InvalidOption('%s: %s not in [%s]' % (self, value, ', '.join(str(c) for c in self.choices)))
        return value

    def unclean(self, value):
        """Returns a parseable value"""
        return str(value)

    def get_null_value(self):
        if self.null_value is None:
            raise NotImplementedError(
                "%s must define a `null_value` attribute" % (self,))
        return self.null_value

class Option(BaseOption):
    
    def __init__(self, **kwargs):
        kwargs.setdefault('value_type', str)
        super(Option, self).__init__(**kwargs)

class BooleanOption(Option):
    
    def __init__(self,
                 true_values=(True, 1, '1', 'on', 'true'),
                 false_values=(False, 0, '0', 'off', 'false'),
                  **kwargs):
        self.true_values = set(true_values)
        self.false_values = set(false_values)
        defaults = {
            'value_type': bool,
            'default': False,
        }
        defaults.update(kwargs)
        super(BooleanOption, self).__init__(**defaults)
    
    def clean(self, value):
        if isinstance(value, basestring):
            value = value.lower()
        if value in self.true_values:
            return True
        if value in self.false_values:
            return False
        raise InvalidOption("%s: %s can't be converted to a boolean" % (self, value))

class NullBooleanOption(BooleanOption):
    
    def __init__(self, **kwargs):
        defaults = {'null': True, 'default': None}
        defaults.update(kwargs)
        super(NullBooleanOption, self).__init__(**kwargs)
    

class IntOption(Option):
    
    def __init__(self, value_type=int, **kwargs):
        super(IntOption, self).__init__(value_type=value_type, **kwargs)
    
class FloatOption(Option):

    def __init__(self, int_pow=0, value_type=float, **kwargs):
        self.int_pow = int_pow
        super(FloatOption, self).__init__(value_type=value_type, **kwargs)
    
    def to_int(self, value):
        return int(value*math.pow(10, self.int_pow))

class JsonOption(Option):
    def clean(self, value):
        return json.loads(value)
    
class CsvOption(Option):
    def clean(self, value):
        return [s.strip() for s in value.split(',')]

class BaseRelativePathOption(Option):
    """Represents a relative file path, resolved to an absolute one when the holder is instanciated"""
    
    def pop_val_from_dict(self, d):
        value = super(BaseRelativePathOption, self).pop_val_from_dict(d)
        return self.get_abs_path(value)

    def get_abs_path(self, value):
        raise NotImplementedError()

class RelativePathOption(BaseRelativePathOption):
    
    def __init__(self, basepath, **kwargs):
        self.basepath = basepath
        super(RelativePathOption, self).__init__(**kwargs)
    
    def get_abs_path(self, value):
        if not os.path.isabs(value):
            value = os.path.join(self.basepath, value)
        return value
    
class DataFileOption(BaseRelativePathOption):
    """Represents a data file path that can be relative to the current data directory"""
    
    def get_abs_path(self, value):
        if not os.path.isabs(value):
            from fmanalyser.conf import settings
            value = os.path.join(settings.data_dir, value)
        return value

class CarrierFrequencyOption(IntOption):
    
    def __init__(self, **kwargs):
        kwargs.setdefault('null_value', 0)
        super(CarrierFrequencyOption, self).__init__(**kwargs)
    
    def clean(self, value):
        return parse_carrier_frequency(value)
    
    def unclean(self, value):
        if value is not None:
            value = float(value)/1000
        return super(CarrierFrequencyOption, self).unclean(value)

class kHzOption(FloatOption):
    """Represents a frequency value displayed in kHz and stored in Hz"""
    
    def __init__(self, int_pow=3, null_value=-1, **kwargs):
        super(kHzOption, self).__init__(int_pow=int_pow, null_value=null_value, **kwargs)
    
    def clean(self, value):
        return parse_deviation_level(value)
    
