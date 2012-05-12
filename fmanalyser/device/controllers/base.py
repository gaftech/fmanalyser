# -*- coding: utf-8 -*-
from fmanalyser.conf import EnableableSectionOptionHolder, options
from fmanalyser.utils.log import Loggable
from fmanalyser.device import Worker
from fmanalyser.conf.section import BaseConfigSection
from fmanalyser.utils.datastructures import OrderedDict

class DeviceControllerConfigSection(BaseConfigSection):
    
    def get_options(self):
        options = self._options.copy()
#        classname = self._source[self.name]['cls']
#        Plugin = get_class(classname)
#        options.update(Plugin._options)
        return options

class DeviceController(Loggable, EnableableSectionOptionHolder):
    
    config_section_name = 'device'
    device_class = None
    model = options.Option(default='p175')
    
    @classmethod
    def config_section_factory(cls, **attrs):
        if cls.device_class is not None:
            dev_opts = cls.device_class._options
            attrs.update(dev_opts)
        return super(DeviceController, cls).config_section_factory(
            config_class=DeviceControllerConfigSection,
            **attrs
        )
    
#    @classmethod
#    def get_options(cls):
#        options = super(DeviceController, cls).get_options()
#        if cls.device_class is not None:
#            options.extend(cls.device_class.get_options())
#        return options
    
    def __init__(self, name=None, channels=(), scans=(), **kwargs):
        
        dev_kwargs = dict(
            (k, kwargs.pop(k)) for k in self.device_class._options
            if k in kwargs
        )
        self._device = self.device_class(**dev_kwargs)
        self._worker = None
        self._last_enqueued = None
        
        self._channels = tuple(channels)
        self._scans = tuple(scans)
        
        super(DeviceController, self).__init__(name=name, **kwargs)
    
    @property
    def worker(self):
        return self._worker
    
    @property
    def device(self):
        return self._device
    
    @property
    def channels(self):
        return self._channels
    
    @property
    def bandscans(self):
        return self._scans
    
    def start_worker(self):
        if self._worker is not None:
            raise RuntimeError('Worker already started')
        try:
            self._worker = Worker(device=self.device)
            self._worker.run()
        except:
            self.stop_worker()
            raise

    def stop_worker(self):
        if self._worker is not None:
            self._worker.stop()
            self._worker = None
    
    def check_worker(self):
        if self._worker is not None and self._worker.exc_info is not None:
            self.logger.warning('Something happened to worker thread, restarting it...')
            self.stop_worker()
            self.start_worker()
    
    def should_enqueue(self):
        return self._last_enqueued is None or self._last_enqueued.done
    
    def enqueue_channel_update(self):
        for channel in self.channels():
            self._last_enqueued = self._enqueue_channel_update(channel)
    
    def _enqueue_channel_update(self, channel):
        raise NotImplementedError()
    
    def enqueue_bandscan_update(self):
        raise NotImplementedError
    
    def close(self):
        self.stop_worker()
        self.device.close()
    

    