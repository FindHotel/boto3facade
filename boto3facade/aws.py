#!/usr/bin/env python
# -*- coding: utf-8 -*-


import abc
import inflection
import os
import json
from requests.adapters import ConnectTimeout
from requests.exceptions import ConnectionError
from configparser import ConfigParser
from collections import namedtuple
import requests
import boto3facade.utils as utils
from boto3facade.exceptions import CredentialsError


def _get_id_field(restype):
    if restype == 'SecurityGroup':
        return 'GroupId'
    else:
        return restype + 'Id'


TemporaryCredentials = namedtuple('TemporaryCredentials',
                                  'key_id secret_key token')

Credentials = namedtuple('Credentials', 'key_id secret_key')


def get_temporary_credentials(role_name=None):
    """Produces a tuple of 3 elements: key id, secret key and token"""
    if role_name is not None:
        try:
            resp = requests.get("http://169.254.169.254/latest/meta-data/"
                                "iam/security-credentials/{}".format(
                                    role_name),
                                timeout=1)
        except (ConnectTimeout, ConnectionError):
            # That's OK, probably we are running this outside the AWS cloud
            # and there are no temporary credentials available
            resp = None

        if resp is not None and resp.status_code == 200:
            resp = json.loads(resp.content.decode())
            return TemporaryCredentials(
                resp['AccessKeyId'],
                resp['SecretAccessKey'],
                resp['Token'])


def get_credentials():
    """Produces a tuple with the local AWS credentials"""
    key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    if key_id is None or secret_key is None:
        aws_creds_ini = os.path.join(
            os.path.expanduser('~'), '.aws', 'credentials')
        cfg = ConfigParser()
        cfg.read(aws_creds_ini)
        profiles = cfg.sections()
        if 'default' in profiles:
            profile = 'default'
        elif len(profiles) < 1:
            msg = 'No credentials could be found in ~/.aws/credentials'
            raise CredentialsError(msg)
        else:
            profile = profiles[0]
        key_id = cfg[profile]['aws_access_key_id']
        secret_key = cfg[profile]['aws_secret_access_key']

    if key_id is not None:
        return Credentials(key_id, secret_key)


class AwsFacade():
    """Common facade functionality across AWS service facades"""
    @abc.abstractproperty
    def client(self):
        pass

    @abc.abstractproperty
    def resource(self):
        pass

    def get_resource_by_tag(self, *args, **kwargs):
        """An alias of filter_resource_by_tag"""
        return self.filter_resource_by_tag(*args, **kwargs)

    def filter_resource_by_tag(self, restype, tags, **kwargs):
        """Get the list of resources that match the provided tags"""
        resources = self._get_resource(restype, **kwargs)
        for k, v in tags.items():
            resources = filter(utils.tag_filter(k, v), resources)
        return resources

    def filter_resource_by_property(self, restype, props, **kwargs):
        """Get the list of resources that match the provided properties"""
        resources = self._get_resource(restype, **kwargs)
        for k, v in props.items():
            resources = filter(utils.property_filter(k, v), resources)
        return resources

    def _get_resource(self, restype, **kwargs):
        """Returns a list of AWS resources"""
        method = getattr(self.client, "describe_{}s".format(
            inflection.underscore(restype)))

        def describe():
            return method(**kwargs)

        if self.resource:
            resource = getattr(self.resource, restype)
            return (resource(v[_get_id_field(restype)])
                    for v in describe()[restype + 's'])
        else:
            return (r for r in describe()[restype + 's'])
