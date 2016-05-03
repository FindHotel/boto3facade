"""Tests the Cloudformation facade."""
import boto3facade.cloudformation as cf
from boto3facade.exceptions import StackNotFoundError
import pytest


def test_get_nonexistent_stack(randomstr):
    c = cf.Cloudformation()
    with pytest.raises(StackNotFoundError):
        c.get_stack_resource(randomstr, "resource_name")
