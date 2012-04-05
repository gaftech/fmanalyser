# -*- coding: utf-8 -*-
import wx

class ControlledMixin(object):
    
    @property
    def controller(self):
        app = wx.GetApp()
        return app.controller

class ChannelVariableListenerMixin(ControlledMixin):
    
    varkey = None
    use_raw_value = False
    
    def __init__(self, *args, **kwargs):
        self.varkey = kwargs.pop('varkey', self.varkey)
        super(ChannelVariableListenerMixin, self).__init__(*args, **kwargs)
        assert self.varkey is not None
        self.register()
        self.update()
        
    def register(self):
        self.controller.add_channel_variable_listener(self.update, self.varkey)
    
    def get_variable(self):
        return self.controller.channel.get_variable(self.varkey)
    
    def update(self, variable=None, event=None):
        if event is not None:
            value = event.new_value
        else:
            if variable is None:
                variable = self.get_variable()
            value = variable.value
        if not self.use_raw_value:
            value = variable.descriptor.format_value(value)
        self.update_value(value)
    
    def update_value(self, current_value):
        pass

