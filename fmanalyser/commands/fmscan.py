# -*- coding: utf-8 -*-
from fmanalyser.conf import fmconfig
from fmanalyser.models.bandscan import Bandscan
from fmanalyser.models.signals import scan_updated
from fmanalyser.utils.command import BaseCommand
from optparse import make_option
import subprocess
import sys
import tempfile
import os
import Gnuplot

class Command(BaseCommand):

    base_options = BaseCommand.base_options + (
        make_option('-g', '--gnuplot', action='store_true', default=False,
            help="lauch gnuplot visualization"),
        make_option('-f', '--ref-file', 
            help="reference scanning file location"),
        make_option('-n', '--no-ref', action='store_true', default=False,
            help="don't try to load reference scanning"),
        make_option('-r', '--store-ref', action='store_true',
            help="save data to the scanning reference file")
    )
    
    def alter_conf(self, config):
        if self.options.ref_file:
            config['scan']['ref_file'] = self.options.ref_file
        
    
    def execute(self):
        # config overrides
        fmconfig['scan']['partial'] = 0
        
        # scan object init
        self.scan = Bandscan(**fmconfig['scan'])

        # Visualization init
        if self.options.gnuplot:
            self.init_gnuplot()
        
        # data acquisition
        self.start_worker()
        self.scan.enqueue_update(self.worker)
        while not (self._stop.is_set() or self.scan.is_complete()):
            self.short_sleep()
        
        if self._stop.is_set():
            return
        
        if self.options.store_ref:
            self.scan.save_ref()
        
        if self.options.gnuplot:
            while not self._stop.is_set() and self.gp.poll() is None:
                self.short_sleep()
        
    def init_gnuplot(self):
        self.gpdatafile = tempfile.NamedTemporaryFile(suffix='.fmscan', delete=True)
        self.gp_empty = True
        
        self.gp = subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE)
        self.gp.stdin.write('set xrange [%f:%f]\n' % (self.scan.start,
                                                    self.scan.stop))
        self.gp.stdin.write('set yrange [0:110]\n')
        
        if not self.options.no_ref:
            ref_file = self.scan.ref_file
            if os.path.exists(ref_file):
                self.gp.stdin.write("plot '%s' with lines\n" % ref_file)
        
        scan_updated.connect(self.update_gnuplot, self.scan)
        
    def update_gnuplot(self, sender, event):
        self.gpdatafile.write('%f %f\n' % (event.frequency, event.level))
        self.gpdatafile.flush()
        if self.gp_empty:
            if self.options.no_ref:
                cmd = 'plot'
            else:
                cmd = 'replot'
            self.gp.stdin.write("%s '%s' with lines\n" % (cmd, self.gpdatafile.name))
            self.gp_empty=False
        else:
            self.gp.stdin.write('replot\n')
           

def main():
    sys.exit(Command().run())

if __name__ == '__main__':
    main()