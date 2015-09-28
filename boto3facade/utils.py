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
