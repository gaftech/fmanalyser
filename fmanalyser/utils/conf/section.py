# -*- coding: utf-8 -*-
from fmanalyser.utils.conf.declarative import DeclarativeOptionMetaclass
from fmanalyser.exceptions import MissingOption, UnexpectedOption,\
    MissingSection
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

    def __init__(self, source, subname=None, dict_type=dict):
        self._source = source
        self._subname = subname
        self._dict = dict_type
        self._values = None

    def __getitem__(self, key):
        return self.values[key]
    
    @property
    def name(self):
        if self._subname is None:
            return self.basename
        return '%s%s%s' % (self.basename, PATH_SEPARATOR, self._subname)
    
    @property
    def values(self):
        if self._values is None:
            self._values = self._get_values()
        return self._values
    
    def _get_values(self):
        
        if self.required and self.name not in self._source:
            raise MissingSection(self.name)
        
        # Merging base section and subsection values
        raw_values = self._dict()
        if self._subname is not None and self.basename in self._source:
            raw_values.update(self._source[self.basename])
        if self.name in self._source:
            raw_values.update(self._source[self.name])
        
        values = self._dict()
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



