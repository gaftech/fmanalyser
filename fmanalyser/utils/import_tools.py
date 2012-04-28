# -*- coding: utf-8 -*-
import sys

def get_class(fullname):
    
    if not isinstance(fullname, basestring):
        raise TypeError('fullname should be a string, got %s' % fullname)
    
    modname, classname = fullname.rsplit('.',1)

    try:
        __import__(modname)
        mod = sys.modules[modname]
        cls = getattr(mod, classname)
    except AttributeError, e:
        raise ImportError("can't find class %s: %s" % (fullname, e))
    return cls