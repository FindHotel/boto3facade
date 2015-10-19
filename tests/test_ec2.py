#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import uuid
from boto3facade.ec2 import Ec2
import boto3


@pytest.yield_fixture(scope="module")
def randomstr():
    yield str(uuid.uuid4())


@pytest.yield_fixture(scope="module")
def ec2():
    yield Ec2()


@pytest.yield_fixture(scope='module')
def ec2client():
    yield boto3.client('ec2')


@pytest.yield_fixture(scope="module")
def testvpc(randomstr, ec2client):
    resp = ec2client.create_vpc(CidrBlock='10.49.0.0/16')
    vpcid = resp['Vpc']['VpcId']
    vpc = boto3.resource('ec2').Vpc(vpcid)
    vpc.create_tags(Tags=[{'Key': 'Name', 'Value': randomstr}])
    yield vpc
    ec2client.delete_vpc(VpcId=vpcid)


@pytest.yield_fixture(scope="module")
def testsubnet(randomstr, ec2client, testvpc):
    resp = ec2client.create_subnet(
        VpcId=testvpc.id,
        CidrBlock='10.49.0.0/24')
    subnetid = resp['Subnet']['SubnetId']
    subnet = boto3.resource('ec2').Subnet(subnetid)
    subnet.create_tags(Tags=[{'Key': 'Name', 'Value': randomstr}])
    yield subnet
    ec2client.delete_subnet(SubnetId=subnetid)


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


def test_get_subnet_by_name(ec2, randomstr, testsubnet):
    subnet = list(ec2.get_subnet_by_name(randomstr))
    assert len(subnet) == 1
    assert subnet[0].id == testsubnet.id
