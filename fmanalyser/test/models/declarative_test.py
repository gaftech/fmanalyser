# -*- coding: utf-8 -*-
"""Tests our black magic stuffs about declarative option and validators metaclasses"""
from .. import TestCase
from ...models import validators
from ...models.channel import BaseChannel
from ...models.descriptors import ValueDescriptor
from ...conf import options

class Validator1(validators.Validator):
    
    opt1 = options.BooleanOption(default=True)
    opt2 = options.BooleanOption(default=False)
    opt3 = options.IntOption(default=1)

class TestChannelClass(BaseChannel):
    
    value1 = ValueDescriptor(
        validator = Validator1,
    )
    
    value2 = ValueDescriptor(
        validator = validators.factory(Validator1, opt3=2)
    )
    
class ChannelConfigTest(TestCase):
    
    def setUp(self):
        super(ChannelConfigTest, self).setUp()
        self.ChannelConfig = TestChannelClass.config_section_factory()

    def test_option_clone(self):
        self.assertIsNot(
            TestChannelClass._descriptors['value1'].validator._options['opt3'],
            TestChannelClass._descriptors['value2'].validator._options['opt3'],
        )
        
   
    def test_default_values(self):
        self.assertEqual(self.ChannelConfig._options['value1_opt3'].default, 1)
        self.assertEqual(self.ChannelConfig._options['value2_opt3'].default, 2)
#    
    


class DeclarativeValidatorTest(TestCase):
    """Here we test the validator class on its own."""
    
    def test_option_count(self):
        self.assertEqual(len(Validator1._options), 5)
        
    def test_option_attnames(self):
        self.assertEqual(Validator1._options['opt1'].attname, 'opt1')
        self.assertEqual(Validator1._options['opt2'].attname, 'opt2')
    
    

    

    


