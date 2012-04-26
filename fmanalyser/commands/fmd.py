# -*- coding: utf-8 -*-

from .. import client
from ..conf import fmconfig
from ..models.channel import create_config_channels
from ..utils.command import BaseCommand
from ..utils.plugin import plugins
from ..models.analyser import Analyser
import sys
from optparse import make_option

class Command(BaseCommand):
    
    base_options = BaseCommand.base_options + (
        make_option('--sleep', default=0.1, type='float',
                    help='time to sleep (s) between two probing loops'),
    )
    
#    def __init__(self, *args, **kwargs):
#        super(Command, self).__init__(*args, **kwargs)
    
    def _stop_worker(self):
        if self.worker is not None and not self.worker.stopped:
            self.worker.stop()
    
    def stop(self, *args, **kwargs):
        super(Command, self).stop(*args, **kwargs)
        self._stop_worker()
    
    def execute(self):
        self.device = client.P175(**fmconfig['device'])
        self.worker = client.Worker(device=self.device)
        self.channels = create_config_channels(fmconfig)
        self.analyser = Analyser(client_worker=self.worker, channels=self.channels)
        
        plugins.populate_from_config(fmconfig)
        
        try:
            self.worker.run()
            while self.worker.is_alive() and not self._stop.is_set():
                task = self.analyser.enqueue_updates()
                self.logger.debug('waiting for task %s' % task)
                task.wait(blocking=False)
                self.logger.debug('sleeping %s s' % self.options.sleep)
                self._stop.wait(self.options.sleep)
        finally:
            self._stop_worker()
        
        
        
        
        
        
        




def main():
    sys.exit(Command().run())

if __name__ == '__main__':
    main()