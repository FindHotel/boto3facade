# -*- coding: utf-8 -*-
"""A simple facade for boto3"""

from boto3facade import metadata
import os
import inspect


__version__ = metadata.version
__author__ = metadata.authors[0]
__license__ = metadata.license
__copyright__ = metadata.copyright

__dir__ = os.path.dirname(inspect.getfile(inspect.currentframe()))
__default_config_file__ = os.path.join(__dir__, 'boto3facade.ini')
