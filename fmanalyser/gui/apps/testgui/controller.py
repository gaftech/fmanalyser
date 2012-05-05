# -*- coding: utf-8 -*-
from fmanalyser import client
from fmanalyser.gui.apps.testgui import view
from fmanalyser.models import channel
from fmanalyser.models.analyser import Analyser
from fmanalyser.models.signals import value_changed
from fmanalyser.utils.command import BaseCommand
from fmanalyser.utils.log import Loggable
from fmanalyser.utils.parse import parse_carrier_frequency
from pydispatch.dispatcher import liveReceivers, getAllReceivers, connect
import sys
import threading
import time
import wx

class Controller(Loggable):
    
    worker_sleep_time = 0.1
    
    def __init__(self):
        self._client_worker = client.Worker(device=client.device.P175())
        self._thread = threading.Thread(target=self._worker)
        self._lock = threading.Lock()
        self._stop = threading.Event()
        
        self._channel = channel.Channel(
            rds_lock_time = 0,
            mes_lock_time = 0,
            stereo_lock_time = 0,
        )
        self._analyser = Analyser(client_worker = self._client_worker, channels=[self._channel])
        
        self._app = view.App(controller=self)
        
    def run(self):
        try:
            self._thread.start()
            self._client_worker.run()
            self._app.MainLoop()
        finally:
            self._stop.set()
            self._thread.join(1)
            if self._thread.is_alive():
                self.logger.warning("thread still running")
            self._client_worker.stop()
    
    @property
    def channel(self):
        return self._channel
    
    def _worker(self):
        self.logger.debug('go to work...')
        try:
            self.logger.debug('start working...')
            while not self._stop.is_set():
                with self._lock:
                    self._update_channel_variables()
                    self._analyser.enqueue_updates().wait(blocking=False)
                time.sleep(self.worker_sleep_time)
        except Exception:
            exc_info = sys.exc_info()
            self.logger.critical('thread exiting on exception', exc_info=exc_info)
        self.logger.debug('end of thread')
        
    def _update_channel_variables(self):
        for variable in self._channel.get_variables():
            # TODO: it may be resource expensive
            variable.enabled = bool(liveReceivers(getAllReceivers(sender=variable)))
            
    def add_channel_variable_listener(self, listener, value_key):
        with self._lock:
            # TODO: maybe implement our own widget notification system, lighter
            # than using pydispatcher 
            def callback(sender, event):
                wx.CallAfter(listener, sender, event)
            variable = self._channel.get_variable(value_key)
            connect(callback, value_changed, variable, False)
            self._update_channel_variables()

    def tune(self, frequency):
        frequency = parse_carrier_frequency(frequency)
        self._channel.set_frequency(frequency)
#        self._channel.tune(client)
        
    def get_channel_value(self, key):
        return getattr(self._channel, key)
        
    def dirty_tune_up(self):
        # TODO : quick done, no event management !!!
        self._client_worker.enqueue('tune_up')  
        
    def dirty_tune_down(self):
        self._client_worker.enqueue('tune_down')
    
    def tune_up(self):
        self._client_worker.enqueue(self._tune_up_down(up=True))
#        with self._lock:
#            self._tune_up_down(up=True)

    def tune_down(self):
        self._client_worker.enqueue(self._tune_up_down(up=False))
#        with self._lock:
#            self._tune_up_down(up=False)
        
    def _tune_up_down(self, client, up):
        step = 1000 # TODO: should be settable
        if not up:
            step = - step
        current = self._channel.frequency
        self._channel.frequency = current + step
        self._client_worker.enqueue('tune')
        
        
        
class Command(BaseCommand):
    
    def execute(self):
        controller = Controller()
        controller.run()

def main():
    sys.exit(Command().run())

if __name__ == '__main__':
    main()    