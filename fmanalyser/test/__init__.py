from ..conf import BaseConfigSection, options
from fmanalyser.conf.source import IniFileSource
import os.path
try:
    from unittest2 import TestCase as BaseTestCase
except ImportError:
    from unittest import TestCase as BaseTestCase

class ConfigSection(BaseConfigSection):
    basename = 'test'
    live_tests = options.BooleanOption(default=True)

class TestCase(BaseTestCase):
    
    @classmethod
    def setUpClass(cls):
        from ..conf import fmconfig
        default_conf_dir = os.path.dirname(fmconfig.DEFAULT_CONF_FILE)
        test_inifile = os.path.join(default_conf_dir, 'test.ini')
        config = fmconfig.fmconfig
        if config.loaded:
            if os.path.exists(test_inifile):
                assert config.source.files == [test_inifile] 
        else:
            config.source = IniFileSource(test_inifile)
        
        cls.conf = config['test']

    def assertIsFrequency(self, f):
        self.assertIsInstance(f, int)
        self.assertLessEqual(f, 108000)
        self.assertGreaterEqual(f, 87500)


    
    
    
    
    
    
    
    
    
    