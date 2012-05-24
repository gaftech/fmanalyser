# -*- coding: utf-8 -*-
from . import validators
import inspect

class ValueDescriptor(object):
    """Describes a variable that will be attached to the :class:`Channel` class.
    """
    
    creation_counter = 0
    
    def __init__(self,
                 verbose_name = None,
                 short_key = None,
                 unit = None,
                 validator = None,
                 validator_class = validators.Validator,
                 validator_options = (),
            ):

        # private attributes 
        self._holder = None
        self._key = None
        self._validator = validator

        # class member ordering
        self.creation_order = ValueDescriptor.creation_counter
        ValueDescriptor.creation_counter += 1

        # default values
        
        # private attributes from arguments
        self._verbose_name = verbose_name
        if inspect.isclass(validator_class):
            self._validator_bases = (validator_class,)
        else:
            self._validator_bases = validator_class
        self._validator_opts = dict(validator_options)
        
        # public attributes from arguments
        self.short_key = short_key
        self.unit = unit
        
        # values checks
        assert self._validator is None or issubclass(self._validator, validators.Validator)
        
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
    
    @property
    def verbose_name(self):
        if self._verbose_name is None:
            return self._key
        return self._verbose_name
    
    @property
    def validator(self):
        if self._validator is None:
            name = 'Validator'
            if self._key is not None:
                name = '%s%s' % (self._key.title(), name)
            kwargs = {'name': name}
            kwargs.update(self._validator_opts)
            self._validator = validators.factory(*self._validator_bases, **kwargs)
        return self._validator
    
    @property
    def device_mode(self):
        return self._device_mode
    
    def read(self, client):
        return client.read(self.key)

    def render(self, value):
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
    
    def render(self, value):
        if value:
            value = float(value) / self.factor
        return super(CarrierFrequencyDescriptor, self).render(value)
    
    
    
    
    