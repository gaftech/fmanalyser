# -*- coding: utf-8 -*-

from . import validators, descriptors, Variable
from ..client import RDS_MODE, MEASURING_MODE, STEREO_MODE, tasks
from ..exceptions import ValidationException
from ..utils.conf import options, OptionHolder, DeclarativeOptionMetaclass
from ..utils.log import Loggable
import threading

class ChannelBase(DeclarativeOptionMetaclass):
    
    def __new__(cls, name, bases, attrs):
                
        new_attrs = attrs.copy()
        
        _descriptors = {}
        
        for k, v in attrs.items():
            if isinstance(v, descriptors.ValueDescriptor):
                _descriptors[k] = new_attrs.pop(k)
                
        new_class = super(ChannelBase, cls).__new__(
            cls, name, bases, new_attrs)
        
        setattr(new_class, '_descriptors', _descriptors)
        
        for k, descriptor in _descriptors.items():
            descriptor.contribute_to_class(new_class, k)
                
        return new_class
        
class BaseChannel(Loggable, OptionHolder):
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

        self._variables = {}
        
        self.name = name
        
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
        super(BaseChannel, self).__init__(**kwargs)

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

    def iter_variables(self):
        return self._variables.itervalues()
    
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
    
    def get_variable(self, key):
        return self._variables[key]
    
    def get_variables_by_mode(self, **filters):
        variables = {}
        for variable in self.filter_variables(**filters):
            mode = variable.device_mode
            variables.setdefault(mode, []).append(variable)
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
        validator = validators.factory(validators.StrictIntValidator,
            enabled = True,
            ref = options.CarrierFrequencyOption()),
        device_mode = None,
                                                       
    )
    
    rf = descriptors.ValueDescriptor(
        short_key = 'l',
        unit = u'dBµV',
        validator = validators.factory(validators.RelativeFloatThresholdValidator,
                                       high=6, low=6)                        
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
    
    rds_lock_time = options.FloatOption(default=5)
    mes_lock_time = options.FloatOption(default=5)
    stereo_lock_time = options.FloatOption(default=5)
    
    def __str__(self):
        return self._variables['frequency'].render()
    

    
    def set_frequency(self, freq):
#        current = self._variables['frequency'].validator.ref
        self._variables['frequency'].validator.ref = freq
        
    def tune(self, client):
        freq = self._variables['frequency'].validator.ref
        if freq:
            client.tune(freq)
    
    def enqueue_updates(self, worker):
        task = None
        
        worker.acquire()
        try:
            
#            # Tuning to the right frequency, if specified
            task = worker.enqueue(self.tune)
                
            variables = self.get_variables_by_mode(enabled=True)            

            # None-mode Measurements
            if None in variables:
                for var in variables[None]:
                    task = worker.enqueue(var.update)
                
            # RDS measurements
            if RDS_MODE in variables:
                # Locking for a while on rds mode
                self._lock_mode(worker, RDS_MODE)
                # Retrieving measurements
                task = worker.enqueue(self.update_rds_variables)
                
            # Stereo mode measurements
            if STEREO_MODE in variables:
                self._lock_mode(worker, STEREO_MODE)
                for var in variables[STEREO_MODE]:
                    task = worker.enqueue(var.update)
            
            # Measuring mode measurements
            if MEASURING_MODE in variables:
                self._lock_mode(worker, MEASURING_MODE)
                for var in variables[MEASURING_MODE]:
                    task = worker.enqueue(var.update)                

        finally:
            worker.release()
            
        return task
        
    def _lock_mode(self, worker, mode):
        timeout = getattr(self, '%s_lock_time' % mode)
        self.logger.debug('enqueueing %s mode lock for %s s' % (mode, timeout))
        worker.enqueue('set_mode', mode)
        return worker.enqueue_task(tasks.Sleep(timeout))
    
    def update(self, client):
        """Update all enabled variables probing the device associated to `client`"""
        # TODO: Here we should check the device frequency
        for variable in self._variables.values():
            variable.update(client)

    def update_rds_variables(self, client, **filters):
        filters['device_mode'] = RDS_MODE
        filters.setdefault('enabled', True)
        variables = self.filter_variables(**filters)
        self._update_rds_data(client, variables)
        
    def _update_rds_data(self, client, variables):
        for k, v in client.get_rds_data().items():
            if k in variables:
                variables[k].set_value(v)
        
def create_config_channels(config):
    """Creates the :class:`Channel` instances described by the `config` object.
    
    :param config: a :class:`fmanalyser.utils.conf.BaseConfig` instance
    :return list: created channels
    """
    channels = []
    for name, channel_config in config.iter_subsection_items('channel'):
        channels.append(Channel(name, **channel_config.values))
    return channels
    
    