from ..client import P175
from ..conf import BaseConfigSection, options
from nose.plugins.skip import SkipTest
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
        if config._files != [test_inifile] and os.path.exists(test_inifile):
            config.set_file(test_inifile)
        
        cls.conf = config['test']

    def assertIsFrequency(self, f):
        self.assertIsInstance(f, int)
        self.assertLessEqual(f, 108000)
        self.assertGreaterEqual(f, 87500)

class LiveTestCase(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super(LiveTestCase, cls).setUpClass()
        if not cls.conf['live_tests']:
            raise SkipTest('%s : live tests disabled' % cls.__name__)
        cls.client = P175()
    
    @classmethod
    def tearDownClass(cls):
        cls.client.close()
    
#    def setUp(self):
#        super(LiveTestCase, self).setUp()
#        if not self.conf['live_tests']:
#            self.skipTest('live tests disabled')
    
    
    
    
    
    
    
    
    
    