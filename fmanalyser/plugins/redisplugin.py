# -*- coding: utf-8 -*-
from ..plugins.base import CorePlugin
import redis
from ..models.signals import value_changed
from ..conf import options

class RedisPlugin(CorePlugin):
    
    config_section_name = 'redis'
    
    host = options.Option(default='localhost')
    port = options.IntOption(default=6379)
    db = options.IntOption(default=0)
    expire = options.IntOption(default=30)
    
    def start(self):
        self.client = redis.Redis(self.host, self.port, self.db)
        self._connect()
    
    def _connect(self):
        value_changed.connect(self.on_value_changed)
        
    def on_value_changed(self, signal, sender, event):
        key = 'fma.channels.%s.%s' % (sender.channel.name, sender.key)
        value = sender.value
        self.set_volatile(key, value)
    
    def set_volatile(self, key, value):
        self.client.set(key, value)
        self.client.expire(key, self.expire)