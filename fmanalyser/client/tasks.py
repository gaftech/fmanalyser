# -*- coding: utf-8 -*-
from ..utils.log import LoggableMixin
from ..utils.threads import Stoppable

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
    
    def __init__(self, worker, callback, *args, **kwargs):
        """
        :param callback:
            Either a client's method name or a callable that takes the client
            instance as first argument
        """
        
        super(CallbackTask, self).__init__(worker=worker)
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
    
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
        
    def run(self, worker):
        self.wait(timeout=self.timeout, blocking=False)


#class ReadChannelValues(BaseTask):
#    
#    def __init__(self, worker, channel):
#        super(ReadChannelValues, self).__init__(worker)
#        self.channel = channel
#    
#    def __str__(self):
#        return 'Measurements : %s' % self.channel
#    
#    def run(self):
#        self.channel.update(self.client)
#
#class Tune(BaseTask):
#    
#    def __init__(self, worker, channel):
#        super(Tune, self).__init__(worker)
#        self.channel = channel
#    
#    def run(self):
#        self.channel.tune(self.client)
#
#class TuneUpCommand(BaseTask):
#    # TODO : Integrate this in channel variable (or alike stuff) to manage events
#    def run(self):
#        self.client.tune_up()
#    
#class TuneDownCommand(BaseTask):
#    
#    def run(self):
#        self.client.tune_down()
#    
#    
#    
#    
#    
#    
#    
