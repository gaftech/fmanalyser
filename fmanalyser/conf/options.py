# -*- coding: utf-8 -*-
from ..exceptions import InvalidOption, MissingOption
from ..utils.parse import parse_carrier_frequency, parse_deviation_level
import math
import os

class BaseOption(object):
    _creation_counter = 0
    value_type = lambda x: x
#    #: the value that will be used to replace `None` when exporting
#    #: a value to a format that doesn't support `None`
    null_value = None

    _ct_opts = ('value_type', 'null_value')

    def __init__(self, default=None, required=False, choices=None, ini_help='', **kwargs):
        
        self._creation_order = Option._creation_counter
        Option._creation_counter += 1
        
        self.default = default
        self._required = required
        self.choices = choices
        self.ini_help = ini_help
        for k in self._ct_opts:
            if k in kwargs:
                setattr(self, k, kwargs.pop(k))
        if len(kwargs):
            raise ValueError('Unexpected option(s) : %s' % ', '.join(kwargs.keys()))
        
        self._holder = None
        self._attname = None

    def __str__(self):
        return '%s: %s.%s' % (self.__class__.__name__, 
                              getattr(self._holder, '__name__', self._holder),
                              self.attname)

    def __copy__(self):
        return self.clone()
    
    def clone(self, **kwargs):
        defaults = dict(
            default = self.default,
            required = self._required,
            choices = self.choices,
            ini_help = self.ini_help,
        )
        for k in self._ct_opts:
            kwargs[k] = getattr(self, k)
        defaults.update(kwargs)
        other = self.__class__(**defaults)
        return other
    
#    def _get_default(self):
#        if callable(self._default):
#            return self._default()
#        return self._default
#
#    def _set_default(self, value):
#        self._default = value
#    
#    default = property(_get_default, _set_default)
    
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
        return d.pop(self.attname, self.default)

#    def contribute_to_instance(self, instance, attname, kwargs):
#        """Method called, for each option, when an option holder is instantiated.
#        """
#        if self.required and attname not in kwargs:
#            raise MissingOption(attname)
#        assert not hasattr(instance, attname)
#        setattr(instance, attname, kwargs.pop(attname, self.default))

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
    value_type = str

class BooleanOption(Option):
    value_type = bool
    true_values = set((True, 1, '1', 'on', 'true'))
    false_values = set((False, 0, '0', 'off', 'false'))
    
    def __init__(self, **kwargs):
        kwargs.setdefault('default', False)
        super(BooleanOption, self).__init__(**kwargs)
    
    def clean(self, value):
        if isinstance(value, basestring):
            value = value.lower()
        if value in self.true_values:
            return True
        if value in self.false_values:
            return False
        raise InvalidOption("%s: %s can't be converted to a boolean" % (self, value))
    
class IntOption(Option):
    value_type = int
    
class FloatOption(Option):
    value_type = float
    int_pow = 0
    
    _ct_opts = Option._ct_opts + ('int_pow',)

    
    def to_int(self, value):
        return int(value*math.pow(10, self.int_pow))

class BaseRelativePathOption(Option):
    """Represents a relative file path, resolved to an absolute one when the holder is instanciated"""
    
    def pop_val_from_dict(self, d):
        value = super(BaseRelativePathOption, self).pop_val_from_dict(d)
        return self.get_abs_path(value)

    def get_abs_path(self, value):
        if not os.path.isabs(value):
            value = os.path.join(self.basepath, value)
        return value

class RelativePathOption(BaseRelativePathOption):
    _ct_opts = Option._ct_opts + ('basepath',)
    
class DataFileOption(BaseRelativePathOption):
    """Represents a data file path that can be relative to the current data directory"""
    
    @property
    def basepath(self):
        from .fmconfig import fmconfig
        return os.path.expanduser(fmconfig['global']['data_dir'])


class CarrierFrequencyOption(IntOption):
    
    null_value = 0
    
    def clean(self, value):
        return parse_carrier_frequency(value)
    
    def unclean(self, value):
        if value is not None:
            value = float(value)/1000
        return super(CarrierFrequencyOption, self).unclean(value)

class kHzOption(FloatOption):
    """Represents a frequency value displayed in kHz and stored in Hz"""
    
    int_pow = 3
    null_value = -1
    
    def clean(self, value):
        return parse_deviation_level(value)
    
