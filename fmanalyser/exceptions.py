# -*- coding: utf-8 -*-

class FmAnalyserException(Exception):
    """Base exception class for all fmanalyser specific exceptions"""

class CommandError(FmAnalyserException):
    """Generic exception to report a command error"""
    def __init__(self, msg, errno=1, *args, **kwargs):
        self.errno = errno
        super(CommandError, self).__init__(msg, *args, **kwargs)

class DeviceError(FmAnalyserException):
    """Base class for device probing or managing errors"""

class DeviceNotFound(DeviceError):
    """Raised when the system can't connect the device"""

class PortLocked(DeviceNotFound):
    """Raised when serial port is already locked"""

class MultipleDevicesFound(DeviceError):
    """Raised when many devices matching a request are connected"""

class DeviceResponseError(DeviceError):
    """Indicates that a response has been received but doesn't match expected criterias"""

class BadResponseFormat(DeviceResponseError):
    """Raised where an incorrectly formatted response is received"""

class SerialError(DeviceError):
    """:class:`serial.serialutil.SerialException` wrapper"""
    def __init__(self, message=None, origin=None, *args, **kwargs):
        self._original = origin
        if message is None and origin is not None:
            message = '%s: %s' % (origin.__class__.__name__, origin)
        super(SerialError, self).__init__(message, *args, **kwargs)
    

class ConfigError(FmAnalyserException):
    """Global class for config related errors"""

class MissingSection(ConfigError):
    """Raised when a required section is not found in configuration""" 

class NoSuchSection(ConfigError):
    """Raised when trying to get a config subsection not defined in config file"""

class UnexpectedSection(ConfigError):
    """Raised when an unexpected section is found in a config"""

class OptionError(ConfigError):
    """Option specific config errors"""

class MissingOption(OptionError):
    """Raised when a required option is not found in configuration"""

class UnexpectedOption(OptionError):
    """Raised when an unexpected option is found in a config"""

class InvalidOption(OptionError):
    """Raised when an option value can't be converted to the appropriate type or doesn't respond to specific requirements"""  

class BadOptionValue(InvalidOption):
    """Raised when an option value doesn't meet a requirement"""

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
    
class OutOfBound(FmAnalyserException):
    """Specific value error"""

class OutOfBoundFrequency(OutOfBound):
    pass
    
    