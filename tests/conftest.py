#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
pytest fixtures shared across test modules
"""

import pytest
import shutil
import os
import uuid
import tempfile
from boto3facade.ec2 import Ec2


@pytest.yield_fixture(scope="function")
def randomstr():
    """A random string (an UUID)"""
    yield str(uuid.uuid4())


@pytest.yield_fixture(scope='function')
def random_dir_path():
    """A random but valid directory path in the local file system"""
    dirpath = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    os.mkdir(dirpath)
    yield dirpath
    if os.path.isdir(dirpath):
        shutil.rmtree(dirpath)


@pytest.yield_fixture(scope='function')
def random_file_path(random_dir_path):
    """A random but valid path name in the local file system"""
    filename = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    yield filename
    if os.path.isfile(filename):
        os.remove(filename)


@pytest.fixture(scope="function")
def ec2(random_file_path, random_dir_path):
    """An Ec2 facade object"""
    obj = Ec2(config_file=random_file_path)
    obj.config.set_profile_option(obj.config.active_profile, 'keys_dir',
                                  random_dir_path)
    return obj


@pytest.yield_fixture(scope='module')
def ec2client(ec2):
    """A boto3 EC2 client object"""
    yield ec2.client


@pytest.yield_fixture(scope='module')
def ec2resource(ec2):
    """A boto3 EC2 resource object"""
    yield ec2.resource
