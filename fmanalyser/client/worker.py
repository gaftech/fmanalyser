# -*- coding: utf-8 -*-
from . import P175, tasks
from .. import settings
from ..exceptions import QueueFull
from ..utils.log import LoggableMixin
from ..utils.threads import Stoppable
import collections
import sys
import threading

class Worker(LoggableMixin, Stoppable):
    
    empty_queue_timeout = settings.WATCHER_SLEEP_TIME
    max_queue_size = 10
    
    def __init__(self):
        super(Worker, self).__init__()
        self.exc_info = None
        self._client = P175()
        self._stop = threading.Event()
        self._queue = collections.deque()
        self._lock = threading.RLock()
        self._thread = threading.Thread(target=self._worker)
        self._thread_started = False
        self._current_task = None
    
    def _worker(self):
        try:
            self.logger.debug('start working...')
            while not self._stop.is_set():
                if len(self._queue):
                    with self._lock:
                        task = self._queue.popleft()
                        self._current_task = task
                    task.perform(worker=self)
                    self._current_task = None
                else:
#                    self.logger.debug('empty queue, waiting %s s' % self.empty_queue_timeout)
                    self._stop.wait(self.empty_queue_timeout)
            self._client.close()
            self.logger.debug('end of thread')
        except Exception, e:
            with self._lock:
                self.exc_info = sys.exc_info()
                self.logger.critical('thread exits on exception', exc_info=True)
        
    def is_alive(self):
        return self._thread.is_alive()
    
    def acquire(self):
        self._lock.acquire()
    
    def release(self):
        self._lock.release()
    
    def run(self):
        with self._lock:
            self._thread_started = True
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
        if self._thread_started:
            self._thread.join(timeout)
        if self._thread.is_alive():
            raise RuntimeError('thread still alive')
        self.logger.debug('worker thread stopped')
    
    def enqueue(self, *args, **kwargs):
        """Enqueues a :class:`tasks.CallbackTask` instance 
        """
        
        task_class = tasks.CallbackTask
        
        if self.max_queue_size and len(self._queue) > self.max_queue_size:
            raise QueueFull('worker queue size : %s' % len(self._queue))
        if self._stop.is_set():
            raise RuntimeError('can not enqueue task while stopping')
#            self.logger.warning('can not enqueue task while stopping : %s' % task)
#            return task
        with self._lock:
            task = task_class(*args, **kwargs)
            self._queue.append(task)
            self.logger.debug('task enqueued : %s' % task)
        return task
    
    def enqueue_task(self, task):
        with self._lock:
            self._queue.append(task)
            self.logger.debug('task enqueued : %s' % task)
        return task        
    
    