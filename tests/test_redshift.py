#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import uuid
import boto3facade.redshift as rs
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


def test_make_copy_s3_temp_credentials(temp_creds):
    creds = rs.make_copy_s3_credentials(temp_creds)
    assert creds == (
        "aws_access_key_id={};"
        "aws_secret_access_key={};"
        "token={}").format(temp_creds.key_id, temp_creds.secret_key,
                           temp_creds.token)


def test_make_copy_s3_local_credentials(local_creds):
    creds = rs.make_copy_s3_credentials(local_creds)
    assert creds == "aws_access_key_id={};aws_secret_access_key={}".format(
        local_creds.key_id, local_creds.secret_key)
