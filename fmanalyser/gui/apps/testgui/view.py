# -*- coding: utf-8 -*-

import wx
from fmanalyser.gui import widgets
        

class App(wx.App):
    
    def __init__(self, controller, *args, **kwargs):
        self.controller = controller
        wx.App.__init__(self, *args, **kwargs)
        
    
    def OnInit(self):
        self.frame = widgets.Frame(None, wx.ID_ANY, 'fmanalyser')
        return True

