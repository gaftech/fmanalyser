# -*- coding: utf-8 -*-
from fmanalyser import test
from fmanalyser.conf import options, BaseConfigSection, BaseConfig, \
    IniFileSource
from fmanalyser.device.controllers.base import DeviceController
from fmanalyser.plugins import core_plugins
from fmanalyser.plugins.base import Plugin
import logging
import os
from fmanalyser.models.channel import Channel
from fmanalyser.models.bandscan import Bandscan

DEFAULT_CONF_FILE = os.path.expanduser(os.path.join('~', '.fmanalyser', 'etc', 'conf.ini'))

class GlobalConfigSection(BaseConfigSection):
    
    basename = 'global'
    
    loglevel = options.IntOption(default=logging.WARNING,
        ini_help="Logging level as defined by the python logging module.\n"
                    "(DEBUG=10, INFO=20, WARNING=30, CRITICAL=50).")
    data_dir = options.Option(default=os.path.join('~', '.fmanalyser', 'var'))
    watcher_sleep_time = options.FloatOption(default=0.1)
    
    ini_help = \
"""Software global parameters.
These can be overriden by command line options."""

def _make_section_classes():

    section_classes = [
        GlobalConfigSection,
        DeviceController.config_section_factory(),
        Channel.config_section_factory(),
        Bandscan.config_section_factory(),
    ]
    
    for cls in core_plugins:
        section_classes.append(cls.config_section_factory())
    
    section_classes.extend([
        Plugin.config_section_factory(),
        test.ConfigSection,
    ])
    
    return section_classes

class Config(BaseConfig):
    section_classes = _make_section_classes()

#: The global configuration access point
fmconfig = Config(source=IniFileSource(DEFAULT_CONF_FILE))

