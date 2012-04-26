# -*- coding: utf-8 -*-

from ..datastructures.ordereddict import OrderedDict
from ConfigParser import ConfigParser
from StringIO import StringIO

def parser_to_dict(parser, dict_type):
    d = dict_type()
    for section in parser.sections():
        d[section] = dict_type()
        for option in parser.options(section):
            d[section][option] = parser.get(section, option)
    return d

def ini_files_dict(files, dict_type = OrderedDict):
    parser = ConfigParser(dict_type = dict_type)
    parser.read(*files)
    return parser_to_dict(parser, dict_type)

def ini_string_dict(s, dict_type = OrderedDict):
    parser = ConfigParser(dict_type = dict_type)
    parser.readfp(StringIO(s))
    return parser_to_dict(parser, dict_type)


    
    