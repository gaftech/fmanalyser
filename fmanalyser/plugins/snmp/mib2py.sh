#!/bin/sh
smidump -l3 -f python "$1" | libsmi2pysnmp > "$2"
