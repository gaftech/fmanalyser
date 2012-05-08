# -*- coding: utf-8 -*-
from copy import copy
from fmanalyser.conf import options, OptionHolder
from fmanalyser.conf.declarative import DeclarativeOptionMetaclass
from fmanalyser.test import TestCase
import os

class TestOptionHolder(object):
    __metaclass__ = DeclarativeOptionMetaclass
    
    opt1 = options.BooleanOption()
    opt2 = options.FloatOption(required=True)

class AnotherHolder(TestOptionHolder):
    
    opt2 = options.Option(required=False)
    opt3 = options.CarrierFrequencyOption()
    opt4 = options.IntOption(default=444)
    
    _options = {
        'opt4': options.BooleanOption(),
        'opt5': options.Option(),
    }

class FileOptionHolder(OptionHolder):
    path = options.RelativePathOption(basepath="/tmp")
    datapath = options.DataFileOption()
    
class DeclarativeOptionsTest(TestCase):
    
    def test_option_count(self):
        self.assertEqual(len(TestOptionHolder._options), 2)
        self.assertEqual(len(AnotherHolder._options), 5)
    
    def test_inheritance_overriding(self):
        self.assertFalse(AnotherHolder._options['opt2'].required)
    
    def test_declaration_mode_priority(self):
        self.assertIsInstance(AnotherHolder._options['opt4'], options.IntOption)
    


class OptionTest(TestCase):
    
    def test_clone_option(self):
        original = options.FloatOption(default=123)
        clone = original.clone()
        clone.default = 456
        self.assertEqual(original.default, 123)
        
    def test_clone_owned_option(self):
        original = AnotherHolder._options['opt1']
        self.assertIs(original._holder, AnotherHolder)
        clone = original.clone()
        self.assertIsNone(clone._holder)
        
    def test_relative_path_option(self):
        holder = FileOptionHolder(path='test.txt',
                                  datapath='somedir/data.dat')
        self.assertEqual(holder.path, '/tmp/test.txt')
        self.assertEqual(holder.datapath,
                         os.path.expanduser('~/.fmanalyser/var/somedir/data.dat'))

