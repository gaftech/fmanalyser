# -*- coding: utf-8 -*-
"""This module provides functions to populate the pysnmp `mibBuilder`
"""
import fmanalyser
from . import MIB_DIR
from pysnmp.smi import builder
from pysnmp.proto.rfc1902 import Integer32, OctetString

FMMIB = "FMANALYSER-MIB"



def populate_builder(controller, mibBuilder):
    
    # Adding ou mib path
    sources = mibBuilder.getMibSources() + (builder.DirMibSource(MIB_DIR),)
    mibBuilder.setMibSources(*sources)
    
    (MibScalarInstance, ) = mibBuilder.importSymbols('SNMPv2-SMI',
        'MibScalarInstance')

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
    DeviceAttGetter.factory('online').export('online', Integer32())

    ##### CHANNELS
#    class ChannelAttGetter(AttGetter):
#        def readGet(self, *args, **kwargs):
#            return AttGetter.readGet(self, *args, **kwargs)
#    ChannelAttGetter.factory('name').export('channelName', OctetString())
    channelName, channelFreq, varName = mibBuilder.importSymbols(FMMIB, 'channelName', 'frequency', 'channelVariableName')
    for i, channel in enumerate(controller.channels, start=1):
        freqVar = channel.get_variable('frequency')
        mibBuilder.exportSymbols(FMMIB,
            MibScalarInstance(channelName.name, (i,), channelName.syntax.clone(channel.name)),
            MibScalarInstance(channelFreq.name, (i,), channelFreq.syntax.clone(channel.frequency or 0)),
            MibScalarInstance(varName.name, (i,1), varName.syntax.clone(freqVar.key)),
        )
        
        
#        for j, var in enumerate(channel.get_variables(), start=1):
#            mibBuilder.exportSymbols(FMMIB,
#                MibScalarInstance(channelName.name, (i,), channelName.syntax.clone(channel.name)),
#                MibScalarInstance(channelFreq.name, (i,), channelFreq.syntax.clone(channel.frequency or 0)),
#            )            
        
        
#        mibBuilder.exportSymbols(FMMIB, ChannelNameGetter(channelName.name, (0,), OctetString()))
        
    
    
    
    
    
    
    
    
    
    
    
