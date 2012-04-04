# -*- coding: utf-8 -*-

from . import validators, descriptors, BoundValue, NOTSET
from ..exceptions import ValidationException
from ..utils.conf import options, ConfigSection
from ..utils.conf.declarative import DeclarativeOptionMetaclass
from copy import copy
from fmanalyser.client import MODE_CHOICES



class ChannelBase(DeclarativeOptionMetaclass):
    _metaname = '_descriptors'
    _option_cls = descriptors.ValueDescriptor

class Channel(object):
    __metaclass__ = ChannelBase
    
    frequency = descriptors.CarrierFrequencyDescriptor(
        short_key = 'f',
        unit = 'MHz',
        writable = True,
        validator = validators.CarrierFrequencyValidator,
    )
    
    rf = descriptors.ValueDescriptor(
        short_key = 'l',
        unit = u'dBµV',
        validator = validators.factory(validators.RelativeFloatThresholdValidator, high=6, low=6)                        
    )
    
    quality = descriptors.ValueDescriptor(
        short_key = 'q',
        validator = validators.factory(validators.SignalQualityValidator, ref=5)
    )
    
    pilot = descriptors.ValueDescriptor(
        verbose_name = 'pilot subcarrier deviation',
        short_key = 'p',
        unit = 'kHz',
        validator = validators.factory(validators.RelativeFloatThresholdValidator,
                                       ref = 6, high = 0.5, low = 0.5)                                            
    )
    
    rds = descriptors.ValueDescriptor(
        verbose_name = 'rds subcarrier deviation',
        short_key = 'r',
        unit = 'kHz',
        validator = validators.factory(validators.RelativeFloatThresholdValidator,
                                       ref = 4, high = 0.5, low = 0.5)
    )
    
    mode = descriptors.ValueDescriptor(
        verbose_name = 'measuring mode',
        readable = False,
        writable = True,
        validator = validators.factory(
            ref = options.ChoiceOption(choices = MODE_CHOICES)
        )                                          
    )
    
    @classmethod
    def iter_descriptors(cls):
        return cls._descriptors.itervalues()
    
    @classmethod
    def from_config(cls, config, name=None):
        if name is None:
            section = 'channel'
        else:
            section = 'channel:%s' % name
        kwargs = config[section].values
        return cls(**kwargs)

    def __init__(self, **kwargs):
#        frequency = kwargs.pop('frequency', None)
#        if frequency is not None:
#            assert isinstance(frequency, int)
#        self.frequency = frequency
        self.values = {}
        for k, descriptor in self._descriptors.items():
            Validator = descriptor.validator
            if Validator is None:
                validator = None
            else:
                validator_kwargs = {}
                for option_key, option in Validator._options.iteritems():
                    fullkey = '%s_%s' % (k, option.name)
                    if fullkey in kwargs:
                        validator_kwargs[option_key] = kwargs.pop(fullkey)
                validator = Validator(**validator_kwargs)
            holder = BoundValue(owner = self,
                                descriptor = descriptor,
                                validator = validator)
#            setattr(self, k, holder)
            self.values[k] = holder
        if len(kwargs):
            raise ValueError("Unexpected options : %s" % ', '.join(kwargs))
    
    def __getattr__(self, name):
        if name not in self.values:
            raise AttributeError(name)
        return self.values[name].get_value()
    
    def __setattr__(self, name, value):
        if name != 'values' and name in self.values:
            self.values[name].set_value(value)
        else:
            super(Channel, self).__setattr__(name, value)
        
    
    def __str__(self):
        f = self.frequency
        if f is NOTSET:
            f = '--'
        else:
            f = float(self.frequency)/1000
        return '%s MHz' % f
    
    def iter_values(self):
        return self.values.itervalues()
    
    def get_values(self):
        return self.values.values()
    
    def get_value(self, key):
        return self.values[key]
    
    def get_validator(self, key):
        return self.values[key].validator
    
    def is_valid(self, key, value):
        try:
            self.validate(key, value)
        except ValidationException:
            return False
        return True
    
    def validate(self, key, value):
        validator = self.get_validator(key)
        if validator is None:
            raise ValidationException('No validator for this key : %s' % key) 
        validator.validate(value)
        
    def read(self, client):
        """Update all enabled bound values probing the device associated to `client`"""
        for value in self.get_values():
            if not value.descriptor.readable:
                continue
            value.update(client)
        
def config_section_factory(base=Channel):
    attrs = {
        'section': 'channel',
#        'frequency': options.CarrierFrequencyOption(required=True),
    }
    for k, descriptor in base._descriptors.items():
        if descriptor.validator is None:
            continue
        for kk, _option in descriptor.validator._options.items():
            option = copy(_option)
            fullkey = '%s_%s' % (k, option.name)
#                option.name = '%s_%s' % (k, option.name)
            assert fullkey not in attrs
            attrs[fullkey] = option
    return  type('ChannelConfigSection', (ConfigSection,), attrs)