#!/usr/bin/env python
# -*- coding: utf-8 -*-


class LoggedException(Exception):
    """Logs an exception message as a critical event"""
    def __init__(self, msg, logger=None):
        if logger:
            logger.critical(msg)
        super().__init__(msg)


class CredentialsError(LoggedException):
    """Unable to retrieve credentials for some service"""
    pass


class ProfileNotFoundError(LoggedException):
    """The specified profile could not be found in the local config files"""
    pass


class InitError(LoggedException):
    """Error initializing a proxy object"""
    pass


class InvalidConfiguration(LoggedException):
    """The module configuration has errors"""
    pass


class InvalidInstanceMetadataFieldError(LoggedException):
    """Trying to retrieve an invalid instance metadata field"""
    pass


class AwsError(LoggedException):
    """An error produced by AWS."""
    pass
