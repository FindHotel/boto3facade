#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pytest
import boto3facade.s3
from boto3.exceptions import S3UploadFailedError
import tempfile
import os
import uuid


@pytest.fixture(scope='module')
def s3():
    return boto3facade.s3.S3(active_profile='test')


@pytest.yield_fixture(scope='module')
def local_file():
    filename = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    with open(filename, 'w') as f:
        f.write("Hello world!")
    yield filename
    if os.path.isfile(filename):
        os.remove(filename)


@pytest.fixture(scope='module')
def s3bucket(s3):
    return s3.config.profile.get('bucket')


@pytest.yield_fixture(scope='function')
def s3key(s3, s3bucket):
    key = "boto3facade/{}".format(str(uuid.uuid4()))
    yield key
    s3.client.delete_object(Bucket=s3bucket, Key=key)


def test_boto3_client_method(s3, s3bucket):
    s3.client.get_bucket_acl(Bucket=s3bucket)


def test_cp(s3, local_file, s3bucket, s3key):
    s3.cp(local_file, s3bucket, s3key)


def test_cp_invalid_bucket(s3, local_file, s3key):
    s3bucket = str(uuid.uuid4())
    with pytest.raises(S3UploadFailedError):
        s3.cp(local_file, s3bucket, s3key)
