# -*- coding: utf-8 -*-
"""This module implements classes to communicate with physical devices"""
from .worker.worker import Worker
from .worker.tasks import BaseTask, CallbackTask, DeviceTask, Sleep 