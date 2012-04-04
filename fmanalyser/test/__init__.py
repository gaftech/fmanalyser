from fmanalyser.utils.conf import ConfigSection
import os.path
from unittest2 import TestCase as BaseTestCase
from .. import conf
from nose.plugins.skip import SkipTest
from fmanalyser.client import P175

class TestCase(BaseTestCase):
    
    @classmethod
    def setUpClass(cls):
#        cls._orig_inifile = conf.CONF_FILE
        cls._orig_inifiles = conf.Config.inifiles
        test_inifile = os.path.join(conf.CONF_DIR, 'test.ini')
        if os.path.exists(test_inifile):
            conf.Config.inifiles = [test_inifile]
        cls.global_conf = conf.Config() 
        cls.conf = cls.global_conf['test']
        
    
    @classmethod
    def tearDownClass(cls):
        conf.Config.inifiles = cls._orig_inifiles
        

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
    
    
    
    
    
    
    
    
    
    