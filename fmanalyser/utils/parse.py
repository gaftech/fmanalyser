# -*- coding: utf-8 -*-
"""This module provides helper to convert and scale input values (from user or device).
"""

def parse(line):
    """clean a received line """
    return line.strip()

def remove_unit(value, default=''):
    if isinstance(value, basestring):
        try:
            value = value.split(None, 1)[0]
        except IndexError:
            value = default
    return value

def parse_int(value):
    return int(remove_unit(value, 0))

def parse_float(value):
    return float(remove_unit(value, 0))

def parse_float_to_int(value, coef):
    return int(parse_float(value)*coef)

def parse_carrier_frequency(raw_value):
    """From a string representing a frequency in MHz, returns the kHz value as an integer
    
    Numeric value should also be accepted but as it is not this function primary goal, nothing particular
    is done for correctly rounding it.
    
    >>> parse_carrier_frequency('107.7 MHz')
    107700
    >>> parse_carrier_frequency('89.2')
    89200
    >>> parse_carrier_frequency('078.5 MHz\\r\\n')
    78500
    >>> parse_carrier_frequency(108)
    108000
    >>> parse_carrier_frequency(8.9925)
    8992
    """
    return parse_float_to_int(raw_value, 1000)

def parse_deviation_level(raw_value):
    """From a string representing a frequency in kHz, returns the float value."""
    return parse_float(raw_value)

def iter_histogram_data(lines):
    for line in lines:
        yield tuple(int(raw) for raw in line.split(';')) 

def parse_histogram_data(lines):
    return tuple(iter_histogram_data(lines))

def iter_rds_groups(lines):
    for line in lines:
        i, v = line.split(';')
        yield i.strip(), parse_float(v)









