# -*- coding: utf-8 -*-

from .iniutil import ini_string_dict, ini_files_dict
from .section import PATH_SEPARATOR, parse_full_section_name

class BaseConfig(object):
    """Provides access to a list of config sections. Values can be read from ini files or from a string"""
    
    #: The handled :class:`BaseConfigSection` classes 
    section_classes = ()
    
    def __init__(self, files=None, raw_data=None, ):
        self._source = None
        self.set_source(files, raw_data)
        self._parser = None
        self._sections = {}

    def __getitem__(self, key):
        return self.get_section(key).values
    
    def set_file(self, path):
        self.set_source(files=[path])
    
    def set_source(self, files=None, raw_data=None):
        if self._source is not None:
            raise RuntimeError("can't change config data source because data is already loaded")
        if isinstance(files, basestring):
            files = [files]
        self._files = files
        self._raw_data = raw_data
    
    @property
    def source(self):
        """Uncleaned values from source files or raw data.
        
        Defaults values are not included.
        """
        if self._source is None:
            self._load_source()
        return self._source
    
    def _load_source(self):
        if self._raw_data is not None:
            self._source = ini_string_dict(self._raw_data)
        elif self._files is not None:
            self._source = ini_files_dict(self._files)
        else:
            raise ValueError('Missing data source')
    
    def get_subsection_fullnames(self, basename):
        return [name for name in self.source
                if name.startswith('%s%s' % (basename, PATH_SEPARATOR))]
        
    def get_subsection_names(self, basename):
        return [name.split(PATH_SEPARATOR, 1)[1] for name in self.source
                if name.startswith('%s%s' % (basename, PATH_SEPARATOR))]
    
    
    def iter_subsection_items(self, basename):
        for fullname in self.get_subsection_fullnames(basename):
            name = fullname.split(PATH_SEPARATOR, 1)[1]
            yield name, self.get_section(fullname)
    
    def get_section(self, name, subname=None):
        if PATH_SEPARATOR in name:
            fullname = name
            basename, subname = parse_full_section_name(name)
        elif subname is None:
            fullname = basename = name
        else:
            basename = name
            fullname = '%s%s%s' % (basename, PATH_SEPARATOR, subname)
                
        if fullname not in self._sections:
            
            try:
                cls = next(c for c in self.section_classes if c.basename == basename)
            except StopIteration:
                raise ValueError('unknown section %s' % fullname) 
            self._sections[fullname] = cls(source=self.source, subname=subname)
        return self._sections[fullname]
    
    
    

