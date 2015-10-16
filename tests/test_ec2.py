#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import uuid
from boto3facade.ec2 import Ec2


@pytest.yield_fixture(scope="module")
def randomstr():
    yield str(uuid.uuid4())


@pytest.yield_fixture(scope="module")
def ec2():
    yield Ec2()


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
