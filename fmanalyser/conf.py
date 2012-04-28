# -*- coding: utf-8 -*-
from . import test
from .client.device import P175
from .models.channel import Channel
from .utils.conf import BaseConfig, BaseConfigSection, options
from .utils.plugin import BasePlugin
import os.path

CONF_DIR = os.path.expanduser('~/.fmanalyser/')
CONF_FILE = os.path.join(CONF_DIR, 'conf.ini')

class VERBOSITY:
    
    CRITICAL = -1
    WARNING = 0
    INFO = 1
    DEBUG = 2
    
    CHOICES = (CRITICAL, WARNING, INFO, DEBUG)

class GlobalConfigSection(BaseConfigSection):
    
    basename = 'global'
    
    verbosity = options.IntChoiceOption(VERBOSITY.CHOICES)

class Config(BaseConfig):
    
    section_classes = (
        GlobalConfigSection,
        P175.config_section_factory(),
        Channel.config_section_factory(),
        BasePlugin.config_section_factory(),
        test.ConfigSection,
    )

#: The global configuration access point
fmconfig = Config(CONF_FILE)

