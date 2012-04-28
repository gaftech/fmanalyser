# PySNMP SMI module. Autogenerated from smidump -f python FMANALYSER-MIB
# by libsmi2pysnmp-0.0.7-alpha at Fri Apr 27 10:36:57 2012,
# Python version sys.version_info(major=2, minor=7, micro=2, releaselevel='final', serial=0)

# Imported just in case new ASN.1 types would be created
from pyasn1.type import constraint, namedval

# Imports

( Integer, ObjectIdentifier, OctetString, ) = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
( Bits, Integer32, ModuleIdentity, MibIdentifier, MibScalar, MibTable, MibTableRow, MibTableColumn, TimeTicks, enterprises, ) = mibBuilder.importSymbols("SNMPv2-SMI", "Bits", "Integer32", "ModuleIdentity", "MibIdentifier", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "TimeTicks", "enterprises")

# Objects

gaftech = MibIdentifier((1, 3, 6, 1, 4, 1, 999999))
fmanalyser = ModuleIdentity((1, 3, 6, 1, 4, 1, 999999, 1)).setRevisions(("1912-04-27 08:36",))

# Augmentions

# Exports

# Module identity
mibBuilder.exportSymbols("FMANALYSER-MIB", PYSNMP_MODULE_ID=fmanalyser)

# Objects
mibBuilder.exportSymbols("FMANALYSER-MIB", gaftech=gaftech, fmanalyser=fmanalyser)
