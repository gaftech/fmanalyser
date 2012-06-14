# -*- coding: utf-8 -*-
from fmanalyser.conf import OptionHolder
from fmanalyser.utils.log import Loggable

class BaseDevice(Loggable):
    pass

class Device(Loggable, OptionHolder):
    pass

    
