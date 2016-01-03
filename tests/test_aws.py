#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pytest
from boto3facade.ec2 import Ec2
from boto3facade.aws import Credentials
from boto3facade.exceptions import CredentialsError


@pytest.fixture
def ec2(scope='module'):
    return Ec2()


@pytest.fixture
def ec2_without_creds(scope='module'):
    return Ec2(profile_name='test')


def test_get_credentials(ec2):
    creds = ec2.get_credentials()
    assert isinstance(creds, Credentials)
    assert not set(creds._fields).difference({'key_id', 'secret_key'})


def test_get_credentials_for_empty_profile(ec2_without_creds):
    with pytest.raises(CredentialsError):
        ec2_without_creds.get_credentials()
