#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module provides functions to generate the MIB file and the pysnmp python mib file.
"""
from fmanalyser.exceptions import CommandError
from fmanalyser.models.channel import Channel
from fmanalyser.plugins.snmp import adapters, DEFAULT_MIB_FILE, \
    DEFAULT_PYMIB_FILE, render_template, VARIABLE_TEMPLATE, ROOT_TEMPLATE
from fmanalyser.utils.command import BaseCommand
from optparse import make_option
import datetime
import fmanalyser
import os
import shlex
import subprocess
import sys
import tempfile
from fmanalyser.utils.datastructures.ordereddict import OrderedDict


class Command(BaseCommand):
    
    base_options = BaseCommand.base_options + (
        make_option('-m', '--mibfile',
            default=DEFAULT_MIB_FILE,
            help="MIB file path (default: %s)" % DEFAULT_MIB_FILE),
        make_option('-M', '--no-mibfile', dest='make_mibfile',
            action='store_false', default=True,
            help="don't generate MIB file (is so, one must already exist)"),
        make_option('-f', '--force', action='store_true', default=False,
            help="try to force files generation if checks fail"),
        make_option('-p', '--pyfile',
            default = DEFAULT_PYMIB_FILE,
            help="compiled MIB file path (default: %s)" % DEFAULT_PYMIB_FILE),
        make_option('-P', '--no-pyfile', dest='make_pyfile',
            action='store_false', default=True,
            help="don't generate compiled MIB file"),
        make_option('-t', '--tree', action='store_true', default=False,
            help='print tree for debugging'),
    )
    
    def get_context(self, **kwargs):
        context = {
            'version': fmanalyser.__version__,
            'now': datetime.datetime.utcnow().strftime('%Y%m%d%H%MZ'),
        }
        context.update(kwargs)
        return context
    
    def render_mib(self):
        context = self.get_context()
        
        # Channel variables
        variable_outputs = [] 
        for varindex, descriptor in enumerate(Channel.get_class_descriptors(), start=1):
            option_adapters = OrderedDict(
                (k, adapters.make_option_adapter(option))
                for k, option in descriptor.validator.iter_options()
            )
            optnode = '%sOptions' % descriptor.key
            option_output = ''
            for optindex, adapter in enumerate(option_adapters.values(), start=1):
                option_output += adapter.render_mib_object(
                    index = optindex,
                    optnode = optnode,
                    varkey = descriptor.key,
                )  
            variable_output = render_template(VARIABLE_TEMPLATE,
                index = varindex,
                key = descriptor.key,
                varnode = '%sChannelVariable' % descriptor.key,
                value_syntax = option_adapters['ref'].get_syntax(),
                optnode = optnode,
                options = option_output,
            )
            variable_outputs.append(variable_output)
        context['variables'] = '\n'.join(variable_outputs)
        
        return render_template(ROOT_TEMPLATE, **context)
    
    def execute(self):
        
        # Add the virtualenv bin dir to the system path
        # in case pysnmp commands are installed there
        # and this command is not running in virtualenv
        binpath = os.path.dirname(sys.executable)
        if binpath not in os.environ['PATH'].split(':'):
            os.environ['PATH'] += ':%s' % binpath
        
        mibfile = os.path.abspath(self.options.mibfile)
        pyfile = os.path.abspath(self.options.pyfile)
        
        if self.options.make_mibfile:
            self.logger.info('generating MIB file %s' % mibfile)
            mib_output = self.render_mib()
            with open(mibfile, 'w') as fp:
                fp.write(mib_output)
        
            self.logger.info('checking MIB with smilint')
            smilint = 'smilint -sm %s' % mibfile
            self.logger.debug(smilint)
            try:
                subprocess.check_call(shlex.split(smilint))
            except subprocess.CalledProcessError, e:
                msg = "MIB file didn't validate, see output above (return code: %s)" % e.returncode
                if self.options.force:
                    self.logger.warning(msg)
                else:
                    raise CommandError(msg, errno=e.returncode)
            else:
                self.logger.info('generated MIB file is smilint-valid')
        
        if self.options.make_pyfile:
            smidump = ['smidump', '-f', 'python', '-l3']
            if self.options.force:
                smidump.append('-k')
            smidump.append(mibfile)
            self.logger.debug(' '.join(smidump))
            smidump_output = tempfile.TemporaryFile()
            try:
                subprocess.check_call(smidump, stdout=smidump_output)
            except subprocess.CalledProcessError, e:
                raise CommandError('smidump failed', errno=e.returncode)

            smidump_output.seek(0)
            smi2py = ['libsmi2pysnmp']
            self.logger.debug(' '.join(smi2py))
            smi2py_output = tempfile.TemporaryFile()
            try:
                test = os.environ['PATH']
                subprocess.check_call(smi2py, stdin=smidump_output, stdout=smi2py_output)
            except subprocess.CalledProcessError, e:
                raise CommandError('libsmi2pysnmp failed', errno=e.returncode)                
            
            self.logger.info('generating compiled MIB file %s' % pyfile)
            smi2py_output.seek(0)
            with open(pyfile, 'w') as fp:
                fp.write(smi2py_output.read())

        if self.options.tree:
            dumptree = 'smidump -f tree -k %s' % mibfile
            subprocess.check_call(shlex.split(dumptree)) 









def main():
    sys.exit(Command().run())

if __name__ == '__main__':
    main()