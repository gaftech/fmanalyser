# -*- coding: utf-8 -*-
from fmanalyser.device.controllers.p175 import P175Controller
from fmanalyser.exceptions import ValidationException
from fmanalyser.test.device import LiveTestCase
from fmanalyser.utils import freqlist
from nose.plugins.skip import SkipTest
import random
import time

class P175Test(LiveTestCase):

    controller_class = P175Controller

    def setUp(self):
        super(P175Test, self).setUp()
        self._check_empty_buffer()
#
    def tearDown(self):
        super(P175Test, self).tearDown()
        self._check_empty_buffer()
        
    def _check_empty_buffer(self):
        for ctl in self.controllers:
            self.assertTrue(ctl.device.socket.inWaiting()==0)

    def test_autodetect(self):
        dev = None
        for ctl in self.controllers:
            if ctl.device.port is not None:
                continue
            dev = ctl.device
            break
        
        if dev is None:
            raise SkipTest('No device configured for autodetection')
        port = dev._autodetect()
        self.assertRegexpMatches(port, r'^/dev/ttyUSB\d$')

    def test_get_frequency(self):
        for ctl in self.controllers:
            f = ctl.device.get_frequency()
            self.assertIsFrequency(f)
        
    def test_tune(self):
        for ctl in self.controllers:
            f = random.choice(freqlist.frequencies)
            ctl.device.tune(f)
            self.assertEqual(f, ctl.device.get_frequency())

    def test_basic_data(self):
        self.skipTest('Work to do !')
        for ctl in self.controllers:
            dev = ctl.devive
            data = dev.get_basic_data()
            self.assertIsFrequency(data['frequency'])
            self.assertIn(data['quality'], (0,1,2,3,4,5))
        
    def test_get_rds_level(self):
        for ctl in self.controllers:
            l = ctl.device.get_rds()
            self.assertIsInstance(l, float)
        

class ValidatorTest(LiveTestCase):
    
    controller_class = P175Controller
    
    def test_channels(self):
        for ctl in self.controllers:
            for channel in ctl.channels:
                f = channel.get_frequency()
                if f is not None:
                    self.assertIsFrequency(f)
                    ctl.device.tune(f)
                    self.assertEqual(ctl.device.get_frequency(), f)
                    self._check_subcarriers(timeout=10, device=ctl.device, channel=channel)
        
    def _check_subcarriers(self, timeout, device, channel):
        # TODO: Here we're waiting for the device to have made enough measurement.
        #       but  there should have a more appropriate place to do this
        device.set_measuring_mode()
        time_limit = time.time() + timeout
        while True:
            rds = device.get_rds()
            self.assertIsInstance(rds, float)
            pilot = device.get_pilot()
            self.assertIsInstance(pilot, float)            
            try:
                channel.validate('rds', rds)
                channel.validate('pilot', pilot)
            except ValidationException:
                if time.time() >= time_limit:
                    raise
                time.sleep(0.5)
            else:
                break
    
    
    
    










