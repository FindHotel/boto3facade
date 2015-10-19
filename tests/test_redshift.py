#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import uuid
import boto3facade.redshift as rs


@pytest.yield_fixture
def ec2_creds(scope='module'):
    key_id = str(uuid.uuid4())
    secret_key = str(uuid.uuid4())
    token = str(uuid.uuid4())
    yield (key_id, secret_key, token)


def test_make_copy_s3_credentials(ec2_creds):
    creds = rs.make_copy_s3_credentials(ec2_creds[:-1])
    assert creds == "aws_access_key_id={};aws_secret_access_key={}".format(
        *ec2_creds)
    creds = rs.make_copy_s3_credentials(ec2_creds)
    assert creds == (
        "aws_access_key_id={};"
        "aws_secret_access_key={};"
        "token={}").format(*ec2_creds)
