# -*- coding: utf-8 -*-
from ..exceptions import AlreadyRegistered
from ..utils.conf import options
from ..utils.conf.holder import OptionHolder
from ..utils.datastructures.ordereddict import OrderedDict
from ..utils.import_tools import get_class
from ..utils.log import LoggableMixin

class BasePlugin(LoggableMixin, OptionHolder):

    config_section_name = 'plugin'
    enabled = options.BooleanOption(default=True)
    
    @classmethod
    def config_section_factory(cls):
        return super(BasePlugin, cls).config_section_factory(classname = options.Option(required=True))

class Registry(object):
    
    def __init__(self):
        self._plugins = OrderedDict()
    
    def populate_from_config(self, config):
        for name, plugin_conf_section in config.iter_subsection_items('plugin'):
            plugin_conf = plugin_conf_section.values.copy()
            Plugin = get_class(plugin_conf.pop('classname'))
            plugin = Plugin(**plugin_conf)
            self.register(name, plugin)
       
    def register(self, name, plugin):
        if name in self._plugins:
            raise AlreadyRegistered('plugin named %s already registered : %s' % (name, plugin))
        self._plugins[name] = plugin
        return plugin
    
plugins = Registry()