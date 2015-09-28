# -*- coding: utf-8 -*-
"""A simple facade for boto3"""

from boto3facade import metadata
from configparser import ConfigParser
import shutil
import os
import inspect


__version__ = metadata.version
__author__ = metadata.authors[0]
__license__ = metadata.license
__copyright__ = metadata.copyright

__dir__ = os.path.dirname(inspect.getfile(inspect.currentframe()))
__default_config_file__ = os.path.join(__dir__, '..',
                                       'boto3facade.ini')
__user_config_file__ = os.path.join(os.path.expanduser('~'),
                                    '.boto3facade.ini')


# Program configuration management
def __initialize_config():
    """Copies the default configuration to the user homedir"""
    shutil.copyfile(__default_config_file__, __user_config_file__)


def __get_config():
    """Gets a ConfigParser object with the current program configuration"""
    if not os.path.isfile(__user_config_file__):
        __initialize_config()

    cp = ConfigParser()
    cp.read(__user_config_file__)
    return cp


def read_config(section, param):
    """Reads a configuration parameter"""
    return __get_config().get(section, param)


def write_config(section, param, value):
    """Writes a configuration parameter"""
    cfg = __get_config()
    if not cfg.has_section(section):
        cfg.add_section(section)

    cfg.set(section, param, value)
    with open(__user_config_file__, 'w') as f:
        cfg.write(f)
