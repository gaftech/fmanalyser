# -*- coding: utf-8 -*-
from fmanalyser.utils.signals import BaseEvent

class ValueChangeEvent(BaseEvent):
    
    kwargs = ('old_value', 'new_value')
    


