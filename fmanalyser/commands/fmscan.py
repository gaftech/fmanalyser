# -*- coding: utf-8 -*-

from fmanalyser.conf import fmconfig
from fmanalyser.device.controllers.base import DeviceController
from fmanalyser.exceptions import CommandError
from fmanalyser.models.bandscan import BaseBandscan
from fmanalyser.models.signals import scan_updated, fft_scan_updated
from fmanalyser.utils.command import BaseCommand
from itertools import izip
from optparse import make_option
import os
import subprocess
import sys
import tempfile
import shutil

class Command(BaseCommand):

    base_options = BaseCommand.base_options + (
#        make_option('-d', '--hd', action="store_true", default=False,
#            help="use HD handscan model"),
        make_option('-s', '--scan-name',
            help="scan config file subsection name (default [scan] section if not set"),
        make_option('-g', '--gnuplot', action='store_true', default=False,
            help="lauch gnuplot visualization"),
        make_option('-m', '--matplotlib', action='store_true', default=False,
            help="lauch matplotlib visualization"),
        make_option('-f', '--ref-file', 
            help="reference scanning file location"),
        make_option('-n', '--no-ref', dest='load_ref', action='store_false', default=True,
            help="don't try to load reference scanning"),
        make_option('-r', '--store-ref', action='store_true',
            help="save data to the scanning reference file"),
        make_option('-o', '--output-file',
            help="save current scan to file"),
        make_option('-d', '--debug', action='store_true', default=False,
            help="display debug things like sub-scans...")
    )
    
    def alter_conf(self, config):
        if self.options.ref_file:
            config['scan']['ref_file'] = os.path.abspath(self.options.ref_file)
        
    
    def execute(self):
        
        # Bandscan and device controller init
        scan_conf = fmconfig.get_section('scan', self.options.scan_name, copy=False)
        if self.options.ref_file:
            scan_conf['ref_file'] = os.path.abspath(self.options.ref_file)
        scan_conf['partial'] = 0
        
        self.scan = BaseBandscan.from_config(fmconfig, self.options.scan_name)
        self.controller = DeviceController.from_config(
            fmconfig,
            subname = scan_conf.get('device'), 
            extras = {
                'scans': [self.scan],
            }
        )
        
        # Visualization init
        self.persist = False
        if self.options.gnuplot:
            self.persist = True
            self.init_gnuplot()
        if self.options.matplotlib:
            self.persist = True
            self.init_matplotlib()
        
        # data acquisition
        self.controller.start_worker()
        self.controller.enqueue_bandscan_update()
        
        while not self.scan.is_complete():
            if self._stop.is_set():
                raise CommandError('scan stopped by user')
            self.short_sleep()
        
        self.controller.close()
        
        if self.options.store_ref:
            self.scan.save_ref()
        
        if self.options.output_file:
            with open(self.options.output_file, 'w') as fp:
                self.scan.dump(fp)
            self.logger.info('file saved: %s' % self.options.output_file)
        
        if self.persist:
            while not self._stop.is_set():
                self.short_sleep()
     
    def close(self):
        if hasattr(self, 'controller'):
            self.controller.close()
    
    def init_gnuplot(self):
        try:
            self._gp = subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE)
        except OSError:
            raise CommandError("can't open gnuplot, please check if it's installed")        
        self._gpw('set xrange [%f:%f]' % (self.scan.start,
                                          self.scan.stop))
        self._gpw('lower')
        
        self._gp_files = set()
        self._gp_count = 0
        self._gp_tmp_dir = tempfile.mkdtemp(suffix='fmscan')
        
        if self.options.load_ref and os.path.exists(self.scan.ref_file):
            #TODO: Bandscan must implement a way to provide its reference and to load a file
#            fpath = os.path.join(self._gp_tmp_dir, 'ref.scan')
#            shutil.copy2(self.scan.ref_file, fpath)
            self._gp_add_file(self.scan.ref_file)
        
        scan_updated.connect(self._gp_update,)
#        scan_completed.connect(self._gp_completed, self.scan)
        fft_scan_updated.connect(self._gp_update,)
        if self.options.debug:
            fft_scan_updated.connect(self._gp_debug_fft)
    
    def _gp_add_file(self, fpath, cmd_extras='with lines'):
        if fpath not in self._gp_files:
            plot = 'replot' if self._gp_count else 'plot'
            self._gp_count += 1
            self._gp_files.add(fpath)
            self._gpw("%s '%s' %s" % (plot, fpath, cmd_extras))
        else:
            self._gpw('replot')
    
    def _gpw(self, command):
        command = '%s\n' % command
        self._gp.stdin.write(command)
    
    def _gp_update(self, signal, sender, event):
        # Global scan
        if self.options.debug or self.scan.is_complete():
            fpath = os.path.join(self._gp_tmp_dir, 'global.scan')
            with open(fpath, 'w') as fp:
                self.scan.dump(fp)
            self._gp_add_file(fpath)
        
    def _gp_debug_fft(self,  signal, sender, event):
        fname = '%s_MHz' % (event.center_freq/1e3)
        fpath = os.path.join(self._gp_tmp_dir, fname)
        with open(fpath, 'w') as fp:
            for f, l in izip(event.rel_freqs, event.levels):
                fp.write('%s %s\n' % (f+event.center_freq, l))
        self._gp_add_file(fpath)
    
        
    def init_matplotlib(self):
        #TODO: find a way to run matplotlib in other process/thread
        
        import matplotlib
        matplotlib.use('GTkAgg')
        import matplotlib.pyplot as plt

        fig = plt.figure()
        subplot = fig.add_subplot(111)
        
        plt.draw()
        plt.show()
        
        def _mpl_update(sender, event):
            data = dict(sender)
            subplot.plot(data.keys(), data.values())
            plt.draw()
        
        scan_updated.connect(_mpl_update, self.scan, weak=False)
        

def main():
    sys.exit(Command().run())

if __name__ == '__main__':
    main()