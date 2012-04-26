# -*- coding: utf-8 -*-
"""A collection of classes that define a channel expected measurements.
"""
from ..exceptions import ValidationException
from ..utils.conf import options, OptionHolder
from ..utils.datastructures import NOTSET

class Validator(OptionHolder):

    ref = options.Option(required=False)
    enabled = options.BooleanOption(default=None)
    
    def __init__(self, **kwargs):
        if kwargs.get('enabled') is None:
            kwargs['enabled'] = kwargs.get('ref', NOTSET) is not NOTSET
        
        super(Validator, self).__init__(**kwargs)
        
#        for k, option in self._options.iteritems():
#            if kwargs.get(k) is None and option.required:
#                raise MissingOption(k)
#            setattr(self, k, kwargs.pop(k, option.default))
#        if len(kwargs):
#            raise UnexpectedOption(', '.join(kwargs))
    
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
        pass

class StrictValidatorMixin(object):
    def validate(self, value):
        if value != self.ref:
            raise ValidationException('%s != %s' % (value, self.ref))

class ThresholdValidatorMixin(object):
    def validate(self, value):
        if value < self.low or value > self.high:
            raise ValidationException('%s out of bound (%s - %s)' % (value, self.low, self.high))

class RelativeThresholdValidatorMixin(object):
    def validate(self, value):
        if value < self.ref - self.low or value > self.ref + self.high:
            raise ValidationException(u'%s out of bound (%s +%s/-%s)' % (value, self.ref, self.high, self.low)) 
        
class BaseIntValidator(Validator):
    ref = options.IntOption()

class BaseIntThresholdValidator(Validator):
    ref = options.IntOption()
    high = options.IntOption()
    low = options.FloatOption()

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

def factory(*bases, **kwargs):
    if len(bases):
        bases = tuple(bases)
    else:
        bases = (Validator,)
    name = 'Validator'
    NewValidator = type(name, bases, {})    
    for k, _option in NewValidator._options.items():
        if k in kwargs:
            if isinstance(kwargs[k], options.Option):
                option = kwargs.pop(k)
            else:
                # argument is then the default value to apply to existing option
                option = _option.clone()
                option.default = kwargs.pop(k)
        else:
            option = _option.clone()
        NewValidator._options[k] = option
    if len(kwargs):
        raise ValueError(u"Can't set default value for missing kwargs %s" % ', '.join(kwargs))
    return NewValidator
    
class SignalQualityValidator(BaseIntValidator):
    
    def validate(self, value):
        if value < self.ref:
            raise ValidationException('Quality less than %s' % self.ref)
        
    
    
    
    
    
    
    
    
    
    
    