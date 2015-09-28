# -*- coding: utf-8 -*-

import boto3facade
import os


def test_read_config():
    """Reads the dummyparam from default section"""
    assert boto3facade.read_config('default', 'dummyparam') == 'dummyvalue'
    assert os.path.isfile(os.path.join(os.path.expanduser('~'),
                                       '.boto3facade.ini'))


def test_write_config():
    """Sets value for an existing configuration option"""
    orig_value = boto3facade.read_config('default', 'dummyparam')
    boto3facade.write_config('default', 'dummyparam', 'anothervalue')
    assert boto3facade.read_config('default', 'dummyparam') == 'anothervalue'
    boto3facade.write_config('default', 'dummyparam', orig_value)
