#!/usr/bin/env python
# -*- coding: utf-8 -*-


import boto3
import inflection
from botocore.loaders import DataNotFoundError


def cached_client(service):
    """A class decorator that caches the boto3 client within a instance of a
    boto3 facade object"""

    def decorator(cls):

        def get_client(self):
            if not hasattr(get_client, 'cached_client'):
                get_client.cached_client = boto3.client(service)
            return get_client.cached_client

        cls.client = property(get_client)
        return cls

    return decorator


def cached_resource(service):
    """A class decorator that caches boto3 resources within a instance of a
    boto3 facade object"""

    def decorator(cls):

        def get_resource(self):
            if not hasattr(get_resource, 'cached_resource'):
                try:
                    get_resource.cached_resource = boto3.resource(service)
                except DataNotFoundError:
                    get_resource.cached_resource = None
            return get_resource.cached_resource

        cls.resource = property(get_resource)
        return cls

    return decorator


def unroll_tags(tags):
    """Unrolls the tag list of a resource into a dictionary"""
    return {tag['Key']: tag['Value'] for tag in tags}


def has_tag(tags, key, value):
    """Returns true if a resource tag has a given value"""
    return unroll_tags(tags).get(key, None) == value


def tag_filter(key, value):
    """Returns true if a resource tags match the provided tags"""
    def filtfunc(r):
        if isinstance(r, dict):
            return unroll_tags(r.get('Tags', {})).get(key, None) == value
        else:
            return unroll_tags(r.tags or {}).get(key, None) == value
    return filtfunc


def property_filter(key, value):
    """Returns true if a resource property matches the provided value"""
    def filtfunc(r):
        if isinstance(r, dict):
            return r.get(inflection.camelize(key)) == value
        else:
            return getattr(r, inflection.underscore(key)) == value
    return filtfunc
