# -*- coding: utf-8 -*-
from ..exceptions import UnexpectedOption
from .declarative import DeclarativeOptionMetaclass
from . import options
from fmanalyser.exceptions import MissingOption

class OptionHolder(object):
    
    __metaclass__ = DeclarativeOptionMetaclass
    
    section_name = None
    ini_help = ''
    
    @classmethod
    def from_config(cls, config, subname=None, defaults=None, extras=None):
        conf_dict = cls.get_config_dict(config, subname)
        return cls.from_config_dict(conf_dict, subname, defaults=defaults, extras=extras)

    @classmethod
    def from_config_dict(cls, confdict, subname=None, defaults=None, extras=None):
        confdict = confdict.copy()
        defaults = defaults or {}
        extras = extras or {}
        kwargs = defaults.copy()
        for k, option in cls.get_config_options().items():
            try:
                value = confdict.pop(k)
            except KeyError:
                if option.required and k not in defaults and k not in extras:
                    raise MissingOption(k)
            else:
                # TODO: Allow the data source to alter the cleaning process
                kwargs[k] = option.clean(value)
        if len(confdict):
            raise UnexpectedOption(
                "%s unexpected option(s): %s" % (
                cls.__name__, ', '.join(confdict),))
        kwargs.update(extras)
        return cls(name=subname, **kwargs)
    
    @classmethod
    def get_config_dict(cls, config, subname=None):
        if cls.section_name is None:
            raise ValueError('%s should define a `section_name`' % cls.__name__)
        return config.get_section(cls.section_name, subname)
    
    @classmethod
    def get_config_options(cls):
        """Returns a copy of the avalaible option dict.
        
        Subclasses may override this method to provide options
        from elsewhere than the class declared options.
        """
        return cls._options.copy()
    
    def __init__(self, name=None, **kwargs):
        
        self.name = name
        
        # Set instance attributes from kwargs or option defaults
        for k, option in self._options.items():
            assert not hasattr(self, k)
            setattr(self, k, option.pop_val_from_dict(kwargs))
        if len(kwargs):
            raise UnexpectedOption(', '.join(kwargs))

class EnableableOptionHolder(OptionHolder):
    
    __metaclass__ = DeclarativeOptionMetaclass
    
    enabled = options.NullBooleanOption()

    @classmethod
    def from_config(cls, config, subname=None, defaults=None, extras=None):
        if cls._options['enabled'].default is None:
            extras.setdefault('enabled', config.has_section(cls.section_name, subname))
        return super(EnableableOptionHolder, cls).from_config(config, subname, defaults, extras)
        





    