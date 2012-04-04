# -*- coding: utf-8 -*-
from .utils.conf import ConfigSection, BaseConfig, options
from .values import channel
import os.path

CONF_DIR = os.path.expanduser('~/.fmanalyser/')
CONF_FILE = os.path.join(CONF_DIR, 'conf.ini')

class TestConfigSection(ConfigSection):
    section = 'test'
    live_tests = options.BooleanOption(default=True)

ChannelConfigSection = channel.config_section_factory()

class Config(BaseConfig):
    
    inifiles = [CONF_FILE]
    
    sections = (
        TestConfigSection,
        ChannelConfigSection,
    )
