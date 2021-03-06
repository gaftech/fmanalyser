# -*- coding: utf-8 -*-

from .. import LiveTestCase
from ...values.channel import Channel
import time
from fmanalyser.exceptions import ValidationException

class ValidatorTest(LiveTestCase):
    
    def test_channels(self):
        channel_confs = self.global_conf.get_subsections('channel')
        for conf in channel_confs:
            self.channel_conf = conf
            self.channel = Channel(**conf.values)
            self._set_frequency()
            self.client.set_measuring_mode()

            self._check_frequency()
            self._check_subcarriers(timeout=10)
        
    def _set_frequency(self):
        f = self.channel_conf['frequency']
        self.assertIsFrequency(f)
        self.client.tune(f)
        
    def _check_frequency(self):
        self.assertEqual(
            self.client.get_frequency(),
            self.channel_conf['frequency']
        )
    
    def _check_subcarriers(self, timeout):
        # TODO: Here we're waiting for the device to have made enough measurement.
        #       but  there should have a more appropriate place to do this
        time_limit = time.time() + timeout
        while True:
            rds = self.client.get_rds()
            self.assertIsInstance(rds, float)
            try:
                self.channel.validate('rds', rds)
            except ValidationException:
                if time.time() >= time_limit:
                    raise
                time.sleep(0.5)
            else:
                break
    
    
    
    