# -*- coding: utf-8 -*-
from . import base
from .base import factory, Validator
from ...utils.conf import options

class RfLevelValidator(base.RelativeThresholdValidatorMixin, Validator):
    ref = options.IntOption(null_value=-1)
    high = options.IntOption(null_value=-1)
    low = options.IntOption(null_value=-1)

class QualityValidator(base.IntLowThresholdValidator):
    ref = options.IntOption(null_value=-1)

class DeviationLevelValidator(base.RelativeThresholdValidatorMixin, Validator):
    ref = options.kHzOption()
    high = options.kHzOption()
    low = options.kHzOption()
    
    