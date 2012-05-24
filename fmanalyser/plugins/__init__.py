from .base import Plugin
from .snmp.server import SnmpServerPlugin
from .redisplugin import RedisPlugin


core_plugins = (
    SnmpServerPlugin,
    RedisPlugin,
)