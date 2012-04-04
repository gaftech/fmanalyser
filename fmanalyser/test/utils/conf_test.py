# -*- coding: utf-8 -*-
from fmanalyser.test import TestCase
from fmanalyser.utils.conf.options import FloatOption
from copy import copy
from fmanalyser.utils.conf import options
from fmanalyser.utils.conf.declarative import DeclarativeOptionMetaclass

class OptionHolder(object):
    __metaclass__ = DeclarativeOptionMetaclass
    
    opt1 = options.BooleanOption()
    opt2 = options.FloatOption(required=True)

class AnotherHolder(OptionHolder):
    
    opt2 = options.Option(required=False)
    opt3 = options.CarrierFrequencyOption()
    opt4 = options.IntOption(default=444)
    
    _options = {
        'opt4': options.Option(),
        'opt5': options.Option(),
    }

class DeclarativeOptionsTest(TestCase):
    
    def test_option_count(self):
        self.assertEqual(len(OptionHolder._options), 2)
        self.assertEqual(len(AnotherHolder._options), 5)
    
    def test_inheritance_overriding(self):
        self.assertFalse(AnotherHolder._options['opt2'].required)
    
    def test_declaration_mode_priority(self):
        self.assertIsInstance(AnotherHolder._options['opt4'], options.IntOption)
    


class OptionTest(TestCase):
    
    def test_copy_option(self):
        original = FloatOption(default=123)
        clone = copy(original)
        clone.default = 456
        self.assertEqual(original.default, 123)
        
    
    

