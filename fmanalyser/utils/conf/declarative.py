# -*- coding: utf-8 -*-
from . import options

class DeclarativeOptionMetaclass(type):
    """Metaclass for option holders
    
    ..todo:: The original idea was to provide a DRY generic declarative metaclass
            but after a first try, I'm not sure it would be a great time saver.
            To be reconsidered if we use more and more similar declarative metaclasses.
    """
    
    
    _metaname = '_options'
    _option_cls = options.Option
    
    def __new__(cls, name, bases, attrs):
        new_attrs = attrs.copy()
        
        # Let's collect options...
        # ... from bases
        _options = {}
        for base in bases:
            if hasattr(base, cls._metaname):
                _options.update(base._options)
        _declared_options = {}
        # ... from class special option attribute
        if cls._metaname in new_attrs:
            _declared_options.update(new_attrs.pop(cls._metaname))
        # ... and from class attributes
        for k,v in new_attrs.items():
            if not k.startswith('_') and isinstance(v, cls._option_cls):
                _declared_options[k] = new_attrs.pop(k)
                
        new_class = super(DeclarativeOptionMetaclass, cls).__new__(
            cls, name, bases, new_attrs)
        
        # Store our options in new class
        _options.update(_declared_options)   
        setattr(new_class, cls._metaname, _options)
        
        # Contribute to new class
        for k, option in _declared_options.iteritems():
            if hasattr(option, 'contribute_to_class'):
                option.contribute_to_class(new_class, k)
        
        return new_class
    
    
