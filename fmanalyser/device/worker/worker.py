# -*- coding: utf-8 -*-
from . import tasks
from fmanalyser.conf import settings
from fmanalyser.exceptions import DeviceError, QueueFull
from fmanalyser.utils.log import Loggable
from fmanalyser.utils.threads import Stoppable
import collections
import sys
import threading

class Worker(Loggable, Stoppable):
    
    max_queue_size = 100
    device_error_sleep = 1
    
    def __init__(self, device):
        
        super(Worker, self).__init__()
        
        # Options
        self.empty_queue_timeout = settings.empty_queue_timeout
        
        self._device = device
        self.exc_info = None
        self._queue = collections.deque()
        self._lock = threading.RLock()
        self._thread = threading.Thread(target=self._worker)
        self._thread_started = False
        self._current_task = None
        
        
    
    def _worker(self):
        try:
            self.logger.info('acquiring data from device %s' % self._device)
            while not self._stop.is_set():
                if self._current_task is None and len(self._queue):
                    self._current_task = self._queue.popleft()
                if self._current_task is None:
                    self._stop.wait(self.empty_queue_timeout)
                else:
                    try:
                        self._current_task.perform(self)
                        self._current_task = None
                    except DeviceError, e:
                        self.logger.info('device error while performing task %s' % self._current_task)
                        self.logger.warning('device error: %s: %s' % (e.__class__.__name__, e))
                        self._device.close()
                        self.logger.info('retrying device probe in %s s' % self.device_error_sleep)
                        self._stop.wait(self.device_error_sleep)
        except Exception:
            self.exc_info = sys.exc_info()
            self.logger.critical('thread exits on exception', exc_info=True)
        finally:
            if self._current_task is not None and not self._current_task.stopped:
                self.logger.warning('stopping unperformed task  : %s' % self._current_task)
                self._current_task.stop()
            self._device.close()
            self.logger.info('device released : %s' % self._device)
    
    @property
    def device(self):
        return self._device
    
    @property
    def empty_queue(self):
        return not len(self._queue)
    
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
            self.logger.debug('stopping current task  : %s' % self._current_task)
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
        """Build and enqueues a :class:`tasks.DeviceTask` instance.
        
        Args and kwargs are passed to the class constructor.
        """
        return self.enqueue_task(tasks.DeviceTask(*args, **kwargs))
    
    def enqueue_worker_task(self, *args, **kwargs):
        return self.enqueue_task(tasks.CallbackTask(*args, **kwargs))
    
    def enqueue_task(self, task):
        if self._stop.is_set():
            self.logger.warning('can not enqueue task while stopping : %s' % task)
            return task
        if self.max_queue_size and len(self._queue) > self.max_queue_size:
            raise QueueFull('worker queue size : %s' % len(self._queue))    
        with self._lock:
            self._queue.append(task)
            self.logger.debug('task enqueued (%s) : %s' % (len(self._queue), task))
        return task    
    
    