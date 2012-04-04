# -*- coding: utf-8 -*-
from fmanalyser.test import TestCase
from fmanalyser.conf import Config
from fmanalyser.values.channel import Channel

class ChannelConfigTest(TestCase):
    
    def setUp(self):
        super(ChannelConfigTest, self).setUp()
        self.ini = """
[channel:testchannel]
frequency = 108.1
PILOT_HIGH = 4 ; We want to be case insensitive
rds_high = 1
"""
#        self.default_conf = Config()
        self.default_channel = Channel(88000)
        self.test_conf = Config(raw_data=self.ini)
        self.test_channel = Channel.from_config(self.test_conf, 'testchannel')
    
    def test_default_values(self):
        self.assertEqual(self.default_channel.get_validator('pilot').high, 0.5)
        self.assertEqual(self.default_channel.get_validator('rds').high, 0.5)
        self.assertEqual(self.test_channel.get_validator('rds').high, 1)
        
    def test_upper_case_key(self):
        self.assertEqual(self.test_channel.get_validator('pilot').high, 4)