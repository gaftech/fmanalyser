# -*- coding: utf-8 -*-
from . import test
from .client.device import P175
from .models.channel import Channel
from .utils.conf.base import BaseConfig
from .utils.plugin import BasePlugin
import os.path

CONF_DIR = os.path.expanduser('~/.fmanalyser/')
CONF_FILE = os.path.join(CONF_DIR, 'conf.ini')



class Config(BaseConfig):
    
    section_classes = (
        P175.config_section_factory(),
        Channel.config_section_factory(),
        BasePlugin.config_section_factory(),
        test.ConfigSection,
    )

#: The global configuration access point
fmconfig = Config(CONF_FILE)

