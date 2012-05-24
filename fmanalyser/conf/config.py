# -*- coding: utf-8 -*-
from fmanalyser.exceptions import MissingSection, NoSuchSection

PATH_SEPARATOR = ':'

def parse_full_section_name(fullname):
    parts = fullname.split(PATH_SEPARATOR)
    if len(parts) == 1:
        return fullname, None
    elif len(parts) == 2:
        return parts
    else:
        raise ValueError('%s is not a valid section name' % fullname)

class Config(object):
    
#    _dict = dict()
    
    def __init__(self, source=None):
        self._source = source
        self._raw = None
        self._sections = None

    def __getitem__(self, key):
        return self._get_section(key, None)
    
    def _get_source(self):
        if self._source is None:
            raise RuntimeError('No source defined')
        return self._source
    
    def _set_source(self, source):
        if self.loaded:
            raise RuntimeError('Source already loaded')
        self._source = source
    
    source = property(_get_source, _set_source)
    
    @property
    def loaded(self):
        return self._raw is not None
    
    @property
    def raw(self):
        if self._raw is None:
            self._raw = self.source.to_dict()
        return self._raw
    
    def get_subsection_fullnames(self, basename):
        return [name for name in self.raw
                if name.startswith('%s%s' % (basename, PATH_SEPARATOR))]
    
    def iter_subsections(self, basename):
        for fullname in self.get_subsection_fullnames(basename):
            name = fullname.split(PATH_SEPARATOR, 1)[1]
            yield name, self.get_section(fullname)
    
    def iter_section_or_subsections(self, basename):
        """iterates over subsections whose base name is `basename`
        or yield the global section if no subsection exists.
        
        yield pairs of key/dict where key is the sub-name of the section
        (or `None` if no subsection) and dict is a copy of the section values
        """
        fullnames = self.get_subsection_fullnames(basename)
        if fullnames:
            for fullname in fullnames:
                yield fullname.split(PATH_SEPARATOR, 1)[1], self.get_section(fullname).copy()
        else:
            yield None, self.get_section(basename).copy()
    
    def get_section_or_subsections(self, basename):
        fullnames = self.get_subsection_fullnames(basename) or [basename]
        return [self.get_section(n) for n in fullnames]
    
    def has_section(self, basename, subname):
        if subname is None:
            fullname = basename
        else:
            fullname = '%s%s%s' % (basename, PATH_SEPARATOR, subname)
        return fullname in self.raw
    
    def get_section(self, name, subname=None, copy=True):
        """Returns the '[name:subname]' section dict. By default, a copy is returned"""
        section = self._get_section(name, subname)
        if copy:
            section = section.copy()
        return section
    
    def _get_section(self, name, subname):
        if PATH_SEPARATOR in name:
            fullname = name
            basename, subname = parse_full_section_name(name)
        elif subname is None:
            fullname = basename = name
        else:
            basename = name
            fullname = '%s%s%s' % (basename, PATH_SEPARATOR, subname)
    
        if self._sections is None:
            self._sections = {}

        if fullname not in self._sections:
            if subname is not None and fullname not in self.raw:
                raise NoSuchSection(fullname)
            values = self.source._dict()
            if basename in self.raw:
                values.update(self.raw[basename])
            if fullname in self.raw:
                values.update(self.raw[fullname])
            self._sections[fullname] = values
        return self._sections[fullname]
    
    
    
    
    
    
    
    