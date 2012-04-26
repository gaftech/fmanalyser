# -*- coding: utf-8 -*-

class FmAnalyserException(Exception):
    """Base exception class for all fmanalyser specific exceptions"""

class DeviceNotFound(FmAnalyserException):
    """Raised when the system can't connect the device"""

class PortLocked(DeviceNotFound):
    """Raised when serial port is already locked"""

class MultipleDevicesFound(FmAnalyserException):
    """Raised when many devices matching a request are connected"""

class ConfigError(FmAnalyserException):
    """Global class for config related errors"""

class MissingSection(ConfigError):
    """Raised when a required section is not found in configuration""" 

class MissingOption(ConfigError):
    """Raised when a required option is not found in configuration""" 

class UnexpectedSection(ConfigError):
    """Raised when an unexpected section is found in a config"""

class UnexpectedOption(ConfigError):
    """Raised when an unexpected option is found in a config"""

class InvalidOption(ConfigError):
    """Raised when an option value can't be converted to the appropriate type or doesn't respond to specific requirements"""  

class ValidationException(FmAnalyserException):
    """Raised by validators when a value doesn't match the expected one"""

class QueueFull(FmAnalyserException):
    """Raised by a queue holder if the queue has grew too much"""
    
class Timeout(FmAnalyserException):
    """Generic timeout related exception"""

class WorkerTimeout(Timeout):
    """Thread worker specific timeout Exception"""
    
class TaskTimeout(Timeout):
    """Task specific timeout Exception"""
    
class AlreadyRegistered(FmAnalyserException):
    """Raised when trying to register an already registered element"""