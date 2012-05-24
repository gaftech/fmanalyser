# -*- coding: utf-8 -*-
from ..utils.log import Loggable
from fmanalyser.conf import fmconfig, settings
from fmanalyser.conf.source import IniFileSource
from fmanalyser.exceptions import CommandError
from fmanalyser.utils.threads import Stoppable
import fmanalyser
import logging
import optparse
import os.path
import signal
import sys

class BaseCommand(Loggable, Stoppable):
    
    # Parser kwargs and options
    parser_cls = optparse.OptionParser
    base_options = (
        optparse.make_option(
            '-v', '--verbose', action='count', dest='verbosity',
            help='set verbose, can be repeated to increase verbosity'),
        optparse.make_option(
            '-q', '--quiet', dest='verbosity', action='store_const', const=-1,
            help='set minimal verbosity'), 
        optparse.make_option(
            '-c',  '--config-file', 
            help='config file to load (defaults to ~/.fmanalyser/conf.ini')
    )
    usage = None
    version = fmanalyser.__version__
    description = None
    epilog = None
    
    def __init__(self):
        super(BaseCommand, self).__init__()
        self.name = self.__module__.split('.').pop()
        self._worker = None
        self._device = None
    
    def __str__(self):
        return '%s version %s' % (self.name, self.version)
    
    @property
    def parser(self):
        if getattr(self, '_parser', None) is None:
            self._parser = self.make_parser()
        return self._parser
    
    def make_parser(self, **kwargs):
        defaults = {
            'usage': self.usage,
            'option_list': self.make_options(),
            'version': self.version,
            'description': self.description,
            'epilog': self.epilog,
        }
        defaults.update(**kwargs)
        parser = self.parser_cls(**defaults)
        for group in self.make_option_groups(parser):
            parser.add_option_group(group)
        return parser
    
    def make_options(self):
        return list(self.base_options)
    
    def make_option_groups(self, parser):
        # TODO: Implement some class-level group description feature
        return []
    
#    def get_logger_name(self):
#        return 'fmanalyser.command.%s' % self.name
    
    def run(self, argv=None):
        self.connect_signals()
        
        try:
            import setproctitle
            setproctitle.setproctitle(self.name)
        except ImportError:
            pass
        
        self.options, self.args = self.parser.parse_args(argv)
        
        if self.options.config_file is not None:
            fmconfig.source = IniFileSource(os.path.abspath(self.options.config_file))
        
        self.alter_conf(fmconfig)
        
        self.configure_logging()
        
        self.logger.info('running %s' % self)
        
        try:
            r = self.execute()
            self.logger.debug('Bye !')
            return r
        except CommandError, e:
            self.logger.critical(str(e))
            sys.exit(e.errno)
        finally:
            self.close()
    
    def alter_conf(self, config):
        """Hook method called to alter the :attr:`fmconfig` object once its source data have been set"""
        pass
    
    def connect_signals(self):
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self.stop_on_signal)
    
    def stop_on_signal(self, signal, frame):
        self.logger.info('stopping on signal %s' % signal)
        self.stop()
    
    def close(self):
        """Hook to perform necessary stuffs on normal or abnormal exit"""
    
    def configure_logging(self):
        
        level = settings.loglevel
        vcount = self.options.verbosity
        if vcount is not None:
            if vcount < 0:
                level = logging.CRITICAL
            elif vcount == 1:
                level = logging.INFO
            elif vcount >= 2:
                level = logging.DEBUG
            fmconfig['global']['loglevel'] = level
        
        root_logger = logging.getLogger('')
        root_logger.setLevel(level)
        
        stderr_handler = logging.StreamHandler()
        stderr_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)-8s %(name)-32s %(message)s',
        ))
        
        root_logger.addHandler(stderr_handler)
