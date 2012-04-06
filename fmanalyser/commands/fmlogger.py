#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ..client import MODE_CHOICES
from ..client.tasks import ReadChannelValues, WriteChannelValue
from ..client.worker import Worker
from ..utils.command import BaseCommand
from ..values.channel import Channel
from ..values.signals import ValueChangeEvent
from optparse import OptionGroup, OptionConflictError
import logging
import sys
import time

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
        group.add_option('--mode', '-m', type='choice',
            choices = MODE_CHOICES,
            help='set device mode {mes|rds|stereo}')
        group.add_option('--mes',
            action='store_const', dest='mode', const='mes',
            help='set measurement mode')
        group.add_option('--rdsm', '--rds-mode', 
            action='store_const', dest='mode', const='rds',
            help='set rds mode')
        group.add_option('--stereo',
            action='store_const', dest='mode', const='stereo',
            help='set stereo mode')
        # measurements
        for descriptor in Channel.iter_descriptors():
            if not descriptor.readable:
                continue
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
        
        ValueChangeEvent.connect(self.on_value_changed)
        
        channel = self.make_channel()
        
        self.worker.run()
        
        mode = self.options.mode
        if mode is not None:
            mode_variable = channel.get_variable('mode')
            mode_variable.set_command(mode)
            self.worker.enqueue(WriteChannelValue, variable=mode_variable)
        freq = self.options.set_freq
        if freq is not None:
            freq_variable = channel.get_variable('frequency')
            freq_variable.set_command(freq)
            self.worker.enqueue(WriteChannelValue, variable=freq_variable)
        while self.worker.is_alive():
            task = self.worker.enqueue(ReadChannelValues, channel=channel)
            task.wait(blocking=False, timeout=2)
            time.sleep(self.options.sleep)

    def make_channel(self):
        channel = Channel()
        for variable in channel.get_variables():
            enabled = getattr(self.options, variable.descriptor.key)
            variable.enabled = enabled
        return channel

    def on_value_changed(self, sender, event):
        message = self.format_event(event)
        self.log_data(message)
    
    def format_event(self, event):
        descriptor = event.sender.descriptor
        return '%s: %s' % (descriptor.key, descriptor.format_value(event.new_value)) 

    def log_data(self, message):
        self.datalogger.info(message)

def main():
    sys.exit(Command().run())

if __name__ == '__main__':
    main()

