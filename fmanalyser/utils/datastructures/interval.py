# -*- coding: utf-8 -*-

class Interval(object):
    
    def __init__(self, *args):
        
        self._bounds = []
        for arg in args:
            if isinstance(arg, (int, float, long)):
                start, stop = arg, arg
            else:
                start, stop = arg
            assert start <= stop
            self._bounds.append((start,stop))
            
    def __contains__(self, item):
        return any(item >= b[0] and item <= b[1] for b in self._bounds)
            
            