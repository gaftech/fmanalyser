# -*- coding: utf-8 -*-
"""This modules provides access to user configuration files.

By default, those files are located in '~/.fmanalyser'.
They are ini-format files whose sections can be extended by subsections,
using the [section:subsection] syntax.


"""
from ConfigParser import ConfigParser
from StringIO import StringIO
from collections import Mapping
from copy import copy
from fmanalyser.exceptions import UnexpectedOption, MissingOption, \
    MissingSection
from fmanalyser.utils.conf.declarative import DeclarativeOptionMetaclass

PATH_SEPARATOR = ':'

def parse_full_section_name(fullname):
    parts = fullname.split(PATH_SEPARATOR)
    if len(parts) == 1:
        return fullname, None
    elif len(parts) == 2:
        return parts
    else:
        raise ValueError('%s is not a valid section' % fullname)

class IniParser(object):
    """Ini config file parser 
    
    By default, gives access to`~/.fmanalyser/conf.ini`.
    """

    #: If false, all keys will be converted to lower case
    cased_keys = False

    def __init__(self, inifiles=None, raw_data=None):
        """
        :param string inifiles:
            list of ini files path 
        :param file-like|string raw_data:
            if given, ini file contents won't be read, but this
            data object will be used to populate the option parser. 
        """
        assert inifiles is not None or raw_data is not None
        self._inifiles = inifiles
        if raw_data is not None:
            if isinstance(raw_data, basestring):
                raw_data = StringIO(raw_data)
            self._parser = self._get_parser(raw_data)

    @property
    def parser(self):
        """The associated :class:`ConfigParser.ConfigParser` instance."""
        if getattr(self, '_parser', None) is None:
            self._parser = self._get_parser()
        return self._parser

    def _get_parser(self, fileobj=None):
        parser = ConfigParser()
        if fileobj is None:
            parser.read(self._inifiles)
        else:
            parser.readfp(fileobj)
        return parser
    
    def get_subsection_names(self, basename):
        return [name for name in self.parser.sections()
                if name.startswith('%s:' % basename)]
        
    def has_subsection(self, key):
        return bool(self.get_subsection_names(key))
    
    def get_section_values(self, key):
        """Returns the data for the given section.
        
        The section `key` can consist of a path like `section:subsection`.
        In that case, the returned dict will be a merge of `[section]`
        and `[section:subsection]` values.
        
        Example :
            
            >>> parser = IniParser(raw_data = \"\"\"\\
            ... [section]
            ... value1 = 1
            ... value2 = 2
            ... [section:subsection]
            ... value2 = 22
            ... value3 = 3
            ... \"\"\")
            >>> section = parser.get_section_values('section:subsection')
            >>> section == {'value1': '1', 'value2': '22', 'value3': '3'}
            True
        
        :param string key: the ini-file section name
        """
        
        parser = self.parser
        section, subsection = parse_full_section_name(key)
        section_dict = self._get_section_dict(parser, section)
        subsection_dict = self._get_section_dict(parser, key)
        if subsection_dict is None:
            raise MissingSection('%s:%s' % (section, subsection))
        values = {}
        if section_dict is not None:
            values.update(section_dict)
        values.update(subsection_dict)
        return values
    
    def _get_section_dict(self, parser, section):
        if section is None or not parser.has_section(section):
            return None
        return dict((option, parser.get(section, option)) for option in parser.options(section))

class ParserAccess(object):
    """Mixin for class wanting to play with an ini file parser"""
    _dict = dict
    
    def get_subsection_values(self, basename):
        keys = self.get_subsection_names(basename)
        return dict((key.split(PATH_SEPARATOR)[1], self.get_section_values(key)) for key in keys)

class ConfigSection(ParserAccess):
    """Represents an ini file section."""
    __metaclass__ = DeclarativeOptionMetaclass
    section = None
    required = True
    allow_extra_options = True
    ignore_extra_options = False
    
    def __init__(self, parser, subsection=None):
        self.subsection = subsection
        if subsection is not None:
            self.name = '%s:%s' % (self.section, self.subsection)
        else:
            self.name = self.section
        self.parser = parser
        self._values = None

    def __getitem__(self, key):
        return self.values[key]

    @property
    def values(self):
        if self._values is None:
            self._values = self._get_values()
        return self._values

    def _get_values(self):
        values = self.get_defaults()
        try:
            raw_values = self.parser.get_section_values(self.name)
        except MissingSection:
            if self.required:
                raise
            return values
        values.update(self.clean_values(raw_values))
        return values
    
    def get_defaults(self):
        return self._dict((k, option.default) for (k, option) in self._options.items())
    
    def clean_values(self, raw_values):
        values = self._dict()
        raw_values = copy(raw_values)
        for k, option in self._options.iteritems():
            try:
                raw = raw_values.pop(k)
            except KeyError:
                if option.required:
                    raise MissingOption("Missing required option from section %s : %s" % (self.name, k))
                value = option.default
            else:
                value = option.clean(raw)
            values[k] = value      
        if len(raw_values):
            if not self.allow_extra_options:
                raise UnexpectedOption("Unexpected options in section %s : %s" % (
                        self.name, ', '.join(raw_values.keys())))
            if not self.ignore_extra_options:
                values.update(raw_values)
        return values

class BaseConfig(ParserAccess):
    
    inifiles = None
    sections = ()
    
    def __init__(self, raw_data=None):
        self.raw_data = raw_data
        self._parser = None
        self._sections = {}
    
    def __len__(self):
        return len(self.parser.sections())
    
    def __iter__(self):
        return iter(self.get_sections())

    def __getitem__(self, key):
        return self.get_section(key)
    
    @property
    def parser(self):
        if self._parser is None:
            self._parser = IniParser(self.inifiles, self.raw_data)
        return self._parser
    
    def get_subsections(self, basename):
        keys = self.parser.get_subsection_names(basename)
        return [self.get_section(k) for k in keys]
    
    def get_section(self, fullname):
        if fullname not in self._sections:
            section, subsection = parse_full_section_name(fullname)
            try:
                cls = next(c for c in self.sections if c.section == section)
            except StopIteration:
                raise MissingSection(fullname) 
            self._sections[fullname] = cls(parser=self.parser, subsection=subsection)
        return self._sections[fullname]
    
    
    
    
    
    
    
    
