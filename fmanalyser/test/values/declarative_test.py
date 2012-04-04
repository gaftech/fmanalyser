# -*- coding: utf-8 -*-
"""Tests our black magic stuffs about declarative option and validators metaclasses"""
from fmanalyser.test import TestCase
from fmanalyser.utils.conf import options
from fmanalyser.values import validators
from fmanalyser.values.channel import ChannelBase, config_section_factory
from fmanalyser.values.descriptors import ValueDescriptor

class Validator1(validators.Validator):
    
    opt1 = options.BooleanOption(default=True)
    opt2 = options.BooleanOption(default=False)
    opt3 = options.IntOption(default=1)

class Channel(object):
    __metaclass__ = ChannelBase
    
    value1 = ValueDescriptor(
        validator = Validator1,
    )
    
    value2 = ValueDescriptor(
        validator = validators.factory(Validator1, opt3=2)
    )
    
class ChannelConfigTest(TestCase):
    
    def setUp(self):
        super(ChannelConfigTest, self).setUp()
        self.ChannelConfig = config_section_factory(Channel)
    
    def test_default_values(self):
        self.assertEqual(self.ChannelConfig._options['value1_opt3'].default, 1)
        self.assertEqual(self.ChannelConfig._options['value2_opt3'].default, 2)
    
    


class DeclarativeValidatorTest(TestCase):
    """Here we test the validator class on its own."""
    
    def test_name(self):
        self.assertEqual(Validator1.name, None)
    
    def test_option_count(self):
        self.assertEqual(len(Validator1._options), 4)
        
    def test_option_names(self):
        self.assertEqual(Validator1._options['opt1'].name, 'opt1')
        self.assertEqual(Validator1._options['opt2'].name, 'opt2')
    
    

    

    


