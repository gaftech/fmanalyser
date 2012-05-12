# -*- coding: utf-8 -*-
from .declarative import DeclarativeOptionMetaclass
from fmanalyser.exceptions import MissingSection
PATH_SEPARATOR = ':'

def parse_full_section_name(fullname):
    parts = fullname.split(PATH_SEPARATOR)
    if len(parts) == 1:
        return fullname, None
    elif len(parts) == 2:
        return parts
    else:
        raise ValueError('%s is not a valid section' % fullname)

class BaseConfigSection(object):
    """Represents an ini file section."""
    __metaclass__ = DeclarativeOptionMetaclass
    basename = None
    required = False
    allow_extra_options = True
    ignore_extra_options = False
    ini_help = ''

    def __init__(self, source, subname=None):
        self._source = source
        self._subname = subname
        self._values = None

    def __getitem__(self, key):
        return self.values[key]
    
    def __str__(self):
        return self.name
    
    @property
    def name(self):
        if self._subname is None:
            return self.basename
        return '%s%s%s' % (self.basename, PATH_SEPARATOR, self._subname)
    
    @property
    def subname(self):
        return self._subname

    @property
    def in_source(self):
        return self.name in self._source
    
    @property
    def values(self):
        if self._values is None:
            self._values = self._get_values()
        return self._values

    def _get_values(self):
        if self.required and not self.in_source:
            raise MissingSection(self)
        values = self._source.clean_section(self)
        return values
    
    def get_options(self):
        return self._options
