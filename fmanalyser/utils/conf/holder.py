# -*- coding: utf-8 -*-
from ...exceptions import MissingOption, UnexpectedOption
from .section import BaseConfigSection
from .declarative import DeclarativeOptionMetaclass

class OptionHolder(object):
    
    __metaclass__ = DeclarativeOptionMetaclass
    
    config_section_name = None
    
    @classmethod
    def get_options(cls):
        return cls._options.values()
    
    @classmethod
    def iter_options(cls):
        for k, opt in cls._options.iteritems():
            yield k, opt
    
    @classmethod
    def get_option(cls, attname):
        return cls._options[attname]
    
    @classmethod
    def config_section_factory(cls, config_class=BaseConfigSection, **attrs):
        assert cls.config_section_name is not None
        attrs['basename'] = cls.config_section_name
        for k, _option in cls._options.items():
            assert k not in attrs
            attrs[k] = _option.clone()
        
        classname = '%sConfigSection' % cls.config_section_name.title()
        
        return  type(classname, (config_class,), attrs)
    
    def __init__(self, **kwargs):
        
        # Set instance attributes from kwargs or option defaults
        for k, option in self._options.items():
            assert not hasattr(self, k)
            setattr(self, k, option.pop_val_from_dict(kwargs))
        if len(kwargs):
            raise UnexpectedOption(', '.join(kwargs))
        
    
    