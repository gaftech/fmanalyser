# -*- coding: utf-8 -*-

from . import validators, descriptors, Variable, NOTSET
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
        validator = validators.factory(validators.StrictIntValidator,
            ref = options.CarrierFrequencyOption(name=False))
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
        self._variables = {}
        for k, descriptor in self._descriptors.items():
            Validator = descriptor.validator
            validator_kwargs = {}
            for option_key, option in Validator._options.iteritems():
                if option.name:
                    fullkey = '%s_%s' % (k, option.name)
                else:
                    fullkey = k
                if fullkey in kwargs:
                    validator_kwargs[option_key] = kwargs.pop(fullkey)
            validator = Validator(**validator_kwargs)
            holder = Variable(owner = self,
                                descriptor = descriptor,
                                validator = validator)
#            setattr(self, k, holder)
            self._variables[k] = holder
        if len(kwargs):
            raise ValueError("Unexpected options : %s" % ', '.join(kwargs))
    
    def __getattr__(self, name):
        if name not in self._variables:
            raise AttributeError(name)
        return self._variables[name].get_value()
    
    def __setattr__(self, name, value):
        if name != '_variables' and name in self._variables:
            self._variables[name].set_value(value)
        else:
            super(Channel, self).__setattr__(name, value)
        
    
    def __str__(self):
        f = self.frequency
        if f is NOTSET:
            f = '--'
        else:
            f = float(self.frequency)/1000
        return '%s MHz' % f
    
    def iter_variables(self):
        return self._variables.itervalues()
    
    def get_variables(self):
        return self._variables.values()
    
    def get_variable(self, key):
        return self._variables[key]
    
    def get_validator(self, key):
        return self._variables[key].validator
    
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
        """Update all enabled variables probing the device associated to `client`"""
        for variable in self._variables.values():
            if not variable.descriptor.readable:
                continue
            variable.update(client)
        
def config_section_factory(base=Channel):
    attrs = {
        'section': 'channel',
#        'frequency': options.CarrierFrequencyOption(required=True),
    }
    for k, descriptor in base._descriptors.items():
        if descriptor.validator is None:
            continue
        for kk, _option in descriptor.validator._options.items():
            option = _option.clone()
            if option.name:
                fullkey = '%s_%s' % (k, option.name)
            else:
                fullkey = k
            assert fullkey not in attrs
            attrs[fullkey] = option
    return  type('ChannelConfigSection', (ConfigSection,), attrs)