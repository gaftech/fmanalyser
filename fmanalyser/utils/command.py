# -*- coding: utf-8 -*-
from fmanalyser.utils.log import LoggableMixin
import fmanalyser
import logging
import optparse
import signal
from fmanalyser.client.worker import Worker

class BaseCommand(LoggableMixin):
    
    # Parser kwargs and options
    parser_cls = optparse.OptionParser
    base_options = (
        optparse.make_option(
            '-v', '--verbose', action='count', dest='verbosity',
            help='set verbose, can be repeated to increase verbosity'),
        optparse.make_option(
            '-q', '--quiet', dest='verbosity', action='store_const', const=-1,
            help='set minimal verbosity')
    )
    usage = None
    version = fmanalyser.__version__
    description = None
    epilog = None
    
    def __init__(self):
        self.name = self.__module__.split('.').pop()
    
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
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self.stop)
        
        try:
            import setproctitle
            setproctitle.setproctitle(self.name)
        except ImportError:
            pass
        
        self.options, self.args = self.parser.parse_args(argv)
        self.configure_logging()
        
        self.logger.info('running %s' % self)
        
        self.worker = Worker()
        try:
            r = self.execute()
        finally:
            try:
                if self.worker.exc_info:
                    msg = 'exception occurred in worker thread'
                    raise RuntimeError(msg)
            finally:
                if not self.worker.stopped:
                    self.worker.stop()
        
        self.logger.debug('Bye !')
        return r
    
    def stop(self, signal, frame):
        pass
    
    def configure_logging(self):
        
        root_logger = logging.getLogger('')
        
        verbosity = self.options.verbosity
        level = logging.WARNING
        if verbosity < 0:
            level = logging.CRITICAL
        elif verbosity == 1:
            level = logging.INFO
        elif verbosity > 1:
            level = logging.DEBUG
        
        root_logger.setLevel(level)
        
        stderr_handler = logging.StreamHandler()
        stderr_handler.setFormatter(logging.Formatter(
            '%(levelname)-8s %(name)-32s %(message)s',
        ))
        
        root_logger.addHandler(stderr_handler)
    

        
