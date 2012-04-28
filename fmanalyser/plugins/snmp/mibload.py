# -*- coding: utf-8 -*-
"""This module provides functions to populate the pysnmp `mibBuilder`
"""
import fmanalyser
from . import MIB_DIR
from pysnmp.smi import builder
from pysnmp.proto.rfc1902 import OctetString, Integer

FMMIB = "FMANALYSER-MIB"



def populate_builder(controller, mibBuilder):
    
    # Adding ou mib path
    sources = mibBuilder.getMibSources() + (builder.DirMibSource(MIB_DIR),)
    mibBuilder.setMibSources(*sources)
    
    MibScalarInstance, = mibBuilder.importSymbols('SNMPv2-SMI', 'MibScalarInstance')

    ##### BASE CLASSES AND FACTORIES
    class Getter(MibScalarInstance):
        
        @classmethod
        def export(cls, name, syntax):
            base, = mibBuilder.importSymbols(FMMIB, name)   
            mibBuilder.exportSymbols(FMMIB,
                cls(base.name, (0,), syntax)
            )
        
        def readGet(self, *args, **kwargs):
            name, val = MibScalarInstance.readGet(self, *args, **kwargs)
            return name, val.clone(self.getCurrentValue())        
        
        def getCurrentValue(self):
            raise NotImplementedError()
    
    class AttGetter(Getter):
        
        attname = None
        
        @classmethod
        def factory(cls, attname):
            classname = '%sGetter' % attname.title()
            return type(classname, (cls, object), {'attname':attname})
        
        def getCurrentValue(self):
            value = getattr(self.getOwner(), self.attname)
            if callable(value):
                value = value
            return value
    
        def getOwner(self):
            raise NotImplementedError()
    

    ##### SOFTWARE INFORMATIONS
    softVersion, = mibBuilder.importSymbols(FMMIB, 'softVersion')
    mibBuilder.exportSymbols(FMMIB,
        MibScalarInstance(softVersion.name, (0,), softVersion.syntax.clone(fmanalyser.__version__))
    )
    
    ##### DEVICE CLIENT ACCESSORS
    class DeviceAttGetter(AttGetter):
        def getOwner(self):
            return controller.device

    DeviceOnline = DeviceAttGetter.factory('online').export('online', Integer())


    


    
    
