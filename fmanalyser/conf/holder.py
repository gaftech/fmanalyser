# -*- coding: utf-8 -*-
from ..exceptions import UnexpectedOption
from .section import BaseConfigSection
from .declarative import DeclarativeOptionMetaclass
from . import options

class OptionHolder(object):
    
    __metaclass__ = DeclarativeOptionMetaclass

    @classmethod
    def get_option(cls, attname):
        return cls._options[attname]
    
    @classmethod
    def get_options(cls):
        return cls._options.values()
    
    @classmethod
    def iter_options(cls):
        for k, opt in cls._options.iteritems():
            yield k, opt
    
    @classmethod
    def from_config_section(cls, section, **kwargs):
        defaults = section.values
        defaults.update(kwargs)
        return cls(name=section.subname, **defaults)
    
    def __init__(self, name=None, **kwargs):
        
        self.name = name
        
        # Set instance attributes from kwargs or option defaults
        for k, option in self._options.items():
            assert not hasattr(self, k)
            setattr(self, k, option.pop_val_from_dict(kwargs))
        if len(kwargs):
            raise UnexpectedOption(', '.join(kwargs))

class SectionOptionHolder(OptionHolder):
    
    config_section_name = None
    
    @classmethod
    def config_section_factory(cls, config_class=BaseConfigSection, **attrs):
        assert cls.config_section_name is not None
        attrs['basename'] = cls.config_section_name
        for k, _option in cls._options.items():
#        for k, _option in cls.get_options().items():
            assert k not in attrs
#            attrs[k] = _option.clone()
            attrs[k] = _option
        
        classname = '%sConfigSection' % cls.config_section_name.title()
        
        return  type(classname, (config_class,), attrs)
    
    @classmethod
    def from_config(cls, config, subname=None, **kwargs):
        section = config.get_section(cls.config_section_name, subname)
        return cls.from_config_section(section, **kwargs)

class EnableableOptionHolderMixin(object):
    
    __metaclass__ = DeclarativeOptionMetaclass
    
    enabled = options.BooleanOption(default=False)

    @classmethod
    def from_config_section(cls, section, **kwargs):
        if section['enabled'] is None:
            kwargs['enabled'] = section.in_source
        return super(EnableableOptionHolderMixin, cls).from_config_section(section, **kwargs)

class EnableableOptionHolder(EnableableOptionHolderMixin, OptionHolder):
    pass

class EnableableSectionOptionHolder(EnableableOptionHolderMixin, SectionOptionHolder):
    pass




    