# -*- coding: utf-8 -*-
import logging

BASE_NAME = 'fmanalyser'

def get_logger(name):
    if not name.startswith('%s.' % BASE_NAME):
        name = '%s.%s' % (BASE_NAME, name)
    return logging.getLogger(name)


class Loggable(object):
    
    logger_name = None
    
    def get_logger_name(self):
        if self.logger_name is None:
            return self.__module__
        return self.logger_name
    
    @property
    def logger(self):
        if getattr(self, '_logger', None) is None:
            self._logger = logging.getLogger(self.get_logger_name())
        return self._logger