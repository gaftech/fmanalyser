"""Device controllers aims to link :class:`..Device` instances with :mod:`fmanalyser.models` data models
"""
from fmanalyser.exceptions import BadOptionValue
from fmanalyser.models.bandscan import Bandscan
from fmanalyser.models.channel import Channel
from .p175 import P175Controller

core_controllers = {
    'p175': P175Controller,
}

def get_controller_class(model_name):
    return core_controllers[model_name]

def create_controllers(config, enabled_only=True):
    
    channels = {}
    for channel_section in config.get_section_or_subsections('channel'):
        channel_conf = channel_section.values.copy()
        ctl_name = channel_conf.pop('device', None)
        channel = Channel(name=channel_section.subname, **channel_conf)
        channels.setdefault(ctl_name, []).append(channel)
    
    scans = {}
    for scan_section in config.get_section_or_subsections('scan'):
        scan_conf = scan_section.values.copy()
        ctl_name = scan_conf.pop('device', None)
        scan = Bandscan(name=scan_section.subname, **scan_conf)
        scans.setdefault(ctl_name,[]).append(scan)
    
    controllers = []
    for dev_section in config.get_section_or_subsections('device'):
        ctl_kwargs = dev_section.values.copy()
        ctl_cls = get_controller_class(ctl_kwargs.pop('model'))
        ctl_name = dev_section.subname
        controller = ctl_cls(name=ctl_name,
                             channels=channels.pop(ctl_name),
                             scans=scans.pop(ctl_name),
                             **ctl_kwargs)
        if not enabled_only or controller.enabled:
            controllers.append(controller)
    
    if len(channels):
        raise BadOptionValue('invalid channel controller(s): %s' % ', '.join(channels))
    if len(scans):
        raise BadOptionValue('invalid bandscan controller(s): %s' % ', '.join(scans))
    
    return controllers