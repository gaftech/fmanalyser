# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
from StringIO import StringIO
from fmanalyser.exceptions import MissingSection, MissingOption, \
    UnexpectedOption
from fmanalyser.utils.datastructures.ordereddict import OrderedDict

class BaseConfigSource(object):

    def __iter__(self):
        """Subclasses must implement this method to iterate over full section names located in source data"""
        raise NotImplementedError()
    
    def get_cleaned_values(self, options):
        """Returns a dict of cleaned values"""
        raise NotImplementedError()

class BaseDictSource(BaseConfigSource):

    def __init__(self, dict_type=OrderedDict):
        self._dict = dict_type
        self._raw = None
    
    def __iter__(self):
        for name in self.raw:
            yield name
    
    @property
    def raw(self):
        if self._raw is None:
            self._raw = self.get_raw()
        return self._raw
    
    def get_raw(self):
        """Subclasses must implement this method to return a 2-level dict
        representing source data sections and key-value pairs""" 
        raise NotImplementedError()
    
    def clean_section(self, section):
        values = self._dict()
        
        # Merging base section and subsection values
        raw_values = self._dict()
        if section.subname is not None and section.basename in self.raw:
            raw_values.update(self.raw[section.basename])
        if section.name in self.raw:
            raw_values.update(self.raw[section.name])
        
        for k, option in section.get_options().items():
            try:
                raw = raw_values.pop(k)
            except KeyError:
                if option.required:
                    raise MissingOption(
                        "Missing required option in section %s: %s" % (section.name, k))
                values[k] = self.clean_option(option.default, None)
            else:
                values[k] = self.clean_option(raw, option)

        if len(raw_values):
            if not section.allow_extra_options:
                raise UnexpectedOption("Unexpected options in section %s: %s" % (
                        section, ', '.join(raw_values.keys())))
            if not section.ignore_extra_options:
                for k, raw in raw_values.items():
                    values[k] = self.clean_option(raw, None)
        return values

    def clean_option(self, option, value):
        raise NotImplementedError
                    
class DictSource(BaseDictSource):
    
    def __init__(self, data, **kwargs):
        super(DictSource, self).__init__(**kwargs)
        self._raw = data

    def get_raw(self):
        return self._raw

    def clean_option(self, value, option=None):
        return value

class BaseIniSource(BaseDictSource):
    
    def clean_option(self, value, option=None):
        if option is not None:
            value = option.clean(value)
        return value

    def parser_to_dict(self, parser):
        d = self._dict()
        for section in parser.sections():
            d[section] = self._dict()
            for option in parser.options(section):
                d[section][option] = parser.get(section, option)
        return d

class IniFileSource(BaseIniSource):
    
    def __init__(self, *files, **kwargs):
        super(IniFileSource, self).__init__(**kwargs)
        self._files = files

    def get_raw(self):
        parser = ConfigParser(dict_type = self._dict)
        parser.read(*self._files)
        return self.parser_to_dict(parser)

class IniStringSource(BaseIniSource):
    
    def __init__(self, raw_data, **kwargs):
        super(IniStringSource, self).__init__(**kwargs)
        self._raw_data = raw_data
    
    def get_raw(self):
        parser = ConfigParser(dict_type = self._dict)
        parser.readfp(StringIO(self._raw_data))
        return self.parser_to_dict(parser)
    
    