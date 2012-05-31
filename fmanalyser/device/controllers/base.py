# -*- coding: utf-8 -*-
from fmanalyser.conf import options, EnableableOptionHolder
from fmanalyser.device import Worker
from fmanalyser.utils.log import Loggable
from fmanalyser.models.bandscan import FFTBandscan, MultiScan

class DeviceController(Loggable, EnableableOptionHolder):
    
    section_name = 'device'
    device_class = None
    model = options.Option(default='p175')
    scan_lock_time = options.FloatOption(default=1)
    
    @classmethod
    def from_config_dict(cls, confdict, name=None, defaults=None, extras=None):
        if cls is DeviceController:
            from fmanalyser.device.controllers import get_controller_class
            opts = confdict.copy()
            model = cls._options['model'].pop_val_from_dict(opts) 
            subcls = get_controller_class(model)
            return subcls.from_config_dict(opts, name, defaults, extras)
        return super(DeviceController, cls).from_config_dict(confdict, name, defaults, extras) 
    
    @classmethod
    def get_config_options(cls):
        opts = super(DeviceController, cls).get_config_options()
        if not cls is DeviceController:
            opts.update(cls.device_class.get_config_options())
        return opts
        
    
    def __init__(self, name=None, channels=(), scans=(), **kwargs):
        
        if self.device_class is None:
            raise ValueError("%s subclasses must define a `device_class` attribute")
        
        # Device and worker init
        #TODO: device should be owned by worker only.
        # Maybe we can pass the device constructor to the worker.
        # Or maybe, we should keep the device and provides to the worker method to build a new one if necessary
        # The underlying idea is that we may want to make devices that needs to restart from a fresh instance 
        # in case of problem.
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
    def scans(self):
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
    
    def enqueue_update(self):
        self.enqueue_channel_update()
        self.enqueue_bandscan_update()
    
    def enqueue_channel_update(self):
        for channel in self.channels:
            self._last_enqueued = self.enqueue_channel_update(channel)
    
    def _enqueue_channel_update(self, channel):
        raise NotImplementedError()
    
    def enqueue_bandscan_update(self):
        for scan in self.scans:
            self.worker.acquire()
            try:
                self._last_enqueued = self._enqueue_bandscan_update(scan)
            finally:
                self.worker.release()
    
    def _enqueue_bandscan_update(self, scan):
        if isinstance(scan, MultiScan):
            scans = scan.scans
        else:
            scans = [scan]
        for scan in scans:
            self.worker.enqueue_worker_task(self._update_scan_loop, scan)
        
    def _update_scan_loop(self, task, worker, scan):
        self._scan_init(worker, scan)
        count = 0
        while True:
            # Check stop conditions
            if worker.stopped:
                break
            if scan.partial and count > scan.partial:
                break
            next_freq = scan.get_next_frequency()
            if not next_freq:
                break
            if isinstance(scan, FFTBandscan):
                self._update_fft_scan(worker, next_freq, scan)
            else:
                self._update_scan(worker, next_freq, scan)
            count += 1
    
    def _scan_init(self, worker, scan):
        """Hook to configure device before scan levels acquiring"""
    
    def _update_scan(self, worker, next_freq, scan):
        worker.device.tune(next_freq)
        worker.sleep(self.scan_lock_time)
        l = self._probe_scan_level(worker)
        scan.update([(next_freq, l)])
    
    def _probe_scan_level(self, worker):
        raise NotImplementedError()
    
    def _update_fft_scan(self, worker, next_freq, scan):
        worker.device.tune(next_freq)
        worker.sleep(self.scan_lock_time)
        rel_freqs, levels = self._probe_fft(worker,
            span = scan.span
        )
        scan.update(next_freq, rel_freqs, levels)        
    
    def _probe_fft(self, worker, span):
        raise NotImplementedError()
    
    def close(self):
        self.stop_worker()
        self.device.close()
    
class GrDeviceController(DeviceController):
    
    def _probe_scan_level(self, worker):
        return worker.device.get_signal_level()
    
    
    
    
    