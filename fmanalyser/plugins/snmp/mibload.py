# -*- coding: utf-8 -*-
"""This module provides functions to populate the pysnmp `mibBuilder`
"""
import fmanalyser
from . import MIB_DIR, adapters
from pysnmp.smi import builder
#from pysnmp.proto.rfc1902 import Integer32, OctetString
from .adapters import make_option_adapter
from . import FMANALYSER_MIB_NAME as FMMIB

def populate_builder(controller, mibBuilder):
    
    # Adding ou mib path
    sources = mibBuilder.getMibSources() + (builder.DirMibSource(MIB_DIR),)
    mibBuilder.setMibSources(*sources)
    
    (MibScalarInstance, Integer32, ) = mibBuilder.importSymbols('SNMPv2-SMI',
        'MibScalarInstance', 'Integer32', )

    ##### BASE CLASSES AND FACTORIES
    class Getter(MibScalarInstance, object):
        
        @classmethod
        def export(cls, name, syntax, instance_id=(0,)):
            if isinstance(instance_id, int):
                instance_id = (instance_id,)
            base, = mibBuilder.importSymbols(FMMIB, name)   
            mibBuilder.exportSymbols(FMMIB,
                cls(base.name, instance_id, syntax)
            )
        
        def readGet(self, *args, **kwargs):
            name, val = MibScalarInstance.readGet(self, *args, **kwargs)
            return name, val.clone(self.getCurrentValue())        
        
        def getCurrentValue(self):
            raise NotImplementedError()
    
    class AttGetter(Getter):
        
        attowner = None
        attname = None
        
        @classmethod
        def factory(cls, attname, **kwargs):
            classname = '%sGetter' % attname.title()
            kwargs['attname'] = attname
            return type(classname, (cls, object), kwargs)
        
        def getCurrentValue(self):
            value = getattr(self.getOwner(), self.attname)
            if callable(value):
                value = value
            return value
    
        def getOwner(self):
            if self.attowner is not None:
                return self.attowner
            raise NotImplementedError("%s instance doesn't define an attribute owner")
    

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
    class VariableValueGetter(Getter):
        
        variable = None
        adapter = None
        
        @classmethod
        def factory(cls, variable):
            classname = '%sValueGetter' % variable.key.title()
            kwargs = {
                'variable': variable,
                'adapter': make_option_adapter(variable.validator.get_option('ref')),
            }
            return type(classname, (cls, object), kwargs)
        
        @classmethod
        def export(cls, name, channel_index):
            return super(VariableValueGetter, cls).export(name,
                syntax=cls.adapter.get_syntax_instance(mibBuilder),
                instance_id = channel_index,
            )
        
        def getCurrentValue(self):
            value = self.variable.get_value()
            value = self.adapter.get_snmp_value(value)
            return value
        
    channelName,  = mibBuilder.importSymbols(FMMIB, 'channelName',)
    for i, channel in enumerate(controller.channels, start=1):
        mibBuilder.exportSymbols(FMMIB,
            MibScalarInstance(channelName.name, (i,), channelName.syntax.clone(channel.name)),
        )
        for variable in channel.get_variables():
            key_symbol, = mibBuilder.importSymbols(FMMIB, '%sKey' % variable.key)
            mibBuilder.exportSymbols(FMMIB,
                MibScalarInstance(key_symbol.name, (i,), key_symbol.syntax.clone(variable.key))
            )
            VariableValueGetter.factory(variable).export('%sValue' % variable.key, i)
            
            for option in variable.validator.get_options():
                adapter = adapters.make_option_adapter(option) 
                value = getattr(variable.validator, option.attname)
                value = adapter.get_snmp_value(value)
                symbol, = mibBuilder.importSymbols(FMMIB, '%s%s' % (variable.key, option.attname.title()))
                mibBuilder.exportSymbols(FMMIB,
                    MibScalarInstance(symbol.name, (i,), symbol.syntax.clone(value))                         
                )
                

        
    
    
    
    
    
    
    
    
    
    
    
