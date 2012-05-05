# -*- coding: utf-8 -*-
"""A collection of classes that define a channel expected measurements.
"""
from ...exceptions import ValidationException
from ...utils.conf import options, OptionHolder

class Validator(OptionHolder):

    enabled = options.BooleanOption(default=None)
    ref = options.Option(required=False)
    
    def __init__(self, **kwargs):
        if kwargs.get('enabled') is None:
            kwargs['enabled'] = kwargs.get('ref') is not None
        
        super(Validator, self).__init__(**kwargs)
    
    def clean(self, raw_value, option_key='ref'):
        option = self._options[option_key]
        return option.clean(raw_value)
    
    def is_valid(self, value):
        try:
            self.validate(value)
        except ValidationException:
            return False
        return True

    def validate(self, value):
        if self.enabled:
            self.validate_value(value)

    def validate_value(self, value):
        pass

class StrictValidatorMixin(object):
    def validate_value(self, value):
        if value != self.ref:
            raise ValidationException('%s != %s' % (value, self.ref))

class ThresholdValidatorMixin(object):
    def validate_value(self, value):
        if value < self.low or value > self.high:
            raise ValidationException('%s out of bound (%s - %s)' % (value, self.low, self.high))

class RelativeThresholdValidatorMixin(object):
    def validate_value(self, value):
        if value < self.ref - self.low or value > self.ref + self.high:
            raise ValidationException(u'%s out of bound (%s +%s/-%s)' % (value, self.ref, self.high, self.low)) 

class LowThresholdValidatorMixin(object):
    def validate_value(self, value):
        if value < self.ref:
            raise ValidationException('%s less than %s' % (value, self.ref))
        
class BaseIntValidator(Validator):
    ref = options.IntOption()

class BaseIntThresholdValidator(Validator):
    ref = options.IntOption()
    high = options.IntOption()
    low = options.IntOption()

class BaseFloatThresholdValidator(Validator):
    ref = options.FloatOption()
    high = options.FloatOption()
    low = options.FloatOption()

class StrictIntValidator(StrictValidatorMixin, BaseIntValidator):
    pass

class RelativeFloatThresholdValidator(RelativeThresholdValidatorMixin, BaseFloatThresholdValidator):
    pass

class RelativeIntThresholdValidator(RelativeThresholdValidatorMixin, BaseIntThresholdValidator):
    pass

class IntLowThresholdValidator(LowThresholdValidatorMixin, BaseIntValidator):
    pass

def factory(*bases, **kwargs):
    name = kwargs.pop('name', 'Validator')
    extra_options = dict((k,kwargs.pop(k)) for k, v in kwargs.items()
                         if isinstance(v, options.Option))
    if len(bases):
        bases = tuple(bases)
    else:
        bases = (Validator,)
    NewValidator = type(name, bases, {'_options': extra_options})
    for k, v in kwargs.iteritems():
        if k not in NewValidator._options:
            raise ValueError(u"Can't set default value for unknown option %s" % k)
        NewValidator._options[k].default = v
    return NewValidator
    

        
    
    
    
    
    
    
    
    
    
    
    