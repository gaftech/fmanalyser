# -*- coding: utf-8 -*-

import wx
from .mixins import ChannelVariableListenerMixin
from ...utils.log import LoggableMixin
from fmanalyser.utils.datastructures import NOTSET
from fmanalyser.gui.widgets.mixins import ControlledMixin


class FrequencyTextCtrl(ChannelVariableListenerMixin, wx.TextCtrl):
    
    varkey = 'frequency'
    use_raw_value = True
    
    def __init__(self, *args, **kwargs):
        defaults = {
            'style': wx.TE_PROCESS_ENTER,
        }
        defaults.update(kwargs)
        super(FrequencyTextCtrl, self).__init__(*args, **defaults)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_enter)

    def on_enter(self, event):
        value = self.GetValue()
        self.controller.tune(value)

class FrequencySpinButton(ControlledMixin, wx.SpinButton):
    
    def __init__(self, *args, **kwargs):
        super(FrequencySpinButton, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_SPIN_DOWN, self.on_spin_down)
        self.Bind(wx.EVT_SPIN_UP, self.on_spin_up)
    
    def on_spin_up(self, event):
        self.controller.tune_up()
    
    def on_spin_down(self, event):
        self.controller.tune_down()
    

class TuneSpinButton(ControlledMixin, wx.SpinButton):
    # TODO : quick and dirty
    def __init__(self, *args, **kwargs):
        super(TuneSpinButton, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_SPIN_DOWN, self.on_spin_down)
        self.Bind(wx.EVT_SPIN_UP, self.on_spin_up)
    
    def on_spin_up(self, event):
        self.controller.dirty_tune_up()
    
    def on_spin_down(self, event):
        self.controller.dirty_tune_down()
    

    