# -*- coding: utf-8 -*-


import pytest
import uuid
import shutil
import tempfile
import os
from boto3facade.ec2 import Ec2
from boto3facade.redshift import Redshift
from boto3facade.config import Config
from boto3facade.exceptions import InvalidConfiguration


@pytest.fixture
def config(scope='module'):
    return Ec2(active_profile='test').config


@pytest.yield_fixture
def dummyparam(config, scope='module'):
    yield 'dummyparam'
    config.config.remove_option('default', 'dummyparam')


@pytest.fixture
def custom_aws_config_dir(scope='module'):
    return tempfile.gettempdir()


@pytest.yield_fixture
def custom_aws_config_file(custom_aws_config_dir, scope='function'):
    filename = os.path.join(custom_aws_config_dir, str(uuid.uuid4()))
    yield filename
    if os.path.isfile(filename):
        os.remove(filename)


@pytest.fixture
def custom_profile(scope='module'):
    return 'test'


@pytest.fixture
def ec2_config(random_file_path, custom_profile, scope='module'):
    return Ec2(active_profile=custom_profile,
               config_file=random_file_path).config


@pytest.fixture
def vanilla_config(random_file_path, scope='module'):
    return Config(config_file=random_file_path)


@pytest.fixture
def custom_fallback(custom_keys, scope='module'):
    # Use a random fallback for the first two keys
    keys = custom_keys[:2]
    return {keys[0]: str(uuid.uuid4()), keys[1]: str(uuid.uuid4())}


@pytest.fixture
def custom_env_prefix(scope='module'):
    return str(uuid.uuid4()).replace('-', '') + '_'


def test_read_config(config):
    """Sets value for an existing configuration option"""
    profile_name = config.get('default', 'profile')
    assert profile_name == 'default'


def test_write_config(config, dummyparam):
    dummyvalue = str(uuid.uuid4())
    config.set('default', dummyparam, dummyvalue)
    config.save()
    config.load()
    assert config.get('default', dummyparam) == dummyvalue


def test_read_ec2_config(ec2_config, random_file_path):
    """Reads a parameter from a custom config file"""
    profile_name = ec2_config.get('default', 'profile')
    assert profile_name == 'default'
    assert ec2_config.config_file == random_file_path
    assert os.path.isfile(random_file_path)


def test_write_config_in_ec2_config(ec2_config, dummyparam, config):
    dummyvalue = str(uuid.uuid4())
    ec2_config.set('default', dummyparam, dummyvalue)
    ec2_config.save()
    ec2_config.load()
    assert ec2_config.get('default', dummyparam) == dummyvalue
    assert config.config_file != ec2_config.config_file
    config.load()
    assert config.get('default', dummyparam) != dummyvalue


def test_constructor_ifc(custom_env_prefix, custom_profile, custom_keys,
                         custom_fallback, random_file_path):

    config = Config(
        env_prefix=custom_env_prefix,
        config_file=random_file_path,
        active_profile=custom_profile,
        keys=custom_keys,
        required_keys=custom_keys,
        fallback=custom_fallback)
    assert config.env_prefix == custom_env_prefix
    assert config.config_file == random_file_path
    assert config.active_profile == custom_profile
    assert config.keys == custom_keys
    assert config.required_keys == custom_keys
    assert config.fallback == custom_fallback


def test_invalid_configuration(blank_config):
    with pytest.raises(InvalidConfiguration):
        blank_config.configure(ask=False)


def test_configure_with_envvars(blank_config):
    # If the fixture ran without errors then we are already good
    pass


def test_configure_local_file(configured_config, monkeypatch):
    # Create a fake home dir
    dirpath = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    os.mkdir(dirpath)
    monkeypatch.setattr(os.path, 'curdir', dirpath)
    orig_file = configured_config.config_file
    configured_config.configure(ask=False, local=True)
    assert orig_file != configured_config.config_file
    assert os.path.dirname(configured_config.config_file) == dirpath
    orig_basename = os.path.basename(orig_file)
    assert os.path.basename(configured_config.config_file) == orig_basename
    # cleanup
    shutil.rmtree(dirpath)


def test_configure_new_local_profile(configured_config, monkeypatch):
    # Create a fake home dir
    dirpath = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    os.mkdir(dirpath)
    monkeypatch.setattr(os.path, 'curdir', dirpath)
    orig_file = configured_config.config_file
    profile_name = str(uuid.uuid4())
    configured_config.activate_profile(profile_name)
    configured_config.configure(ask=False, local=True)
    assert orig_file != configured_config.config_file
    assert os.path.dirname(configured_config.config_file) == dirpath
    orig_basename = os.path.basename(orig_file)
    assert os.path.basename(configured_config.config_file) == orig_basename
    # cleanup
    shutil.rmtree(dirpath)


def test_constructor_with_config_object(vanilla_config):
    rs = Redshift(config=vanilla_config)
    assert rs.config.config_file == vanilla_config.config_file
