# -*- coding: utf-8 -*-

from . import validators, descriptors, Variable
from ..client import RDS_MODE, MEASURING_MODE, STEREO_MODE, tasks
from ..exceptions import ValidationException, MissingOption
from ..utils.conf import options, ConfigSection
from ..utils.conf.declarative import DeclarativeOptionMetaclass
from ..utils.datastructures import NOTSET
import threading

class ChannelBase(DeclarativeOptionMetaclass):
    _metaname = '_descriptors'
    _option_cls = descriptors.ValueDescriptor

class Channel(object):
    __metaclass__ = ChannelBase
    
    frequency = descriptors.CarrierFrequencyDescriptor(
        short_key = 'f',
        unit = 'MHz',
        validator = validators.factory(validators.StrictIntValidator,
            ref = options.CarrierFrequencyOption())
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
    measure_lock_time = options.FloatOption(default=5)
    stereo_lock_time = options.FloatOption(default=5)
    
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
        
        # Set instance options
        for k, option in self.__class__.__dict__.items():
            if not isinstance(option, options.Option):
                continue
            if option.required and k not in kwargs:
                raise MissingOption(k)
            setattr(self, k, kwargs.pop(k, option.default))
            
            
            
        if len(kwargs):
            raise ValueError("Unexpected options : %s" % ', '.join(kwargs))

        self._lock = threading.Lock()
    
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
        return self._variables['frequency'].render()
    
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
    
    def tune(self, client):
        F = self._variables['frequency'].validator.ref
        assert F is not NOTSET
        client.tune(F)
    
    def enqueue_updates(self, worker):
        task = None
        
        worker.acquire()
        try:
            
            # Tuning to the right frequency, if specified
            if self.frequency is not NOTSET:
                task = worker.enqueue(self.tune)
                
            variables = self.get_variables_by_mode(enabled=True)            
                
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
            
            # Other measurements
            if None in variables:
                for var in variables[None]:
                    task = worker.enqueue(var.update)
        finally:
            worker.release()
            
        return task
        
    def _lock_mode(self, worker, mode):
        timeout = getattr(self, '%s_lock_time' % mode)
        self.logger.debug('locking on %s mode for %s s' % (mode, timeout))
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
        
def config_section_factory(base=Channel):
    attrs = {
        'section': 'channel',
    }
    for k, descriptor in base._descriptors.items():
        for option_key, _option in descriptor.validator._options.items():
            option = _option.clone()
            if option_key == 'ref':
                fullkey = k
            else:
                fullkey = '%s_%s' % (k, option_key)
            assert fullkey not in attrs
            attrs[fullkey] = option
    
    for k, _option in base.__dict__.items():
        if not isinstance(_option, options.Option):
            continue
        assert k not in attrs
        attrs[k] = _option.clone()
    
    return  type('ChannelConfigSection', (ConfigSection,), attrs)