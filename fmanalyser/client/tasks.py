# -*- coding: utf-8 -*-
from ..utils.log import LoggableMixin
from ..utils.threads import Stoppable
from fmanalyser.exceptions import Timeout

class BaseTask(LoggableMixin, Stoppable):
    
    def __init__(self):
        super(BaseTask, self).__init__()
        self._done = False
    
    def perform(self, worker):
        try:
            self.logger.debug('performing %s...' % self)
            self.run(worker)
            self._done = True
            self.logger.debug('%s done' % self)
        finally:
            self._stop.set()
    
    def run(self, worker):
        pass

class CallbackTask(BaseTask):
    """Calls a function or a client's method when ran by the worker.
    """
    
    def __init__(self, callback, *args, **kwargs):
        """
        :param callback:
            Either a client's method name or a callable that takes the client
            instance as first argument
        """
        
        super(CallbackTask, self).__init__()
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
    
    def __str__(self):
        name = '???'
        if isinstance(self.callback, basestring):
            name = self.callback
        elif hasattr(self.callback, 'im_self'):
            name = '%s.%s' % (self.callback.im_self,
                              self.callback.__name__)
        
        return 'callback : %s' % name
    
    def run(self, worker):
        client = worker._client
        if isinstance(self.callback, basestring):
            method = getattr(client, self.callback)
            return method(*self.args, **self.kwargs)
        else:
            return self.callback(client, *self.args, **self.kwargs)

class Sleep(BaseTask):
    
    def __init__(self, timeout):
        super(Sleep, self).__init__()
        self.timeout = timeout
    
    def __str__(self):
        return '%s s sleep' % self.timeout
    
    def run(self, worker):
#        self._stop.wait(timeout=self.timeout)
        try:
            self.wait(timeout=self.timeout, blocking=False)
        except Timeout:
            pass


