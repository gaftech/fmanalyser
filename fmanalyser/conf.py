# -*- coding: utf-8 -*-
from . import test
from .client.device import P175
from .models.channel import Channel
from .models.bandscan import Bandscan
from .utils.conf import BaseConfig, BaseConfigSection, options
from .utils.plugin import BasePlugin
import os.path

DEFAULT_CONF_FILE = os.path.expanduser(os.path.join('~', '.fmanalyser', 'etc', 'conf.ini'))

class VERBOSITY:
    
    CRITICAL = -1
    WARNING = 0
    INFO = 1
    DEBUG = 2
    
    CHOICES = (CRITICAL, WARNING, INFO, DEBUG)

class GlobalConfigSection(BaseConfigSection):
    
    basename = 'global'
    
    verbosity = options.IntOption(choices=VERBOSITY.CHOICES)
    data_dir = options.Option(default=os.path.expanduser(os.path.join('~', '.fmanalyser', 'var')))

class Config(BaseConfig):
    
    section_classes = (
        GlobalConfigSection,
        P175.config_section_factory(),
        Channel.config_section_factory(),
        Bandscan.config_section_factory(),
        BasePlugin.config_section_factory(),
        test.ConfigSection,
    )

#: The global configuration access point
fmconfig = Config(DEFAULT_CONF_FILE)

