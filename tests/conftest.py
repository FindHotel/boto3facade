"""Global fixtures."""
import os
import shutil
import tempfile

import pytest
import uuid

import boto3facade.config
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


@pytest.fixture
def custom_keys(scope='module'):
    return [str(uuid.uuid4()) for _ in range(5)]


@pytest.fixture
def custom_values(custom_keys, scope='module'):
    return [str(uuid.uuid4()) for _ in range(len(custom_keys))]


@pytest.fixture(scope="function")
def blank_config(custom_env_prefix, custom_keys, custom_values,
                 random_file_path):
    """A boto3facace.config object."""
    return boto3facade.config.Config(
        env_prefix=custom_env_prefix,
        config_file=random_file_path,
        keys=custom_keys,
        required_keys=custom_keys)


@pytest.fixture(scope="function")
def configured_config(blank_config, custom_env_prefix, custom_keys,
                      custom_values, monkeypatch):
    # Mock the environment
    for k, v in zip(custom_keys, custom_values):
        varname = "{}{}".format(custom_env_prefix, k.upper())
        monkeypatch.setitem(os.environ, varname, v)
    blank_config.configure(ask=False)
    return blank_config


@pytest.yield_fixture(scope='function')
def ec2client(ec2):
    """A boto3 EC2 client object"""
    yield ec2.client


@pytest.yield_fixture(scope='function')
def ec2resource(ec2):
    """A boto3 EC2 resource object"""
    yield ec2.resource
