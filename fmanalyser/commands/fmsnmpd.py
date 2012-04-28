# -*- coding: utf-8 -*-

from ..utils.command import BaseCommand
from ..snmp.server import SnmpServer
from ..conf import fmconfig 
import sys

class Command(BaseCommand):
    
#    def __init__(self, *args, **kwargs):
#        super(Command, self).__init__(*args, **kwargs)
        
    
    def execute(self):
        self.server = SnmpServer(
            verbosity = self.options.verbosity,
            **fmconfig['snmpd']
        )
        self.server.run()
        
#    def connect_signals(self):
#        pass 

    def stop(self, *args, **kwargs):
        self.server.stop()
        super(Command, self).stop(*args, **kwargs)
        

def main():
    sys.exit(Command().run())

if __name__ == '__main__':
    main()