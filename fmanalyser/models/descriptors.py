# -*- coding: utf-8 -*-
from . import validators
from ..utils.datastructures import NOTSET
from ..client import MEASURING_MODE

class ValueDescriptor(object):
    """Describes a variable that will be attached to the :class:`Channel` class.
    """    
    def __init__(self,
                 verbose_name = None,
                 short_key = None,
                 unit = None,
                 device_mode = MEASURING_MODE,
                 validator = validators.Validator,
            ):

        # default values
        
        # values checks
        assert issubclass(validator, validators.Validator)
        
        # private attributes from arguments
        self._verbose_name = verbose_name
        self._device_mode = device_mode
        
        # public attributes from arguments
        self.short_key = short_key
        self.unit = unit
        self.validator = validator

        # other private attributes 
        self._holder = None
        self._key = None
        
    def __str__(self):
        s = self.verbose_name
        if self.unit is not None:
            s = '%s (%s)' % (s, self.unit)
        return s
    
    def contribute_to_class(self, holder_cls, name):
        assert self._holder is None
        self._holder = holder_cls
        self._key = name
    
    @property
    def key(self):
        return self._key
    
#    def _get_key(self):
#        assert self._key is not None
#        return self._key
#    
#    def _set_key(self, value):
#        assert self._key is None and value is not None
#        self._key = value
#    
#    key = property(_get_key, _set_key)
    
    @property
    def verbose_name(self):
        if self._verbose_name is None:
            return self._key
        return self._verbose_name
    
    @property
    def device_mode(self):
        return self._device_mode
    
    def read(self, client):
        return client.read(self.key)

    def render_value(self, value):
        if self.unit:
            return '%s %s' % (value, self.unit)
        else:
            return str(value)
    
class CarrierFrequencyDescriptor(ValueDescriptor):
    """Represents a value stored as an integer and displayed as a floating point number"""
    
    def __init__(self, factor=1000, **kwargs):
        """
        :param number factor:
            stored value is divided by `factor` to get the display value 
        """
        self.factor = factor
        super(CarrierFrequencyDescriptor, self).__init__(**kwargs)
    
    def render_value(self, value):
        if not value is NOTSET:
            value = float(value) / self.factor
        return super(CarrierFrequencyDescriptor, self).render_value(value)
    
    
    
    
    