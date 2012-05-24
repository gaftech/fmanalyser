# -*- coding: utf-8 -*-
from fmanalyser.conf import EnableableOptionHolder, options
from fmanalyser.exceptions import OutOfBoundFrequency, BadOptionValue
from fmanalyser.models.signals import scan_updated, fft_scan_updated,\
    scan_completed
from fmanalyser.utils.log import Loggable
from fmanalyser.utils.render import render_frequency
from itertools import izip
import datetime
import fmanalyser
import threading

MODEL_BASIC = 'basic'
MODEL_FFT = 'fft'
MODEL_MULTISCAN = 'multiscan'

class BaseBandscan(Loggable, EnableableOptionHolder):
    
    section_name = 'scan'
    
    device = options.Option(
        ini_help="Name of the device to use (as in [device:<name>] section)")
    model = options.Option(choices=(MODEL_BASIC, MODEL_FFT, MODEL_MULTISCAN), default=MODEL_BASIC)
    step = options.IntOption(default=100)
    partial = options.IntOption(default=10)
    exclude = options.JsonOption(default=(),
        ini_help="JSON formatted list of frequency intervals in which to skip alarm triggering")
    ref_file = options.DataFileOption(default='scan.ref')

    @classmethod
    def from_config(cls, config, subname=None, **kwargs):
        if cls is BaseBandscan:
            subcls = cls.get_subclass(cls.get_config_dict(config, subname))
            return subcls.from_config(config, subname, **kwargs)
        return super(BaseBandscan, cls).from_config(config, subname, **kwargs)

    @classmethod
    def from_config_dict(cls, confdict, subname=None, **kwargs):
        if cls is BaseBandscan:
            subcls = cls.get_subclass(confdict)
            return subcls.from_config_dict(confdict, subname, **kwargs)
        return super(BaseBandscan, cls).from_config_dict(confdict, subname, **kwargs)

    @classmethod
    def get_subclass(cls, confdict):
        model = confdict.get('model')
        try:
            return {
                MODEL_BASIC: Bandscan,
                MODEL_FFT: FFTBandscan,
                MODEL_MULTISCAN: MultiScan,
            }[model]
        except KeyError:
            raise BadOptionValue("invalid bandscan model: %s" % model)
    
    def __init__(self, **kwargs):
        super(BaseBandscan, self).__init__(**kwargs)
        self._lock = threading.Lock()
        self.init()
        self.reset()    

    def __str__(self):
        return '%s[%s..%s]' % (self.__class__.__name__,
                               render_frequency(self.start),
                               render_frequency(self.stop))
    
    def __iter__(self):
        for f, l in self.iter_interlaced():
            yield f, l

    def init(self):
        pass

    def reset(self):
        pass

    def get_next_frequency(self):
        raise NotImplementedError()

    def is_complete(self):
        raise NotImplementedError()
    
    def round_freq(self, freq):
        return int(round(freq/self.step)*self.step)
    
    def _round_freq_interlace(self, lst):
        return max(lst)

    def _update(self, freq, data):
        try:
            self._pending.remove(freq)
        except ValueError:
            pass
        self._data[freq].append(data)

    def save_ref(self):
        assert self.is_complete()
        with open(self.ref_file, 'w') as fp:
            self.dump(fp)
        self.logger.info('scanning reference file saved: %s' % self.ref_file)

    def dump(self, fileobj):
        infos = {
            'version': fmanalyser.__version__,
            'now': datetime.datetime.now(),
        }
        template = """
# RF band scan generated by fmanalyser %(version)s.
# Date: %(now)s
"""
        output = template % infos
        fileobj.write(output)
        for f,l in self:
            fileobj.write('%s %s\n' % (f,l))

class BaseMultipassBandscan(BaseBandscan):

    def reset(self):
        self._pending = self._freqs[:]
        self._data = dict((f, []) for f in self._freqs)

    def get_next_frequency(self):
        """Returns the next frequency without value associated or `Ǹone` if scan is complete."""
        try:
            return self._pending[0]
        except IndexError:
            return None
    
    def is_complete(self):
        return not len(self._pending)

    def _multipass_interlace(self, lst):
        return max(lst)

class Bandscan(BaseMultipassBandscan):

    start = options.CarrierFrequencyOption(default=87500)
    stop = options.CarrierFrequencyOption(default=108000)

    def init(self):
        if self.start >= self.stop:
            raise ValueError(
                "start frequency (%s) must be lower than stop frequency (%s)" % (
                self.start, self.stop))
        self._freqs = range(self.start, self.stop+self.step, self.step)

    def iter_interlaced(self):
        for f in self._freqs:
            levels = self._data[f]
            if levels:
                yield f, self._multipass_interlace(levels) 

    def get(self, freq, round_freq=False):
        levels = self._get_levels(freq, round_freq)
        if levels:
            return self._multipass_interlace(levels)
        return None
    
    def get_levels(self, freq, round_freq=False):
        return self._get_levels(freq, round_freq)[:]
    
    def _get_levels(self, freq, round_freq=False):
        if round_freq:
            freq = self.round_freq(freq)
        try:
            return self._data[freq]
        except KeyError:
            raise OutOfBoundFrequency(freq)
        
    def update(self, freq_levels, round_freqs=False, interlace=True):
        if round_freqs:
            freq_levels = [(self.round_freq(f),l) for f,l in freq_levels]
        if interlace:
            d = {}
            for f,l in freq_levels:
                d.setdefault(f,[]).append(l)
            freq_levels = [(f,self._round_freq_interlace(lst)) for f,lst in d.iteritems()]
        with self._lock:
            updated_freqs = set()
            for freq, level in freq_levels:
                self._update(freq, level)
                updated_freqs.add(freq)
                self.logger.debug("%s updated : %s => %s" % (self, freq, level))
            freq_levels = [(f, self.get(f, round_freq=False)) for f in sorted(updated_freqs)]
        scan_updated.send(self, freq_levels)
        if self.is_complete():
            scan_completed.send(self)

