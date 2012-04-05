# -*- coding: utf-8 -*-
from . import view
from ..client.tasks import ReadChannelValues
from ..utils.log import LoggableMixin
from ..values import channel
from pydispatch.dispatcher import liveReceivers, getAllReceivers
import sys
import threading
import time
import wx
from fmanalyser.client.tasks import WriteChannelValue, TuneUpCommand,\
    TuneDownCommand

class Controller(LoggableMixin):
    
    worker_sleep_time = 1
    
    def __init__(self, client_worker):
        self._client_worker = client_worker
        self._thread = threading.Thread(target=self._worker)
        self._lock = threading.Lock()
        self._stop = threading.Event()
        
    def run(self):
        self._channel = channel.Channel()
        self._client_worker.run()
        self._thread.start()
        self._app = view.App(controller=self)
        self._app.MainLoop()
    
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
                    self._client_worker.enqueue(ReadChannelValues, channel=self._channel)
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
            # TODO: maybe implement our own widget notification system, lighter than using pydispatcher 
            def callback(sender, event):
                wx.CallAfter(listener, sender, event)
            sender = self._channel.get_variable(value_key)
            sender.connect_change_listener(callback, weak=False)
            self._update_channel_variables()

    def set_channel_command(self, key, value):
        variable = self._channel.get_variable(key)
        variable.set_command(value)
        self._client_worker.enqueue(WriteChannelValue, variable=variable)
        
    def get_channel_value(self, key):
        return getattr(self._channel, key)
        
    def dirty_tune_up(self):
        # TODO : quick done, no event management !!!
        self._client_worker.enqueue(TuneUpCommand)  
        
    def dirty_tune_down(self):
        self._client_worker.enqueue(TuneDownCommand)
    
    def tune_up(self):
        with self._lock:
            self._tune_up_down(up=True)

    def tune_down(self):
        with self._lock:
            self._tune_up_down(up=False)
        
    def _tune_up_down(self, up):
        variable = self.channel.get_variable('frequency')
        current = variable.value
        step = 1000 # TODO: should be settable
        if not up:
            step = - step
        variable.set_command(current + step, clean_value=False)
        self._client_worker.enqueue(WriteChannelValue, variable=variable)
        
        
        
    