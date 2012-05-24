# -*- coding: utf-8 -*-
from fmanalyser.conf import options, OptionHolder
from fmanalyser.utils.log import Loggable
from fmanalyser.utils.import_tools import get_class

class BasePlugin(Loggable, OptionHolder):
    pass

class CorePlugin(BasePlugin):
    pass

class Plugin(BasePlugin):

    section_name = 'plugin'

    cls = options.Option(required=True,
        ini_help="Full python class name (e.g. myapp.mymodule.MyPluginClass)")
    
    ini_help = """
Base config for all user defined plugins.
It must be extended for each plugin by creating a section named [plugin:<your_plugin_name>].
"""

    def __init__(self, controller, name=None, **kwargs):
        
        self.controller = controller
        self.name = name
        
        super(Plugin, self).__init__(name=name, **kwargs)
        
        if self.enabled:
            self.logger.info('plugin loaded: %s' % self)

    def __str__(self):
        return self.name

    def start(self):
        pass
    
    def close(self):
        pass

def create_plugins(controller, config):
    from . import core_plugins
    
    plugins = []
    
    for Plugin in core_plugins:
        plugin = Plugin(controller, **config[Plugin.section_name])
        plugins.append(plugin)
    
    for name, plugin_conf_section in config.iter_subsections('plugin'):
        plugin_conf = plugin_conf_section.copy()
        Plugin = get_class(plugin_conf.pop('cls'))
        plugin = Plugin(controller, name, **plugin_conf)
        plugins.append(plugin)
    
    return plugins
