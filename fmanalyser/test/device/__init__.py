from .. import TestCase
from nose.plugins.skip import SkipTest
from fmanalyser.conf.fmconfig import fmconfig
from fmanalyser.device.controllers import core_controllers
from fmanalyser.device.controllers import create_controllers

class LiveTestCase(TestCase):
    
    controller_class = None
    
    @classmethod
    def setUpClass(cls):
        super(LiveTestCase, cls).setUpClass()
        if not cls.conf['live_tests']:
            raise SkipTest('%s : live tests disabled' % cls.__name__)
        
        cls.controllers = [c for c in create_controllers(fmconfig)
                           if c.__class__ is cls.controller_class
                           and c.enabled]
            
    @classmethod
    def tearDownClass(cls):
        for controller in cls.controllers:
            controller.close()