class FFTBandscan(BaseMultipassBandscan):
    
    start_cf = options.CarrierFrequencyOption(required=True)
    stop_cf = options.CarrierFrequencyOption()
    jump = options.IntOption(required=True)
    span = options.IntOption(required=True)
    dc_skip = options.IntOption(default=0,
        ini_help="width (kHz) of fft values to drop around each center frequency")
    side_skip = options.IntOption(default=0)
    
    def init(self):
        if not self.stop_cf:
            self.stop_cf = self.start_cf
        
        # Value checks
#        if self.stop_cf < self.start_cf:
#            raise ValueError(
#                "stop frequency (%s) must be greater than or equal to stop frequency (%s)" % (
#                self.stop_cf, self.start_cf))
        #TODO: jump/span/reject value checks
    
        # Computed fixed attributes
        self.start = self.start_cf - self.span/2 + self.side_skip
        self.stop = self.stop_cf + self.span/2 - self.side_skip
    
        # Data init
        self._freqs = range(self.start_cf, self.stop_cf+self.jump, self.jump)
        
    def update(self, center_freq, rel_freqs, levels):
#        if not isinstance(rel_freqs, numpy.array):
#            rel_freqs = numpy.array(rel_freqs)
#        if not isinstance(levels, numpy.array):
#            levels = numpy.array(levels)
        self._update(center_freq, (rel_freqs, levels))
        fft_scan_updated.send(self, center_freq, rel_freqs, levels)
        if self.is_complete():
            scan_completed.send(self)

    def get_raw_ffts(self):
        raw_ffts = []
        for cf, ffts in sorted(self._data.items()):
            for rel_freqs, levels in ffts:
                raw_ffts.append((rel_freqs + cf, levels))
        return raw_ffts
    
    def iter_interlaced(self):
        bigdata = {}
        for cf, ffts in self._data.iteritems():
            if not ffts:
                continue
            fft = self._get_multipass_fft(ffts)
            for rel_freq, level in izip(*fft):
                bigdata.setdefault(cf+rel_freq, []).append(level)

        for f, levels in sorted(bigdata.items()):
            yield f, self._overlap_interlace(levels)
    
    def _get_multipass_fft(self, ffts):
        rounded_ffts = [self._clean_fft(freqs, levels) for freqs, levels in ffts]
        rounded_freqs = rounded_ffts[0][0]
        levels = [fft[1] for fft in rounded_ffts]
        interlaced_levels = [self._multipass_interlace(lst) for lst in izip(*levels)]
        return rounded_freqs, interlaced_levels
    
    def _clean_fft(self, freqs, levels):
        rounded = {}
        for f,l in izip(freqs, levels):
            if abs(f) < self.dc_skip/2 or abs(f) >= (self.span/2-self.side_skip):
                continue
            rounded.setdefault(self.round_freq(f), []).append(l)
        _freqs, _levels = [], []
        for f,lst in sorted(rounded.items()):
            _freqs.append(f)
            _levels.append(self._round_freq_interlace(lst))
        return _freqs, _levels
    
    def _overlap_interlace(self, lst):
        return max(lst)        
        
class MultiScan(BaseBandscan):
    
    ini_help = """\
Multiscan is a bandscan that aggregates other scans ('sub-scans').
This section can define options that will be set as default for all sub-scans.
"""
    
    scans = options.CsvOption(required=True,
        ini_help="scan names assembled in this scan")
    
    @classmethod
    def from_config(cls, config, subname=None, extras=None, **kwargs):
        confdict = config.get_section(cls.section_name, subname)
        subscan_defaults = dict((k,confdict.pop(k)) for k in confdict.keys()
                                if k not in cls._options)
        subscan_names = cls._options['scans'].clean(confdict['scans'])
        subscans = []
        for subscan_name in subscan_names:
            sub_confdict = subscan_defaults.copy() 
            sub_confdict.update(config.get_section(cls.section_name, subscan_name))
            subscan = BaseBandscan.from_config_dict(sub_confdict, subscan_name)
            subscans.append(subscan)
        extras = extras or {}
        extras.setdefault('scans', subscans)
        return cls.from_config_dict(confdict, subname, extras=extras, **kwargs)
        
    def is_complete(self):
        return all(s.is_complete() for s in self.scans)
    
    def iter_interlaced(self):
        bigdata = {}
        for scan in self.scans:
            for f,l in scan:
                bigdata.setdefault(f, []).append(l)
        for f, levels in sorted(bigdata.items()):
            yield f, self._overlap_interlace(levels)
    
    def _overlap_interlace(self, lst):
        return max(lst)   
    