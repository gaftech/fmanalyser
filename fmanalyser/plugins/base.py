# -*- coding: utf-8 -*-
from fmanalyser.conf.holder import EnableableSectionOptionHolder
from fmanalyser.conf import BaseConfigSection, options
from fmanalyser.utils.log import Loggable
from fmanalyser.utils.import_tools import get_class

class BasePlugin(Loggable, EnableableSectionOptionHolder):
    pass

class CorePlugin(BasePlugin):
    pass

class PluginConfigSection(BaseConfigSection):

    cls = options.Option(required=True,
        ini_help="Full python class name (e.g. myapp.mymodule.MyPluginClass)")

    ini_help = """
Base config for all user defined plugins.
It must be extended for each plugin by creating a section named [plugin:<your_plugin_name>].
"""

    def get_options(self):
        options = self._options.copy()
        classname = self._source[self.name]['cls']
        Plugin = get_class(classname)
        options.update(Plugin._options)
        return options

class Plugin(BasePlugin):

    config_section_name = 'plugin'
    
    @classmethod
    def config_section_factory(cls):
        return super(Plugin, cls).config_section_factory(
            config_class = PluginConfigSection,
        )

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
        plugin = Plugin(controller, **config[Plugin.config_section_name])
        plugins.append(plugin)
    
    for name, plugin_conf_section in config.iter_subsection_items('plugin'):
        plugin_conf = plugin_conf_section.values.copy()
        Plugin = get_class(plugin_conf.pop('cls'))
        plugin = Plugin(controller, name, **plugin_conf)
        plugins.append(plugin)
    
    return plugins

#class Registry(object):
#    
#    def __init__(self):
#        self._plugins = OrderedDict()
#    
#    def __iter__(self):
#        for plugin in self._plugins.itervalues():
#            yield plugin
#    
#    def populate_from_config(self, config):
#        for name, plugin_conf_section in config.iter_subsection_items('plugin'):
#            plugin_conf = plugin_conf_section.values.copy()
#            Plugin = get_class(plugin_conf.pop('cls'))
#            plugin = Plugin(**plugin_conf)
#            self.register(name, plugin)
#       
#    def register(self, name, plugin):
#        if name in self._plugins:
#            raise AlreadyRegistered('plugin named %s already registered : %s' % (name, plugin))
#        self._plugins[name] = plugin
#        return plugin
#    
#plugins = Registry()