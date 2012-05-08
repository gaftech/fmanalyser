# -*- coding: utf-8 -*-
from . import BaseConfig, BaseConfigSection, options
from ..client.device import P175
from ..models.channel import Channel
from ..models.bandscan import Bandscan
from .. import test
import logging
import os
from fmanalyser.plugins import core_plugins
from fmanalyser.plugins.base import Plugin

DEFAULT_CONF_FILE = os.path.expanduser(os.path.join('~', '.fmanalyser', 'etc', 'conf.ini'))

class GlobalConfigSection(BaseConfigSection):
    
    basename = 'global'
    
    loglevel = options.IntOption(default=logging.WARNING,
        ini_help="Logging level as defined by the python logging module.\n"
                    "(DEBUG=10, INFO=20, WARNING=30, CRITICAL=50).")
    data_dir = options.Option(default=os.path.join('~', '.fmanalyser', 'var'))
    
    ini_help = \
"""Software global parameters.
These can be overriden by command line options."""

section_classes = [
    GlobalConfigSection,
    P175.config_section_factory(),
    Channel.config_section_factory(),
    Bandscan.config_section_factory(),
]

for cls in core_plugins:
    section_classes.append(cls.config_section_factory())

section_classes.extend([
    Plugin.config_section_factory(),
    test.ConfigSection,
])

class Config(BaseConfig):
    section_classes = section_classes

#: The global configuration access point
fmconfig = Config(DEFAULT_CONF_FILE)

