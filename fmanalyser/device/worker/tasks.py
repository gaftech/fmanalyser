# -*- coding: utf-8 -*-
from fmanalyser.exceptions import Timeout
from fmanalyser.utils.log import Loggable
from fmanalyser.utils.threads import Stoppable

class BaseTask(Loggable, Stoppable):
    
    def __init__(self):
        super(BaseTask, self).__init__()
        self._done = False
        self._retval = None
    
    @property
    def done(self):
        return self._done
    
    def perform(self, worker):
        try:
            self.logger.debug('performing %s...' % self)
            self._retval = self.run(worker)
            self._done = True
            self.logger.debug('%s done' % self)
        finally:
            self._stop.set()
        return self._retval
    
    def wait(self, *args, **kwargs):
        super(BaseTask, self).wait(*args, **kwargs)
        return self._retval
    
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
        if hasattr(self.callback, 'im_self'):
            name = '%s.%s' % (self.callback.im_self,
                              self.callback.__name__)
        return 'callback : %s' % name
    
    def run(self, worker):
        return self.callback(self, worker, *self.args, **self.kwargs)

class DeviceTask(CallbackTask):

    def __str__(self):
        if isinstance(self.callback, basestring):
            return 'device.%s' % self.callback        
        return super(DeviceTask, self).__str__()

    def run(self, worker):
        if isinstance(self.callback, basestring):
            method = getattr(worker._device, self.callback)
            return method(*self.args, **self.kwargs)
        else:
            return self.callback(worker._device, *self.args, **self.kwargs)

class Sleep(BaseTask):
    
    def __init__(self, timeout):
        super(Sleep, self).__init__()
        self.timeout = timeout
    
    def __str__(self):
        return '%s s sleep' % self.timeout
    
    def run(self, worker):
        try:
            self.wait(timeout=self.timeout, blocking=False)
        except Timeout:
            pass


