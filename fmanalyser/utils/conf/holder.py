# -*- coding: utf-8 -*-
from ...exceptions import MissingOption, UnexpectedOption
from .section import BaseConfigSection
from .declarative import DeclarativeOptionMetaclass

class OptionHolder(object):
    
    __metaclass__ = DeclarativeOptionMetaclass
    
    config_section_name = None
    
    @classmethod
    def config_section_factory(cls, **attrs):
        assert cls.config_section_name is not None
        attrs['basename'] = cls.config_section_name
        for k, _option in cls._options.items():
            assert k not in attrs
            attrs[k] = _option.clone()
        
        classname = '%sConfigSection' % cls.config_section_name.title()
        
        return  type(classname, (BaseConfigSection,), attrs)
    
    def __init__(self, **kwargs):
        
        # Set instance attributes from kwargs or option defaults
        for k, option in self._options.items():
            if option.required and k not in kwargs:
                raise MissingOption(k)
            setattr(self, k, kwargs.pop(k, option.default))
            
        if len(kwargs):
            raise UnexpectedOption(', '.join(kwargs))
        
        
    
    