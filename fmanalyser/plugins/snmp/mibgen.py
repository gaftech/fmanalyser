#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module provides functions to generate the MIB file and the pysnmp python mib file.
"""
from fmanalyser.plugins.snmp import MIB_DIR
import datetime
import fmanalyser
import os.path
import shlex
import subprocess

#PYSNMP_BUILD_COMMAND = 'build-pysnmp-mib'

MAIN_TEMPLATE = """FMANALYSER-MIB DEFINITIONS ::= BEGIN


IMPORTS
    enterprises, MODULE-IDENTITY, OBJECT-TYPE,
        Integer32, Unsigned32
        FROM SNMPv2-SMI;

fmanalyser MODULE-IDENTITY
    LAST-UPDATED    "%(now)s"
    ORGANIZATION    "Gaftech"
    CONTACT-INFO    "gabriel@gaftech.fr"
    DESCRIPTION     "The MIB module for fmanalyser snmp plugin"
    REVISION        "%(now)s"
    DESCRIPTION     "auto-generated revision with fmanalyser %(version)s"
    ::= { gaftech 1 }

gaftech OBJECT IDENTIFIER ::= { enterprises 999999 }

software OBJECT IDENTIFIER ::= { fmanalyser 1 }

softVersion OBJECT-TYPE
    SYNTAX        OCTET STRING
    MAX-ACCESS    read-only
    STATUS        current
    DESCRIPTION   "fmanalyser software version"
    ::= { software 0 }


device OBJECT IDENTIFIER ::= { fmanalyser 2 }

online OBJECT-TYPE
    SYNTAX        Integer32(0..1)
    MAX-ACCESS    read-only
    STATUS        current
    DESCRIPTION
        "The device online/offline status."
    ::= { device 1 }

analyser OBJECT IDENTIFIER ::= { fmanalyser 3 }

channelTable OBJECT-TYPE
    SYNTAX       SEQUENCE OF channelEntry
    MAX-ACCESS   not-accessible
    STATUS       current
    DESCRIPTION  "channel table"
    ::= { analyser 1 }
    
channelEntry OBJECT-TYPE
    SYNTAX       ChannelEntry
    MAX-ACCESS   not-accessible
    STATUS       current
    DESCRIPTION  "entry in channel table"
    INDEX        { channelIndex }
    ::= { channelTable 1 }

ChannelEntry ::= SEQUENCE {
    channelIndex            Unsigned32
    -- other columns in the table
    }

END
"""


def get_context(**kwargs):
    context = {
        'version': fmanalyser.__version__,
        'now': datetime.datetime.utcnow().strftime('%Y%m%d%H%MZ'),
    }
    context.update(kwargs)
    return context



def generate(mibfile=None,
             make_mibfile=True,
             pysnmpfile=None,
             make_pysnmpfile=True,
             ):

    if mibfile is None:
        mibfile = os.path.join(MIB_DIR, 'FMANALYSER-MIB')
    mibfile = os.path.abspath(mibfile)
    if pysnmpfile is None:
        pysnmpfile = os.path.join(MIB_DIR, 'FMANALYSER-MIB.py')
    pysnmpfile = os.path.abspath(pysnmpfile)
    
    if make_mibfile:
        mib_output = MAIN_TEMPLATE % get_context()
        with open(mibfile, 'w') as fp:
            fp.write(mib_output)
    
    if make_pysnmpfile:
        cmd = ['sh',
               os.path.join(os.path.dirname(__file__), 'mib2py.sh'),
               mibfile,
               pysnmpfile]
        subprocess.check_call(cmd)
#        command = 
#        command = shlex.split(command)
#        smidump = 'smidump -l3 -f python %s' % mibfile
#        smiparts = shlex.split(smidump)
#        smioutput = subprocess.check_output(smiparts)
#        
#        0
        
#        command = 'smidump -l3 -f python %s | libsmi2pysnmp > %s' %(
#            mibfile, pysnmpfile)
#        
##        command = '%s -o %s %s' % (PYSNMP_BUILD_COMMAND, pysnmpfile, mibfile)
#        check_call(shlex.split(command), shell=True)



if __name__ == '__main__':
    generate()