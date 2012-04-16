# -*- coding: utf-8 -*-
from ..exceptions import Timeout
from .. import settings
import threading
import time

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
