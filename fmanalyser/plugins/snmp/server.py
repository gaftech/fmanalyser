# -*- coding: utf-8 -*-
from ...utils.command import VERBOSITY
from ...utils.conf import options
from ...utils.plugin import BasePlugin
from ...conf import fmconfig
from .mibload import populate_builder
from pysnmp import debug #@UnresolvedImport
from pysnmp.carrier.asynsock.dgram import udp #@UnresolvedImport
from pysnmp.entity import engine, config #@UnresolvedImport
from pysnmp.entity.rfc3413 import cmdrsp, context #@UnresolvedImport
import threading

class SnmpServerPlugin(BasePlugin):
    
    config_section_name = 'snmpd'
    
    ipv4 = options.BooleanOption(default=True)
    host = options.Option(default='127.0.0.1')
    ipv6 = options.Option(default=False)
    ipv6_host = options.Option(default='::1')
    port = options.IntOption(default=161)

    # v1/v2c specific options
    v1 = options.BooleanOption(default=True) # v1 enabled
    v2c = options.BooleanOption(default=True) # v2 enabled
    security_name = options.Option(default='security')
    community_name = options.Option(default='public')
    
    # v3 specific options
    v3 = options.BooleanOption(default=True)
    auth_protocol = options.ChoiceOption(('SHA1', 'MD5'), default='MD5')
    priv_protocol = options.ChoiceOption(('AES', 'DES'), default='DES')
    user_name = options.Option(default='user')
    user_security_level = options.ChoiceOption(('noAuthNoPriv', 'authNoPriv', 'authPriv'), default='noAuthNoPriv')
    user_auth_key = options.Option(default='auth_key')
    user_priv_key = options.Option(default='priv_key')
    admin_name = options.Option(default='admin')
    admin_security_level = options.ChoiceOption(('noAuthNoPriv', 'authNoPriv', 'authPriv'), default='authNoPriv')
    admin_auth_key = options.Option(default='auth_key')
    admin_priv_key = options.Option(default='priv_key')
    
    
    def start(self):
        self._configure()
        self.thread= threading.Thread(target=self._worker)
        self.thread.start()
    
    def _configure(self):
        
        verbosity = fmconfig['global']['verbosity']
        if verbosity >= VERBOSITY.DEBUG:
            debug.setLogger(debug.Debug('all'))
        
        # Create SNMP engine with autogenernated engineID and pre-bound
        # to socket transport dispatcher
        snmpEngine = engine.SnmpEngine()
        
        # Setup UDP over IPv4 transport endpoint
        if self.ipv4:
            config.addSocketTransport(
                snmpEngine,
                udp.domainName,
                udp.UdpSocketTransport().openServerMode((self.host, self.port))
                )
        
        # Setup UDP over IPv6 transport endpoint
        if self.ipv6:
            from pysnmp.carrier.asynsock.dgram import udp6 #@UnresolvedImport
            config.addSocketTransport(
                snmpEngine,
                udp6.domainName,
                udp6.Udp6Transport().openServerMode((self.ipv6_host, self.port))
            )
        
        # Sympols import/export
        populate_builder(
            controller = self.controller,
            mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder,
        )
        
        # v1/v2 setup
        if self.v1 or self.v2c:
            config.addV1System(snmpEngine, self.security_name, self.community_name)
        # v3 setup
        if self.v3:
            auth_protocol = {
                'SHA1': config.usmHMACSHAAuthProtocol,
                'MD5': config.usmHMACMD5AuthProtocol
            }[self.auth_protocol]
            priv_protocol = {
                'AES': config.usmAesCfb128Protocol,
                'DES': config.usmDESPrivProtocol
            }[self.priv_protocol]
            
            # Read-only user
            config.addV3User(snmpEngine, self.user_name,
                authProtocol = auth_protocol,
                authKey = self.user_auth_key,
                privProtocol = priv_protocol,
                privKey = self.user_priv_key
            )
            
            # Read-write user (admin)
            config.addV3User(snmpEngine, self.admin_name,
                authProtocol = auth_protocol,
                authKey = self.admin_auth_key,
                privProtocol = priv_protocol,
                privKey = self.admin_priv_key
            )
        
        
        # VACM setup
        config.addContext(snmpEngine, '')
        if self.v1:
            config.addRwUser(snmpEngine, 1, self.security_name, 'noAuthNoPriv', (1,3,6)) # v1
        if self.v2c:
            config.addRwUser(snmpEngine, 2, self.security_name, 'noAuthNoPriv', (1,3,6)) # v2c
        if self.v3:
            config.addRoUser(snmpEngine, 3, self.user_name, self.user_security_level, (1,3,6)) # v3
            config.addRwUser(snmpEngine, 3, self.admin_name, self.admin_security_level, (1,3,6)) # v3

        # SNMP context
        snmpContext = context.SnmpContext(snmpEngine)

        # Apps registration
        cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
        cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
        cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
        cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)
        
        self.engine = snmpEngine
        
    def _worker(self):
        if self.ipv4:
            self.logger.info('snmp server listening at %s:%s' % (self.host, self.port))
        if self.ipv6:
            self.logger.info('snmp server listening at %s:%s' % (self.ipv6_host, self.port))
        self.engine.transportDispatcher.jobStarted(1) # this job would never finish
        self.engine.transportDispatcher.runDispatcher()
        self.logger.info('snmp server exited')

    def close(self):
        self.engine.transportDispatcher.jobFinished(1)
        self.thread.join(timeout=2)
        if self.thread.is_alive():
            self.logger.critical('server thread still running')
        
        
        

