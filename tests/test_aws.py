#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pytest
import uuid
import boto3facade.aws as aws


@pytest.yield_fixture(scope="module")
def randomstr():
    yield str(uuid.uuid4())


def test_get_temporary_credentials(randomstr):
    creds = aws.get_temporary_credentials(role_name=randomstr)
    assert creds is None
