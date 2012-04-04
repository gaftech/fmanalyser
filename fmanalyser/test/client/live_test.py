# -*- coding: utf-8 -*-
from .. import LiveTestCase
from ...client import P175
from ...utils import freqlist
import random

class P175Test(LiveTestCase):

    def setUp(self):
        super(P175Test, self).setUp()
        self._check_empty_buffer()
#
    def tearDown(self):
        super(P175Test, self).tearDown()
        self._check_empty_buffer()
        
    def _check_empty_buffer(self):
        self.assertTrue(self.client.socket.inWaiting()==0)

    def test_autodetect(self):
        dev = P175._autodetect()
        self.assertRegexpMatches(dev, r'^/dev/ttyUSB\d$')

    def test_get_frequency(self):
        f = self.client.get_frequency()
        self.assertIsFrequency(f)
        
    def test_tune(self):
        f = random.choice(freqlist.frequencies)
        self.client.tune(f)
        self.assertEqual(f, self.client.get_frequency())

    def test_basic_data(self):
        self.skipTest('Work to do !')
        data = self.client.get_basic_data()
        self.assertIsFrequency(data['frequency'])
        self.assertIn(data['quality'], (0,1,2,3,4,5))
        
    def test_get_rds_level(self):
        l = self.client.get_rds_level()
        self.assertIsInstance(l, float)
        












