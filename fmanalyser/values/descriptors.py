# -*- coding: utf-8 -*-
from . import validators, NOTSET

class ValueDescriptor(object):
    
    def __init__(self,
                 verbose_name = None,
                 short_key = None,
                 unit = None,
                 readable = True,
                 writable = False,
                 validator = validators.Validator,
            ):
        """
        ..todo: Provide default values for readable/writable. Maybe based on client class introspection.
        """


        # default values
        
        # values checks
        assert issubclass(validator, validators.Validator)
        
        # private attributes from arguments
        self._verbose_name = verbose_name
        
        # public attributes from arguments
        self.short_key = short_key
        self.unit = unit
        self.readable = readable
        self.writable = writable
        self.validator = validator

        # other private attributes 
        self._key = None
        
    def __str__(self):
        s = self.verbose_name
        if self.unit is not None:
            s = '%s (%s)' % (s, self.unit)
        return s
    
    def _get_key(self):
        assert self._key is not None
        return self._key
    
    def _set_key(self, value):
        assert self._key is None and value is not None
        self._key = value
    
    key = property(_get_key, _set_key)
    
    
    @property
    def verbose_name(self):
        if self._verbose_name is None:
            return self._key
        return self._verbose_name
    
    def contribute_to_class(self, holder_cls, name):
        self.key = name
    
    def read(self, client):
        assert self.readable
        return client.read(self.key)
    
    def write(self, client, value):
        assert self.writable
        return client.write(self.key, value)
    
    def format_value(self, value):
        if self.unit is None:
            return str(value)
        else:
            return '%s %s' % (value, self.unit)
    
class CarrierFrequencyDescriptor(ValueDescriptor):
    """Represents a value stored as an integer and displayed as a floating point number"""
    
    def __init__(self, factor=1000, **kwargs):
        """
        :param number factor:
            stored value is divided by `factor` to get the display value 
        """
        self.factor = factor
        super(CarrierFrequencyDescriptor, self).__init__(**kwargs)
    
    def format_value(self, value):
        value = float(value) / self.factor
        return super(CarrierFrequencyDescriptor, self).format_value(value)
    
    
    
    
    