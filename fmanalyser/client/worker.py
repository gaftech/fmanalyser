# -*- coding: utf-8 -*-
from . import P175
from .. import settings
from ..exceptions import QueueFull, Timeout
import collections
import logging
import threading
import time
import sys
from fmanalyser.utils.log import LoggableMixin

class Stoppable(object):
    
    def __init__(self, *args, **kwargs):
        super(Stoppable, self).__init__(*args, **kwargs)
        self._stop = threading.Event()
        self._lock = threading.Lock()
    
    
    @property
    def stopped(self):
        return self._stop.is_set()
    
    def stop(self, *args, **kwargs):
        with self._lock:
            if self._stop.is_set():
#                self.logger.warning('already stopping !')
                raise RuntimeError('already stopping')
            self._stop.set()
            self._on_stop(*args, **kwargs)

    def _on_stop(self, *args, **kwargs):
        pass

    def wait(self, timeout=None, blocking=True):
        if blocking:
            self._wait_blocking(timeout)
        else:
            self._wait_non_blocking(timeout)

    def _wait_non_blocking(self, timeout):
        if timeout is not None:
            time_limit = time.time() + timeout
        while not self._stop.is_set():
            if timeout is not None and time.time() > time_limit:
                raise Timeout(self)
            time.sleep(settings.WATCHER_SLEEP_TIME)

    def _wait_blocking(self, timeout):
        self._stop.wait(timeout)
        if not self._stop.is_set():
            raise Timeout(self)

class BaseTask(LoggableMixin, Stoppable):
    
    def __init__(self, worker):
        super(BaseTask, self).__init__()
        self._worker = worker
        self._done = False
    
    @property
    def client(self):
        return self._worker._client
    
    def perform(self):
        try:
            self.logger.debug('performing %s...' % self)
            self.run()
            self._done = True
            self.logger.debug('%s done' % self)
        finally:
            self._stop.set()
    
    def run(self):
        pass

class CallbackTask(BaseTask):
    
    def __init__(self, worker, callback):
        super(CallbackTask, self).__init__(worker=worker)
        self.callback = callback
    
    def run(self):
        return self.callback()

class Worker(LoggableMixin, Stoppable):
    
    empty_queue_timeout = settings.WATCHER_SLEEP_TIME
    max_queue_size = 10
    
    def __init__(self):
        super(Worker, self).__init__()
        self.exc_info = None
        self._client = P175()
        self._stop = threading.Event()
        self._queue = collections.deque()
        self._thread = threading.Thread(target=self._worker)
        self._lock = threading.Lock()
        self._current_task = None
    
    def _worker(self):
        try:
            self.logger.debug('start working...')
            while not self._stop.is_set():
                if len(self._queue):
                    with self._lock:
                        task = self._queue.popleft()
                        self._current_task = task
                    task.perform()
                    self._current_task = None
                else:
#                    self.logger.debug('empty queue, waiting %s s' % self.empty_queue_timeout)
                    self._stop.wait(self.empty_queue_timeout)
            self._client.close()
            self.logger.debug('end of thread')
        except Exception, e:
            with self._lock:
                self.exc_info = sys.exc_info()
                self.logger.warning('thread exits on exception', exc_info=True)
        
    def is_alive(self):
        return self._thread.is_alive()
    
    def run(self):
        self._thread.start()
            
    def _on_stop(self, timeout=5):
        self.logger.debug('worker exiting...')
        if self._current_task is not None and not self._current_task.stopped:
            self.logger.debug('stopping task  : %s' % self._current_task)
            self._current_task.stop()
        for task in self._queue:
            if not task.stopped:
                self.logger.debug('stopping queued task : %s' % task)
                task.stop()
        self._thread.join(timeout)
        if self._thread.is_alive():
            raise RuntimeError('thread still alive')
        self.logger.debug('worker thread stopped')
    
    def enqueue(self, task_class=CallbackTask, *args, **kwargs):
        if self.max_queue_size and len(self._queue) > self.max_queue_size:
            raise QueueFull('worker queue size : %s' % len(self._queue))
        if self._stop.is_set():
            raise RuntimeError('can not enqueue task while stopping')
#            self.logger.warning('can not enqueue task while stopping : %s' % task)
#            return task
        with self._lock:
            task = task_class(worker=self, *args, **kwargs)
            self.logger.debug('enqueuing task : %s' % task)
            self._queue.append(task)
            self.logger.debug('task enqueued : %s' % task)
        return task
    
    
    
    