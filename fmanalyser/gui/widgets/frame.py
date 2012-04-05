# -*- coding: utf-8 -*-

import wx

from . import display, input

class Frame(wx.Frame):
    
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        
        
        panel = wx.Panel(self)
        freq_input_label = wx.StaticText(panel, label="frequency")
        freq_input = input.FrequencyTextCtrl(panel)
        freq_display_label = wx.StaticText(panel, label="frequency")
        freq_display = display.SimpleValueDisplay(panel, varkey="frequency")
        tune_button = input.FrequencySpinButton(panel)
        dirty_tune_button = input.TuneSpinButton(self)
        rf_display_label = wx.StaticText(panel, label="rf level")
        rf_display = display.SimpleValueDisplay(panel, varkey="rf")
         
        
        sizer = wx.GridSizer(3, 3)
        sizer.Add(freq_input_label)
        sizer.Add(freq_input)
        sizer.Add(tune_button)
        sizer.Add(freq_display_label)
        sizer.Add(freq_display)
        sizer.Add(dirty_tune_button)
        sizer.Add(rf_display_label)
        sizer.Add(rf_display)
        
        
        box = wx.BoxSizer()
        box.Add(sizer)
        panel.SetSizerAndFit(box)
        self.Fit()
        
        self.Show(True)
        self.Center()