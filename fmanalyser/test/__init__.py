from fmanalyser import conf
from fmanalyser.conf import fmconfig
from fmanalyser.conf.source import IniFileSource
import os.path
try:
    from unittest2 import TestCase as BaseTestCase
except ImportError:
    from unittest import TestCase as BaseTestCase

class ConfigSection(conf.OptionHolder):
    section_name = 'test'
    live_tests = conf.options.BooleanOption(default=True)

class TestCase(BaseTestCase):
    
    @classmethod
    def setUpClass(cls):
        default_conf_dir = os.path.dirname(conf.DEFAULT_CONF_FILE)
        test_inifile = os.path.join(default_conf_dir, 'test.ini')
        if fmconfig.loaded:
            if os.path.exists(test_inifile):
                source = fmconfig.source
                assert source._files == [test_inifile] 
        elif os.path.exists(test_inifile):
            fmconfig.source = IniFileSource(test_inifile)
        
        cls.conf = ConfigSection.from_config(fmconfig)

    def assertIsFrequency(self, f):
        self.assertIsInstance(f, int)
        self.assertLessEqual(f, 108000)
        self.assertGreaterEqual(f, 87500)


    
    
    
    
    
    
    
    
    
    