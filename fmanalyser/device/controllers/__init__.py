"""Device controllers aims to link :class:`..Device` instances with :mod:`fmanalyser.models` data models
"""
from fmanalyser.device.controllers.base import DeviceController
from fmanalyser.exceptions import BadOptionValue
from fmanalyser.models.bandscan import Bandscan
from fmanalyser.models.channel import Channel
from fmanalyser.utils.import_tools import get_class

_core_controllers = {
    'p175':          'p175.P175Controller',
    'funcube':      'funcube.FuncubeController',
    'rtl':          'rtl2832.Rtl2832Controller',
    'grrtl':        'gr_rtl2832.GrRtl2832Controller',
    'si4735_ar':    'si4735_shield_arduino.Si4735ArduinoShieldController',
}

def get_controller_class(model_name):
    class_path = 'fmanalyser.device.controllers.%s' % (_core_controllers[model_name],)
    return get_class(class_path)

def create_controllers(config, enabled_only=True):
    
    channels = {}
    for channel_name, channel_conf in config.iter_section_or_subsections('channel'):
#        ctl_name = channel_conf.pop('device', None)
        ctl_name = channel_conf.get('device') # TODO: device option (that points to a controller)
#                                             # should not be associated to a model
#                                             # (same thing about scan below) 
        channel = Channel.from_config_dict(channel_conf, name=channel_name) #TODO: call from_config might be cleaner
        channels.setdefault(ctl_name, []).append(channel)
    
    scans = {}
    for scan_name, scan_conf in config.iter_section_or_subsections('scan'):
#        ctl_name = scan_conf.pop('device', None)
        ctl_name = scan_conf.get('device')
        scan = Bandscan.from_config(config, subname=scan_name)
        scans.setdefault(ctl_name,[]).append(scan)
    
    controllers = []
    for ctl_name, dev_conf in config.iter_section_or_subsections('device'):
        dev_conf.setdefault('enabled', True)
        controller = DeviceController.from_config_dict(  #TODO: call from_config might be cleaner
            dev_conf,
            name = ctl_name,
            channels = channels.pop(ctl_name, ()),
            scans = scans.pop(ctl_name, ()),
        )

        if not enabled_only or controller.enabled:
            controllers.append(controller)
    
    if len(channels):
        raise BadOptionValue('invalid channel controller(s): %s' % ', '.join(channels))
    if len(scans):
        raise BadOptionValue('invalid bandscan controller(s): %s' % ', '.join(scans))
    
    return controllers