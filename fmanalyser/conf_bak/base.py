# -*- coding: utf-8 -*-

from .section import PATH_SEPARATOR, parse_full_section_name

class BaseConfig(object):
    """Provides access to a list of config sections. Values can be read from ini files or from a string"""
    
    #: The handled :class:`BaseConfigSection` classes 
    section_classes = ()
    
    def __init__(self, source=None):
        self._source = source
        self._sections = None

    def __getitem__(self, key):
        return self.get_section(key).values
    
    def _get_source(self):
        if self._source is None:
            raise RuntimeError('No source defined')
        return self._source
    
    def _set_source(self, source):
        if self._sections is not None:
            raise RuntimeError('Source already loaded')
        self._source = source
    
    source = property(_get_source, _set_source)
    
    @property
    def loaded(self):
        return self._source is not None
    
    def get_subsection_fullnames(self, basename):
        return [name for name in self.source
                if name.startswith('%s%s' % (basename, PATH_SEPARATOR))]
        
    def get_subsection_names(self, basename):
        return [name.split(PATH_SEPARATOR, 1)[1] for name in self.source
                if name.startswith('%s%s' % (basename, PATH_SEPARATOR))]
    
    def get_subsections(self, basename):
        return [self.get_section(fullname)
                for fullname in self.get_subsection_fullnames(basename)]
    
    def iter_subsection_items(self, basename):
        for fullname in self.get_subsection_fullnames(basename):
            name = fullname.split(PATH_SEPARATOR, 1)[1]
            yield name, self.get_section(fullname)
    
    def get_section_or_subsections(self, basename):
        return self.get_subsections(basename) or [self.get_section(basename)]
                
    def get_section(self, name, subname=None):
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
            try:
                cls = next(c for c in self.section_classes if c.basename == basename)
            except StopIteration:
                raise ValueError('unknown section %s' % fullname) 
            self._sections[fullname] = cls(source=self.source, subname=subname)
        return self._sections[fullname]
    
    
    

