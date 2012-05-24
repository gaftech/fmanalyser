# -*- coding: utf-8 -*-
"""This package provides access to user configuration files.

By default, those files are located in '~/.fmanalyser'.
They are ini-format files whose section_classes can be extended by subsections,
using the [section:subsection] syntax.
"""
from . import options
from .config import Config
from .holder import OptionHolder, EnableableOptionHolder
from .source import IniFileSource
#from fmanalyser.settings import Settings, DEFAULT_CONF_FILE

#from fmanalyser.conf import options, OptionHolder
import logging
import os
from textwrap import dedent

DEFAULT_CONF_FILE = os.path.expanduser(os.path.join('~', '.fmanalyser', 'etc', 'conf.ini'))

class GlobalConfigSection(OptionHolder):
    
    section_name = 'global'
    ini_help = dedent("""\
        Software global parameters.
        These can be overriden by command line options.""")
    
    loglevel = options.IntOption(
        default = logging.WARNING,
        ini_help = dedent("""\
            Logging level as defined by the python logging module.
            (DEBUG=10, INFO=20, WARNING=30, CRITICAL=50).""")
    )
    data_dir = options.Option(default=os.path.expanduser(os.path.join('~', '.fmanalyser', 'var')))
    watcher_sleep_time = options.FloatOption(default=0.1)
    empty_queue_timeout = options.FloatOption(default=1)

class Settings(object):
    
    def __init__(self, config):
        self._config = config
        self._section = None
    
    def __getattr__(self, key):
        if self._section is None:
            self._section = GlobalConfigSection.from_config(self._config)
        return getattr(self._section, key)


fmconfig = Config(source=IniFileSource(DEFAULT_CONF_FILE))
settings = Settings(config=fmconfig)
