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
