# -*- coding: utf-8 -*-
import wx
from .mixins import ChannelVariableListenerMixin
from ...utils.log import Loggable

class SimpleValueDisplay(Loggable, ChannelVariableListenerMixin, wx.StaticText):
    
    def update_value(self, value):
        self.SetLabel(value)




