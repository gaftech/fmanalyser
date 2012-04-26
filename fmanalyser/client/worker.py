# -*- coding: utf-8 -*-
from . import tasks
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
    
    def __init__(self, device):
        super(Worker, self).__init__()
        self._client = device
        self.exc_info = None
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
                    self._stop.wait(self.empty_queue_timeout)
        except Exception:
            self.exc_info = sys.exc_info()
            self.logger.critical('thread exits on exception', exc_info=True)
        finally:
            if self._current_task is not None and not self._current_task.stopped:
                self.logger.warning('stopping unperformed task  : %s' % self._current_task)
                self._current_task.stop()
            self._client.close()
            self.logger.debug('end of thread')        
        
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
            
    def stop(self, timeout=5):
        self.logger.debug('stopping worker...')
        super(Worker, self).stop()
        if self._current_task is not None and not self._current_task.stopped:
            self.logger.warning('stopping unperformed task  : %s' % self._current_task)
            self._current_task.stop()
        for task in self._queue:
            if not task.stopped:
                self.logger.debug('stopping queued task : %s' % task)
                task.stop()
        if self._thread_started:
            self._thread.join(timeout)
        if self._thread.is_alive():
            raise RuntimeError('thread still alive')
        self.logger.debug('worker stopped')
    
    def enqueue(self, *args, **kwargs):
        """Build and enqueues a :class:`tasks.CallbackTask` instance.
        
        Args and kwargs are passed to the class constructor.
        """
        
        task_class = tasks.CallbackTask
        
        if self.max_queue_size and len(self._queue) > self.max_queue_size:
            raise QueueFull('worker queue size : %s' % len(self._queue))
        task = task_class(*args, **kwargs)
        if self._stop.is_set():
#            raise RuntimeError('can not enqueue task while stopping')
            self.logger.warning('can not enqueue task while stopping : %s' % task)
            return task
        return self.enqueue_task(task)
#        with self._lock:
#            
#            self._queue.append(task)
#            self.logger.debug('task enqueued (%s) : %s' % (len(self._queue), task))
#        return task
    
    def enqueue_task(self, task):
        with self._lock:
            self._queue.append(task)
            self.logger.debug('task enqueued (%s) : %s' % (len(self._queue), task))
        return task        
    
    