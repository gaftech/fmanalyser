#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ..client import MODE_CHOICES
from ..models.channel import Channel
from ..models.signals import ValueChangeEvent
from ..utils.command import BaseCommand
from optparse import OptionGroup, OptionConflictError
import logging
import sys
import time
from fmanalyser.models.signals import value_changed
from fmanalyser.models.analyser import Analyser
from fmanalyser.utils.parse import parse_carrier_frequency
from fmanalyser.utils.datastructures import NOTSET

class Command(BaseCommand):
    
    def make_option_groups(self, parser):
        groups = super(Command, self).make_option_groups(parser)
        # Runtime options
        runtime_group = OptionGroup(parser, 'runtime options')
        runtime_group.add_option('--sleep', default=1, type='float',
            help='time to sleep (s) between two probing loops')
        # Channel options
        channel_group = OptionGroup(parser, 'channel options')
        self._append_channel_options(channel_group)
        groups.append(channel_group)
        # Data output options
        data_group = OptionGroup(parser, 'data logging options')
        data_group.add_option('--file',dest='datafile',
                             help="File to store data in")
        groups.append(data_group)
        return groups
    
    def _append_channel_options(self, group):
        # initial frequency
        group.add_option('--set-freq', '-F',
            help='set initial frequency (MHz)')
        # measurements
        for descriptor in Channel.iter_descriptors():
            longopt = '--%s' % descriptor.key
            shortopt = None
            if descriptor.short_key is not None:
                shortopt = '-%s' % descriptor.short_key
            kwargs= {
                'dest': descriptor.key,
                'action': 'store_true',
                'help': 'enable %s measurement' % descriptor,
            }
            try:
                group.add_option(longopt, shortopt, **kwargs)
            except OptionConflictError:
                group.add_option(longopt, **kwargs)
        return group
    
    def configure_logging(self):
        super(Command, self).configure_logging()
        datalogger_name = '%s.data' % self.get_logger_name()
        datalogger = logging.getLogger(datalogger_name)
        datalogger.propagate = False
        datalogger.setLevel(logging.DEBUG)
        data_streamhandler = logging.StreamHandler(sys.stdout)
        datalogger.addHandler(data_streamhandler)
        if self.options.datafile:
            data_filehandler = logging.FileHandler(self.options.datafile)
            datalogger.addHandler(data_filehandler)
        self.datalogger = datalogger
    
    def stop(self, signal, frame):
        self.logger.info(u"stopping on signal %s..." % signal)
        if hasattr(self, 'worker'):
            self.worker.stop()
    
    def execute(self):
        
        value_changed.connect(self._on_value_changed)
        
        channel = self._make_channel()
        analyser = Analyser(client_worker=self.worker, channels=[channel])
        
        self.worker.run()
        
        while self.worker.is_alive():
            task = analyser.trigger_measurements()
            task.wait(blocking=False, timeout=2)
            time.sleep(self.options.sleep)

    def _make_channel(self):
        F = NOTSET
        if self.options.set_freq:
            F = parse_carrier_frequency(self.options.set_freq)
        channel = Channel(frequency=F)
        for variable in channel.get_variables():
            enabled = getattr(self.options, variable.descriptor.key)
            variable.enabled = enabled
        return channel

    def _on_value_changed(self, sender, event):
        message = self._format_event(event)
        self.log_data(message)
    
    def _format_event(self, event):
        descriptor = event.sender.descriptor
        return '%s: %s' % (descriptor.key,
                           descriptor.render_value(event.new_value)) 

    def log_data(self, message):
        self.datalogger.info(message)

def main():
    sys.exit(Command().run())

if __name__ == '__main__':
    main()

