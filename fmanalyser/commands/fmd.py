# -*- coding: utf-8 -*-

from fmanalyser.conf.fmconfig import fmconfig
from fmanalyser.exceptions import CommandError
from fmanalyser.models.bandscan import Bandscan
from fmanalyser.models.channel import create_config_channels
from fmanalyser.plugins.base import create_plugins
from fmanalyser.utils.command import BaseCommand
from optparse import make_option
import sys

class Command(BaseCommand):
    
    base_options = BaseCommand.base_options + (
        make_option('--sleep', default=0.1, type='float',
                    help='time to sleep (s) between two probing loops'),
    )
    
    def stop(self, *args, **kwargs):
        super(Command, self).stop(*args, **kwargs)
        self._stop_worker()
    
    def execute(self):
        self._init_worker()
        self.channels = create_config_channels(fmconfig)
        self.bandscan = Bandscan.from_config(fmconfig)

        self.plugins = create_plugins(self, fmconfig)
        try:
            for plugin in self.plugins:
                if not plugin.enabled:
                    continue
                plugin.start()            
            
            self.worker.run()
            last_task = self._enqueue_updates()
            if last_task is None:
                raise CommandError('No task configured')
            while self.worker.is_alive() and not self._stop.is_set():
                if last_task.stopped:
                    self.logger.debug('sleeping %s s' % self.options.sleep)
                    self._stop.wait(self.options.sleep)                        
                    last_task = self._enqueue_updates()
                    self.logger.debug('waiting for task %s' % last_task)
                self.short_sleep()

        finally:
            for plugin in self.plugins:
                try:
                    plugin.close()
                except:
                    self.logger.critical('error while stopping plugin', exc_info = True)

    def _enqueue_updates(self):
        task = None
        for channel in self.channels:
            task =channel.enqueue_updates(self._worker)
        if self.bandscan.enabled:
            task = self.bandscan.enqueue_update()
        return task

def main():
    sys.exit(Command().run())

if __name__ == '__main__':
    main()
