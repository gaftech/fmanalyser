# -*- coding: utf-8 -*-

from . import validators, descriptors, Variable
from ..exceptions import ValidationException
from ..conf import options, OptionHolder, DeclarativeOptionMetaclass
from ..utils.datastructures.ordereddict import OrderedDict
from ..utils.log import Loggable
import threading
from fmanalyser.conf.holder import EnableableSectionOptionHolder

class ChannelBase(DeclarativeOptionMetaclass):
    
    def __new__(cls, name, bases, attrs):
                
        new_attrs = attrs.copy()
        
#        _descriptors = OrderedDict()
        _descriptor_items = []
        for k, v in attrs.items():
            if isinstance(v, descriptors.ValueDescriptor):
#                _descriptors[k] = new_attrs.pop(k)
                _descriptor_items.append((k, new_attrs.pop(k)))
        
        _descriptor_items.sort(cmp=lambda x,y: cmp(x[1].creation_order, y[1].creation_order))
          
        new_class = super(ChannelBase, cls).__new__(
            cls, name, bases, new_attrs)
        
        new_class._descriptors = OrderedDict(_descriptor_items)
        
        for k, descriptor in new_class._descriptors.items():
            descriptor.contribute_to_class(new_class, k)
                
        return new_class
        
class BaseChannel(Loggable, EnableableSectionOptionHolder):
    """Base class for channel.
    
    At the moment, the only reason to have a separate base class for `Channel` is testing purpose
    
    """

    __metaclass__ = ChannelBase
    
    config_section_name = 'channel'

    @classmethod
    def get_class_descriptors(cls):
        return cls._descriptors.values()

    @classmethod
    def config_section_factory(cls):
        attrs = {}
        for k, descriptor in cls._descriptors.items():
            for option_key, _option in descriptor.validator._options.items():
                option = _option.clone()
                if option_key == 'ref':
                    fullkey = k
                else:
                    fullkey = '%s_%s' % (k, option_key)
                assert fullkey not in attrs
                attrs[fullkey] = option
        return super(BaseChannel, cls).config_section_factory(**attrs)

    def __init__(self, name=None, **kwargs):

        self._variables = OrderedDict()
        
        # Create variables from descriptors
        for k, descriptor in self._descriptors.items():
            Validator = descriptor.validator
            validator_kwargs = {}
            for option_key in Validator._options:
                if option_key == 'ref':
                    fullkey = k
                else:
                    fullkey = '%s_%s' % (k, option_key)
                if fullkey in kwargs:
                    validator_kwargs[option_key] = kwargs.pop(fullkey)
            validator = Validator(**validator_kwargs)
            self._variables[k] = Variable(owner = self,
                                          descriptor = descriptor,
                                          validator = validator)
        
        # Handle options
        super(BaseChannel, self).__init__(name=name, **kwargs)

        self._lock = threading.Lock()
    
    def __getattr__(self, name):
        if name not in self._variables:
            raise AttributeError(name)
        return self._variables[name].get_value()
    
    def __setattr__(self, name, value):
        if name != '_variables' and name in self._variables:
            self._variables[name].set_value(value)
        else:
            super(BaseChannel, self).__setattr__(name, value)

    def get_variable(self, key):
        return self._variables[key]

    def iter_variables(self):
        return self._variables.iteritems()
    
    def get_variables(self):
        return self._variables.values()
    
    def filter_variables(self, enabled=None, device_mode=None):
        variables = []
        for var in self._variables.values():
            if enabled is not None and var.enabled != enabled:
                continue
            if device_mode is not None and var.device_mode != device_mode:
                continue
            variables.append(var)
        return variables
    
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

class Channel(BaseChannel):
    
    frequency = descriptors.CarrierFrequencyDescriptor(
        short_key = 'f',
        unit = 'MHz',
        validator = validators.factory(validators.base.StrictIntValidator,
            name = 'FrequencyValidator',
            enabled = True,
            ref = options.CarrierFrequencyOption(
                ini_help="Channel frequency as a floating point number in MHz\n"
                         "If not given, the current device frequency will be used.")),
                                                       
    )
    
    rf = descriptors.ValueDescriptor(
        short_key = 'l',
        unit = u'dBµV',
        validator_class = validators.RfLevelValidator,
        validator_options = dict(high=6, low=6)                        
    )
    
    quality = descriptors.ValueDescriptor(
        short_key = 'q',
        validator_class = validators.QualityValidator,
        validator_options = dict(ref=5)
    )
    
    pilot = descriptors.ValueDescriptor(
        verbose_name = 'pilot subcarrier deviation',
        short_key = 'p',
        unit = 'kHz',
        validator_class = validators.DeviationLevelValidator,
        validator_options = dict(ref = 6, high = 0.5, low = 0.5)                                            
    )
    
    rds = descriptors.ValueDescriptor(
        verbose_name = 'rds subcarrier deviation',
        short_key = 'r',
        unit = 'kHz',
        validator_class = validators.DeviationLevelValidator,
        validator_options = dict(ref = 4, high = 0.5, low = 0.5)
    )
    
    rds_data_enabled = options.BooleanOption(default=None,
        ini_help = "Shortcut to enable/disable all RDS data variables",
    )
    
    device = options.Option(
        ini_help = "Configured name of the device used to update this channel.",
    )
    
    def __str__(self):
        return self._variables['frequency'].render()
    
    def get_frequency(self):
        return self._variables['frequency'].validator.ref
    
    def set_frequency(self, freq):
        self._variables['frequency'].validator.ref = freq

        
#def create_config_channels(config):
#    """Creates the :class:`Channel` instances described by the `config` object.
#    
#    :param config: a :class:`fmanalyser.utils.conf.BaseConfig` instance
#    :return list: created channels
#    """
#    channels = []
#    for name, channel_config in config.iter_subsection_items('channel'):
#        channels.append(Channel(name, **channel_config.values))
#    return channels
    
    