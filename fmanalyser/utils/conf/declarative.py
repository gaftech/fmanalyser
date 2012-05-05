# -*- coding: utf-8 -*-
from . import options
from fmanalyser.utils.datastructures.ordereddict import OrderedDict
from copy import copy

class DeclarativeOptionMetaclass(type):
    """Metaclass for option holders
    
    ..todo:: The original idea was to provide a DRY generic declarative metaclass
            but after a first try, I'm not sure it would be a great time saver.
            To be reconsidered if we use more and more similar declarative metaclasses.
    """
    
    
    _metaname = '_options'
    _option_cls = options.Option
    _copy_options = True
    
    def __new__(cls, name, bases, attrs):
        new_attrs = attrs.copy()
        
        # Grab options...
        # ... from bases
        _options = {}
        for base in bases:
            _options.update(getattr(base, cls._metaname, {}).items())
        # ... from class special option attribute
        _options.update(new_attrs.pop(cls._metaname, {}).items())
        # ... and from class attributes
        _options.update((k,new_attrs.pop(k)) for k,v in new_attrs.items()
                       if not k.startswith('_') and isinstance(v, cls._option_cls))
        
        # Sort and clone the _options
        items = _options.items()
        if hasattr(cls._option_cls, '_creation_counter'):
            items.sort(cmp=lambda x,y: cmp(x[1]._creation_order, y[1]._creation_order))
        if cls._copy_options:
            items = [(k, copy(o)) for k,o in items]
        options = OrderedDict(items)
        
        new_class = super(DeclarativeOptionMetaclass, cls).__new__(
            cls, name, bases, new_attrs)
        
        # Store our _options in new class
#        _options.update(_options)   
        setattr(new_class, cls._metaname, options)
        
        # Contribute to new class
        for k, option in options.iteritems():
            if hasattr(option, 'contribute_to_class'):
                option.contribute_to_class(new_class, k)
        
        return new_class
    
    
