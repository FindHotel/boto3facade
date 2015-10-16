#!/usr/bin/env python
# -*- coding: utf-8 -*-


import boto3


def cached_client(service):
    """A class decorator that caches the boto3 client within a instance of a
    boto3 facade object"""

    def decorator(cls):
        cls.__client = None

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
        cls.__client = None

        def get_resource(self):
            if not hasattr(get_resource, 'cached_resource'):
                get_resource.cached_resource = boto3.resource(service)
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
        return unroll_tags(r.tags or {}).get(key, None) == value
    return filtfunc
