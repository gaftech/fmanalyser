# -*- coding: utf-8 -*-
import wx
from .mixins import ChannelVariableListenerMixin
from ...utils.log import LoggableMixin

class SimpleValueDisplay(LoggableMixin, ChannelVariableListenerMixin, wx.StaticText):
    
    def update_value(self, value):
        self.SetLabel(value)




