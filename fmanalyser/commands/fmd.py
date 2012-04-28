# -*- coding: utf-8 -*-

from fmanalyser import client
from fmanalyser.conf import fmconfig
from fmanalyser.exceptions import MissingSection
from fmanalyser.models.channel import create_config_channels
from fmanalyser.utils.command import BaseCommand
from fmanalyser.utils.plugin import create_plugins
from fmanalyser.models.analyser import Analyser
import sys
from optparse import make_option
from fmanalyser.settings import WATCHER_SLEEP_TIME

class Command(BaseCommand):
    
    base_options = BaseCommand.base_options + (
        make_option('--sleep', default=0.1, type='float',
                    help='time to sleep (s) between two probing loops'),
    )
    
    def _stop_worker(self):
        if self.worker is not None and not self.worker.stopped:
            self.worker.stop()
    
    def stop(self, *args, **kwargs):
        super(Command, self).stop(*args, **kwargs)
        self._stop_worker()
    
    def execute(self):
        self.config = fmconfig
        self.device = client.P175(**fmconfig['device'])
        self.worker = client.Worker(device=self.device)
        self.channels = create_config_channels(fmconfig)
        self.analyser = Analyser(client_worker=self.worker, channels=self.channels)

        if not self.channels:
            raise MissingSection('no channel configured')

        self.plugins = create_plugins(self, fmconfig)
        try:
            for plugin in self.plugins:
                if not plugin.enabled:
                    continue
                plugin.start()            
            
            self.worker.run()
            last_task = None
            while self.worker.is_alive() and not self._stop.is_set():
                if last_task is None or last_task.stopped:
                    if last_task is not None:
                        self.logger.debug('sleeping %s s' % self.options.sleep)
                        self._stop.wait(self.options.sleep)                        
                    last_task = self.analyser.enqueue_updates()
                    self.logger.debug('waiting for task %s' % last_task)
                self._stop.wait(WATCHER_SLEEP_TIME)
                
                
                

        finally:
            self._stop_worker()
            for plugin in self.plugins:
                try:
                    plugin.close()
                except:
                    self.logger.critical('error while stopping plugin', exc_info = True)


#    def get_device(self):
#        return self.device
            

def main():
    sys.exit(Command().run())

if __name__ == '__main__':
    main()
