# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
from StringIO import StringIO
from fmanalyser.utils.datastructures import OrderedDict

class BaseConfigSource(object):
    
    def __init__(self, dict_type=OrderedDict):
        self._dict = dict_type
        self._raw = None
    
    def to_dict(self):
        raise NotImplementedError()
    
class BaseIniSource(BaseConfigSource):

    @property
    def parser(self):
        if getattr(self, '_parser', None) is None:
            self._parser = self.get_parser()
        return self._parser
        
    def get_parser(self):
        raise NotImplementedError()

    def to_dict(self):
        d = self._dict()
        for section in self.parser.sections():
            d[section] = self._dict()
            for option in self.parser.options(section):
                d[section][option] = self.parser.get(section, option)
        return d

class IniFileSource(BaseIniSource):
    
    def __init__(self, *files, **kwargs):
        super(IniFileSource, self).__init__(**kwargs)
        self._files = files

    def get_parser(self):
        parser = ConfigParser(dict_type = self._dict)
        parser.read(*self._files)
        return parser

class IniStringSource(BaseIniSource):
    
    def __init__(self, raw_data, **kwargs):
        super(IniStringSource, self).__init__(**kwargs)
        self._raw_data = raw_data
    
    def get_parser(self):
        parser = ConfigParser(dict_type = self._dict)
        parser.readfp(StringIO(self._raw_data))
        return parser
