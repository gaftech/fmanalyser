# PySNMP SMI module. Autogenerated from smidump -f python FMANALYSER-MIB
# by libsmi2pysnmp-0.1.3 at Sun Apr 29 11:28:05 2012,
# Python version (2, 6, 7, 'final', 0)

# Imports

( Integer, ObjectIdentifier, OctetString, ) = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
( NamedValues, ) = mibBuilder.importSymbols("ASN1-ENUMERATION", "NamedValues")
( ConstraintsIntersection, ConstraintsUnion, SingleValueConstraint, ValueRangeConstraint, ValueSizeConstraint, ) = mibBuilder.importSymbols("ASN1-REFINEMENT", "ConstraintsIntersection", "ConstraintsUnion", "SingleValueConstraint", "ValueRangeConstraint", "ValueSizeConstraint")
( ModuleCompliance, ObjectGroup, ) = mibBuilder.importSymbols("SNMPv2-CONF", "ModuleCompliance", "ObjectGroup")
( Bits, Integer32, Integer32, ModuleIdentity, MibIdentifier, MibScalar, MibTable, MibTableRow, MibTableColumn, TimeTicks, Unsigned32, enterprises, ) = mibBuilder.importSymbols("SNMPv2-SMI", "Bits", "Integer32", "Integer32", "ModuleIdentity", "MibIdentifier", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "TimeTicks", "Unsigned32", "enterprises")

# Objects

gaftech = MibIdentifier((1, 3, 6, 1, 4, 1, 999999))
fmanalyser = ModuleIdentity((1, 3, 6, 1, 4, 1, 999999, 1)).setRevisions(("2012-04-29 09:28",))
if mibBuilder.loadTexts: fmanalyser.setOrganization("Gaftech")
if mibBuilder.loadTexts: fmanalyser.setContactInfo("gabriel@gaftech.fr")
if mibBuilder.loadTexts: fmanalyser.setDescription("The MIB module for fmanalyser snmp plugin")
device = MibIdentifier((1, 3, 6, 1, 4, 1, 999999, 1, 1))
online = MibScalar((1, 3, 6, 1, 4, 1, 999999, 1, 1, 2), Integer32().subtype(subtypeSpec=ValueRangeConstraint(0, 1))).setMaxAccess("readonly")
if mibBuilder.loadTexts: online.setDescription("The device online/offline status.")
analyser = MibIdentifier((1, 3, 6, 1, 4, 1, 999999, 1, 2))
channels = MibIdentifier((1, 3, 6, 1, 4, 1, 999999, 1, 2, 1))
channelTable = MibTable((1, 3, 6, 1, 4, 1, 999999, 1, 2, 1, 1))
if mibBuilder.loadTexts: channelTable.setDescription("channel table")
channelEntry = MibTableRow((1, 3, 6, 1, 4, 1, 999999, 1, 2, 1, 1, 1)).setIndexNames((0, "FMANALYSER-MIB", "channelIndex"))
if mibBuilder.loadTexts: channelEntry.setDescription("entry in channel table")
channelIndex = MibTableColumn((1, 3, 6, 1, 4, 1, 999999, 1, 2, 1, 1, 1, 1), Unsigned32()).setMaxAccess("noaccess")
if mibBuilder.loadTexts: channelIndex.setDescription("channel index")
channelName = MibTableColumn((1, 3, 6, 1, 4, 1, 999999, 1, 2, 1, 1, 1, 2), OctetString()).setMaxAccess("readonly")
if mibBuilder.loadTexts: channelName.setDescription("channel identifer")
channelRefFrequency = MibTableColumn((1, 3, 6, 1, 4, 1, 999999, 1, 2, 1, 1, 1, 3), Unsigned32()).setMaxAccess("readonly")
if mibBuilder.loadTexts: channelRefFrequency.setDescription("configured channel frequency")
channelVariables = MibIdentifier((1, 3, 6, 1, 4, 1, 999999, 1, 2, 2))
rfChannelVariable = MibIdentifier((1, 3, 6, 1, 4, 1, 999999, 1, 2, 2, 1))
frequencyChannelVariable = MibIdentifier((1, 3, 6, 1, 4, 1, 999999, 1, 2, 2, 2))
qualityChannelVariable = MibIdentifier((1, 3, 6, 1, 4, 1, 999999, 1, 2, 2, 3))
rdsChannelVariable = MibIdentifier((1, 3, 6, 1, 4, 1, 999999, 1, 2, 2, 4))
pilotChannelVariable = MibIdentifier((1, 3, 6, 1, 4, 1, 999999, 1, 2, 2, 5))
software = MibIdentifier((1, 3, 6, 1, 4, 1, 999999, 1, 8))
softVersion = MibScalar((1, 3, 6, 1, 4, 1, 999999, 1, 8, 1), OctetString()).setMaxAccess("readonly")
if mibBuilder.loadTexts: softVersion.setDescription("fmanalyser software version")
conformance = MibIdentifier((1, 3, 6, 1, 4, 1, 999999, 1, 9))
compliances = MibIdentifier((1, 3, 6, 1, 4, 1, 999999, 1, 9, 1))
groups = MibIdentifier((1, 3, 6, 1, 4, 1, 999999, 1, 9, 2))

# Augmentions

# Groups

staticValues = ObjectGroup((1, 3, 6, 1, 4, 1, 999999, 1, 9, 2, 1)).setObjects(*(("FMANALYSER-MIB", "channelName"), ("FMANALYSER-MIB", "softVersion"), ) )
if mibBuilder.loadTexts: staticValues.setDescription("static informations")
liveValues = ObjectGroup((1, 3, 6, 1, 4, 1, 999999, 1, 9, 2, 2)).setObjects(*(("FMANALYSER-MIB", "online"), ) )
if mibBuilder.loadTexts: liveValues.setDescription("live informations")
cachedValues = ObjectGroup((1, 3, 6, 1, 4, 1, 999999, 1, 9, 2, 3)).setObjects(*(("FMANALYSER-MIB", "channelRefFrequency"), ) )
if mibBuilder.loadTexts: cachedValues.setDescription("cached acquired data")

# Compliances

mibCompliance = ModuleCompliance((1, 3, 6, 1, 4, 1, 999999, 1, 9, 1, 1)).setObjects(*(("FMANALYSER-MIB", "staticValues"), ("FMANALYSER-MIB", "liveValues"), ("FMANALYSER-MIB", "cachedValues"), ) )
if mibBuilder.loadTexts: mibCompliance.setDescription("our compliance")

# Exports

# Module identity
mibBuilder.exportSymbols("FMANALYSER-MIB", PYSNMP_MODULE_ID=fmanalyser)

# Objects
mibBuilder.exportSymbols("FMANALYSER-MIB", gaftech=gaftech, fmanalyser=fmanalyser, device=device, online=online, analyser=analyser, channels=channels, channelTable=channelTable, channelEntry=channelEntry, channelIndex=channelIndex, channelName=channelName, channelRefFrequency=channelRefFrequency, channelVariables=channelVariables, rfChannelVariable=rfChannelVariable, frequencyChannelVariable=frequencyChannelVariable, qualityChannelVariable=qualityChannelVariable, rdsChannelVariable=rdsChannelVariable, pilotChannelVariable=pilotChannelVariable, software=software, softVersion=softVersion, conformance=conformance, compliances=compliances, groups=groups)

# Groups
mibBuilder.exportSymbols("FMANALYSER-MIB", staticValues=staticValues, liveValues=liveValues, cachedValues=cachedValues)

# Compliances
mibBuilder.exportSymbols("FMANALYSER-MIB", mibCompliance=mibCompliance)
