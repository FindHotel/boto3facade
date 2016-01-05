#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import os
from boto3facade.ec2 import (TemporaryCredentials,
                             get_temporary_credentials)
from botocore.exceptions import ClientError
from collections import namedtuple
import time


@pytest.yield_fixture(scope="function")
def testvpc(randomstr, ec2client, ec2resource):
    resp = ec2client.create_vpc(CidrBlock='10.49.0.0/16')
    vpcid = resp['Vpc']['VpcId']
    vpc = ec2resource.Vpc(vpcid)
    vpc.create_tags(Tags=[{'Key': 'Name', 'Value': randomstr}])
    yield vpc
    try:
        ec2client.delete_vpc(VpcId=vpcid)
    except ClientError:
        # Wait for dependencies to be deleted and retry
        time.sleep(3)
        ec2client.delete_vpc(VpcId=vpcid)


@pytest.yield_fixture(scope="function")
def testsg(randomstr, ec2client, ec2resource, testvpc):
    resp = ec2client.create_security_group(
        GroupName=randomstr, Description='test group (delete me!)',
        VpcId=testvpc.id)
    sgid = resp['GroupId']
    sg = ec2resource.SecurityGroup(sgid)
    sg.create_tags(Tags=[{'Key': 'Name', 'Value': randomstr}])
    yield sg
    ec2client.delete_security_group(GroupId=sg.id)


@pytest.yield_fixture(scope="function")
def testsubnet(randomstr, ec2client, ec2resource, testvpc):
    resp = ec2client.create_subnet(
        VpcId=testvpc.id,
        CidrBlock='10.49.0.0/24')
    subnetid = resp['Subnet']['SubnetId']
    subnet = ec2resource.Subnet(subnetid)
    subnet.create_tags(Tags=[{'Key': 'Name', 'Value': randomstr}])
    yield subnet
    ec2client.delete_subnet(SubnetId=subnetid)


@pytest.yield_fixture(scope="function")
def testkeypair(randomstr, ec2):
    keyname = 'test-' + randomstr
    yield keyname
    ec2.delete_key_pair(keyname)
    local_key = os.path.join(ec2.config.profile.get('keys_dir'),
                             randomstr)
    if os.path.isfile(local_key):
        os.remove(local_key)


def test_get_ami_by_tag_no_match(ec2, randomstr):
    """Try to retrieve by tag an AMI that does not exist"""
    ami_id = ec2.get_ami_by_tag({'Name': randomstr})
    assert ami_id == []


def test_get_ami_by_name_no_match(ec2, randomstr):
    ami = ec2.get_ami_by_name(randomstr)
    assert list(ami) == []


def test_get_sg_by_name_no_match(ec2, randomstr):
    ami = ec2.get_sg_by_name(randomstr)
    assert list(ami) == []


def test_get_vpc_by_name_no_math(ec2, randomstr):
    vpc = ec2.get_vpc_by_name(randomstr)
    assert list(vpc) == []


def test_get_subnet_by_name_no_math(ec2, randomstr):
    subnet = ec2.get_subnet_by_name(randomstr)
    assert list(subnet) == []


def test_get_vpc_by_name(ec2, randomstr, testvpc):
    vpc = list(ec2.get_vpc_by_name(randomstr))
    assert len(vpc) == 1
    assert vpc[0].id == testvpc.id


def test_filter_resource_by_property(ec2, randomstr, testsg):
    sg = list(ec2.get_sg_by_name(randomstr))
    assert len(sg) == 1
    assert sg[0].id == testsg.id


def test_get_subnet_by_name(ec2, randomstr, testsubnet):
    subnet = list(ec2.get_subnet_by_name(randomstr))
    assert len(subnet) == 1
    assert subnet[0].id == testsubnet.id


def test_get_temporary_credentials_in_ec2(monkeypatch):
    monkeypatch.setattr('boto3facade.ec2.in_ec2', lambda: True)
    Role = namedtuple('Role', 'name')

    def get_role():
        return Role('dummyrole')

    monkeypatch.setattr('boto3facade.ec2.get_instance_profile_role', get_role)

    def get_metadata(field):
        if field == 'iam/security-credentials/dummyrole':
            return {'AccessKeyId': 'blahblah',
                    'SecretAccessKey': 'yeahyeah',
                    'Token': 'pupu'}

    monkeypatch.setattr('boto3facade.ec2.get_instance_metadata', get_metadata)
    creds = get_temporary_credentials()
    # Running tests in an EC2 instance: must have a role associated to it
    assert isinstance(creds, TemporaryCredentials)
    expected_fields = {'key_id', 'secret_key', 'token'}
    assert not set(creds._fields).difference(expected_fields)


def test_get_temporary_credentials_outside_ec2(monkeypatch):
    monkeypatch.setattr('boto3facade.ec2.in_ec2', lambda: False)
    creds = get_temporary_credentials()
    assert creds is None


def test_key_pairs(ec2, testkeypair):
    assert not ec2.key_pair_exists(testkeypair)
    keypair = ec2.create_key_pair(testkeypair)
    assert type(keypair).__name__ == 'ec2.KeyPairInfo'
    keysdir = os.path.expanduser(ec2.config.profile['keys_dir'])
    local_key = os.path.join(keysdir, testkeypair)
    assert os.path.isfile(local_key)
