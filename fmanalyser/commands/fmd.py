# -*- coding: utf-8 -*-

from fmanalyser.conf import fmconfig
from fmanalyser.device.controllers import create_controllers
from fmanalyser.device.worker.tasks import Sleep
from fmanalyser.exceptions import CommandError
from fmanalyser.plugins.base import create_plugins
from fmanalyser.utils.command import BaseCommand
from optparse import make_option
import sys

class Command(BaseCommand):
    
    base_options = BaseCommand.base_options + (
        make_option('--sleep', default=1, type='float',
                    help='time to sleep (s) between two probing loops'),
    )
    
    def stop(self, *args, **kwargs):
        super(Command, self).stop(*args, **kwargs)
        self._stop_workers()
    
    def execute(self):
        self.controllers = create_controllers(fmconfig)
        if not self.controllers:
            raise CommandError('No controller enabled')
        self.plugins = create_plugins(self, fmconfig)
        try:
            self._start_plugins()
            while not self._stop.is_set():
                self._check_workers()
                self.short_sleep()
        finally:
            self._stop_workers()
            self._stop_plugins()

    def _start_plugins(self):
        for plugin in self.plugins:
            if plugin.enabled:
                plugin.start()        

    def _stop_plugins(self):
        for plugin in self.plugins:
            try:
                plugin.close()
            except:
                self.logger.critical('error while stopping plugin', exc_info = True)

    def _check_workers(self):
        for controller in self.controllers:
            controller.check_worker()
            if controller.should_enqueue():
                controller.enqueue_updates()
                controller.worker.enqueue_task(Sleep(self.options.sleep))
            
    def _start_workers(self):
        for controller in self.controllers:
            controller.start_worker()

    def _stop_workers(self):
        for controller in self.controllers:
            try:
                controller.stop_worker()
            except:
                self.logger.critical('error while stopping worker', exc_info=True)

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
