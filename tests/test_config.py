# -*- coding: utf-8 -*-


import pytest
import uuid
import tempfile
import configparser
import os
from boto3facade.ec2 import Ec2
import boto3facade.config
from boto3facade.config import Config
from boto3facade.exceptions import InvalidConfiguration


@pytest.fixture
def config(scope='module'):
    return Ec2(active_profile='test').config


@pytest.yield_fixture
def dummyparam(config, scope='module'):
    yield 'dummyparam'
    config.config.remove_option('default', 'dummyparam')


@pytest.yield_fixture
def custom_config_file(scope='function'):
    filename = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    yield filename
    if os.path.isfile(filename):
        os.remove(filename)


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
def ec2_config(custom_config_file, custom_profile, scope='module'):
    return Ec2(active_profile=custom_profile,
               config_file=custom_config_file).config


@pytest.fixture
def custom_keys(scope='module'):
    return [str(uuid.uuid4()) for _ in range(5)]


@pytest.fixture
def custom_values(custom_keys, scope='module'):
    return [str(uuid.uuid4()) for _ in range(len(custom_keys))]


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


def test_read_ec2_config(ec2_config, custom_config_file):
    """Reads a parameter from a custom config file"""
    profile_name = ec2_config.get('default', 'profile')
    assert profile_name == 'default'
    assert ec2_config.config_file == custom_config_file
    assert os.path.isfile(custom_config_file)


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
                         custom_fallback, custom_config_file):

    config = Config(
        env_prefix=custom_env_prefix,
        config_file=custom_config_file,
        active_profile=custom_profile,
        keys=custom_keys,
        required_keys=custom_keys,
        fallback=custom_fallback)
    assert config.env_prefix == custom_env_prefix
    assert config.config_file == custom_config_file
    assert config.active_profile == custom_profile
    assert config.keys == custom_keys
    assert config.required_keys == custom_keys
    assert config.fallback == custom_fallback


def test_invalid_configuration(custom_keys, custom_config_file):
    config = Config(
        config_file=custom_config_file,
        keys=custom_keys,
        required_keys=custom_keys)
    with pytest.raises(InvalidConfiguration):
        config.configure(ask=False)


def test_configure_with_envvars(custom_env_prefix, custom_keys, custom_values,
                                custom_config_file, monkeypatch):
    config = Config(
        env_prefix=custom_env_prefix,
        config_file=custom_config_file,
        keys=custom_keys,
        required_keys=custom_keys)

    # Mock the environment
    for k, v in zip(custom_keys, custom_values):
        varname = "{}{}".format(custom_env_prefix, k.upper())
        monkeypatch.setitem(os.environ, varname, v)
    config.configure(ask=False)


def test_aws_signature_version(custom_config_file, custom_aws_config_file,
                               custom_aws_config_dir, monkeypatch):
    monkeypatch.setattr(boto3facade.config, 'AWS_CONFIG_DIR',
                        custom_aws_config_dir)
    monkeypatch.setattr(boto3facade.config, 'AWS_CONFIG_FILE',
                        custom_aws_config_file)
    config = Config(keys=[], required_keys=[])
    config.configure(ask=False)
    # Check the the AWS config file has been properly updated
    cfg = configparser.ConfigParser()
    cfg.read(custom_aws_config_file)
    assert cfg['default'].get('s3') == '\nsignature_version = s3v4'
