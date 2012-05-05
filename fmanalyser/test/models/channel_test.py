# -*- coding: utf-8 -*-
from .. import TestCase
from ...conf import Config
from ...models.channel import Channel, create_config_channels

class ChannelVariablesTest(TestCase):
    
    def test_validator_option_order(self):
        channel = Channel()
        validator = channel._descriptors['rds'].validator
        options = validator._options
        self.assertSequenceEqual(options.keys(),
            ['enabled', 'ref', 'high', 'low']
        )
    

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
        self.default_channel = Channel(frequency=88000)
        self.test_conf = Config(raw_data=self.ini)
        channels = create_config_channels(config=self.test_conf)
        self.assertEqual(len(channels), 1)
        self.assertEqual(channels[0].name, 'testchannel')
        self.test_channel = channels[0]
    
    def test_default_values(self):
        self.assertEqual(self.default_channel.get_validator('frequency').ref, 88000)
        self.assertEqual(self.default_channel.get_validator('pilot').high, 0.5)
        self.assertEqual(self.default_channel.get_validator('rds').high, 0.5)
    
    def test_values_from_ini(self):
        self.assertEqual(self.test_channel.get_validator('frequency').ref, 108100)
        self.assertEqual(self.test_channel.get_validator('pilot').low, 0.5)
        self.assertEqual(self.test_channel.get_validator('pilot').high, 4)
        self.assertEqual(self.test_channel.get_validator('rds').high, 1)
        
    def test_upper_case_key(self):
        self.assertEqual(self.test_channel.get_validator('pilot').high, 4)