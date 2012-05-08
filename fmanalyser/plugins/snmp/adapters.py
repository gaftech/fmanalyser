# -*- coding: utf-8 -*-

from ...conf import options
from . import render_template, OPTION_TEMPLATE, FMANALYSER_MIB_NAME

class BaseOptionAdapter(object):
    """Helper to represent an :class:`fmanalyser.utils.conf.options.Option`
    instance as a MIB leaf.
    """
    null_value = None
    syntax_mib = 'SNMPv2-SMI'
    
    def __init__(self, option):
        self.option = option
    
    def __str__(self):
        return '%s: %s.%s' % (self.__class__.__name__,
                             self.option.holder.__name__,
                             self.option.attname)
    
    # MIB file generation utilities
    def get_syntax(self):
        return self.syntax
    
    def render_mib_object(self, **context):
        return render_template(OPTION_TEMPLATE,
            key = self.option.attname,
            Key = self.option.attname.title(),
            syntax = self.get_syntax(),
            **context
        )

    # Pysnmp mib loading utilities
    def get_syntax_instance(self, mibBuilder):
        symbol, = mibBuilder.importSymbols(self.syntax_mib, self.get_syntax())
        return symbol()
    
    def get_snmp_value(self, value):
        if value is None:
            return self.get_null_value()
        return value

    def get_null_value(self):
        if self.null_value is not None:
            return self.null_value
        try:
            return self.option.get_null_value()
        except (AttributeError, NotImplementedError):
            raise NotImplementedError('%s: adapter or its associated option must define a null_value attribute' % self)

class OptionAdapter(BaseOptionAdapter):
    syntax = 'OCTET STRING'

class IntOptionAdapter(BaseOptionAdapter):
    syntax = 'Integer32'

class BoolOptionAdapter(BaseOptionAdapter):
    syntax = 'TruthValue'
    syntax_mib = 'SNMPv2-TC'

    def get_snmp_value(self, value):
        return {True: 1, False: 2}[bool(value)]

class kHzOptionAdapter(BaseOptionAdapter):
    syntax = 'DeviationLevel'
    syntax_mib = FMANALYSER_MIB_NAME
    null_value = 0
    
    def get_snmp_value(self, value):
        value = super(kHzOptionAdapter, self).get_snmp_value(value)
        return self.option.to_int(value)

def make_option_adapter(option, *args, **kwargs):
    if isinstance(option, options.kHzOption):
        cls = kHzOptionAdapter
    else:
        cls = {
            str: OptionAdapter,
            int: IntOptionAdapter,
            bool: BoolOptionAdapter,
        }[option.value_type]
    return cls(option, *args, **kwargs)