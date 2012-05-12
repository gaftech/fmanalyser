# -*- coding: utf-8 -*-
from ..exceptions import Timeout
import threading
import time
from functools import wraps

class Stoppable(object):
    
    def __init__(self, *args, **kwargs):
        self._stop = threading.Event()
        
        from fmanalyser.conf.fmconfig import fmconfig
        self.short_sleep_time = fmconfig['global']['watcher_sleep_time']
    
    @property
    def stopped(self):
        return self._stop.is_set()
    
    def stop(self, *args, **kwargs):
        self._stop.set()

    def sleep(self, timeout=None, blocking=True):
        try:
            self.wait(timeout, blocking)
        except Timeout:
            pass

    def short_sleep(self):
        self._stop.wait(self.short_sleep_time)

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
            self.short_sleep()
#            time.sleep(settings.WATCHER_SLEEP_TIME)

    def _wait_blocking(self, timeout):
        self._stop.wait(timeout)
        if not self._stop.is_set():
            raise Timeout(self)

class Lockable(object):
    
    def __init__(self, *args, **kwargs):
        self._lock = threading.Lock()
    
    def acquire(self):
        self._lock.acquire()
        
    def release(self):
        self._lock.release()

def locking():
    """Method synchronization decorator.
    
    Intended to be used when class provides `acquire` and `release` methods.
    """
    def locked(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            self.acquire()
            try:
                return func(self, *args, **kwargs)
            finally:
                self.release()
        return inner
    return locked




