# -*- coding: utf-8 -*-
from .. import TestCase
from fmanalyser.utils.freqlist import fine_tune_frequencies
from fmanalyser.utils.parse import parse_carrier_frequency

class ParsingTest(TestCase):
    
    def test_parse_carrier_frequencies(self):
        strings = []
        f = 87.5
        while f <= 108:
            s = str(f)
            decimal = s.split('.')[1]
            self.assertLessEqual(len(decimal), 2)
            strings.append(str(f))
            f += 0.05
        self.assertEqual(len(strings), len(fine_tune_frequencies))
        for s, f in zip(strings, fine_tune_frequencies):
            self.assertEqual(parse_carrier_frequency(s), f)