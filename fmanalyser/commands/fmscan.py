# -*- coding: utf-8 -*-
from fmanalyser.conf.fmconfig import fmconfig
from fmanalyser.models.bandscan import Bandscan
from fmanalyser.models.signals import scan_updated
from fmanalyser.utils.command import BaseCommand
from optparse import make_option
import subprocess
import sys
import tempfile
import os
from fmanalyser.exceptions import CommandError

class Command(BaseCommand):

    base_options = BaseCommand.base_options + (
        make_option('-g', '--gnuplot', action='store_true', default=False,
            help="lauch gnuplot visualization"),
        make_option('-f', '--ref-file', 
            help="reference scanning file location"),
        make_option('-n', '--no-ref', dest='load_ref', action='store_false', default=True,
            help="don't try to load reference scanning"),
        make_option('-r', '--store-ref', action='store_true',
            help="save data to the scanning reference file"),
        make_option('-o', '--output-file',
            help="save current scan to file")
    )
    
    def alter_conf(self, config):
        if self.options.ref_file:
            config['scan']['ref_file'] = os.path.abspath(self.options.ref_file)
        
    
    def execute(self):
        # config overrides
        fmconfig['scan']['partial'] = 0
        
        # scan object init
        self.scan = Bandscan(**fmconfig['scan'])

        # config checks
        if self.options.load_ref and not os.path.exists(self.scan.ref_file):
            raise CommandError('reference file not found : %s' % self.scan.ref_file)

        # Visualization init
        self.persist = False
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
        
        if self.options.output_file:
            with open(self.options.output_file, 'w') as fp:
                self.scan.dump(fp)
            self.logger.info('file saved: %s' % self.options.output_file)
        
        if self.persist:
            # TODO: make views independant
            while not self._stop.is_set() and self.gp.poll() is None:
                self.short_sleep()
        
    def init_gnuplot(self):
        self.persist = True
        self.gpdatafile = tempfile.NamedTemporaryFile(suffix='.fmscan', delete=True)
        self.gp_empty = True
        
        try:
            self.gp = subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE)
        except OSError:
            raise CommandError("can't open gnuplot, please check if it's installed")
        self.gp.stdin.write('lower\n')
        self.gp.stdin.write('set xrange [%f:%f]\n' % (self.scan.start,
                                                    self.scan.stop))
        self.gp.stdin.write('set yrange [0:110]\n')
        
        self.load_ref = False
        ref_file = self.scan.ref_file
        if self.options.load_ref and os.path.exists(ref_file):
            self.load_ref = True
            self.gp.stdin.write("plot '%s' with lines\n" % ref_file)
        
        scan_updated.connect(self.update_gnuplot, self.scan)
        
    def update_gnuplot(self, sender, event):
        self.gpdatafile.write('%f %f\n' % (event.frequency, event.level))
        self.gpdatafile.flush()
        if self.gp_empty:
            if self.load_ref:
                cmd = 'replot'
            else:
                cmd = 'plot'
            self.gp.stdin.write("%s '%s' with lines\n" % (cmd, self.gpdatafile.name))
            self.gp_empty=False
        else:
            self.gp.stdin.write('replot\n')
           

def main():
    sys.exit(Command().run())

if __name__ == '__main__':
    main()