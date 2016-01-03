#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import uuid
import boto3facade.redshift as rs
import boto3facade.ec2 as ec2
from collections import namedtuple


@pytest.yield_fixture
def temp_creds(scope='module'):
    key_id = str(uuid.uuid4())
    secret_key = str(uuid.uuid4())
    token = str(uuid.uuid4())
    TemporaryCredentials = namedtuple('TemporaryCredentials',
                                      'key_id secret_key token')
    yield TemporaryCredentials(key_id, secret_key, token)


@pytest.yield_fixture
def local_creds(scope='module'):
    key_id = str(uuid.uuid4())
    secret_key = str(uuid.uuid4())
    LocalCredentials = namedtuple('LocalCredentials', 'key_id secret_key')
    yield LocalCredentials(key_id, secret_key)


@pytest.fixture(scope='module')
def redshift():
    return rs.Redshift()


def test_get_temp_copy_credentials(redshift, monkeypatch, temp_creds):
    monkeypatch.setattr(ec2, 'get_temporary_credentials',
                        lambda: temp_creds)
    creds = redshift.get_copy_credentials()
    assert creds == (
        "aws_access_key_id={};"
        "aws_secret_access_key={};"
        "token={}").format(temp_creds.key_id, temp_creds.secret_key,
                           temp_creds.token)


def test_get_local_copy_credentials(redshift, monkeypatch, local_creds):
    monkeypatch.setattr('boto3facade.ec2.get_temporary_credentials',
                        lambda: None)
    monkeypatch.setattr(redshift, 'get_credentials', lambda: local_creds)
    creds = redshift.get_copy_credentials()
    assert creds == "aws_access_key_id={};aws_secret_access_key={}".format(
        local_creds.key_id, local_creds.secret_key)
