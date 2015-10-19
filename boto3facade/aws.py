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


def _get_id_field(restype):
    if restype == 'SecurityGroup':
        return 'GroupId'
    else:
        return restype + 'Id'


TemporaryCredentials = namedtuple('TemporaryCredentials',
                                  'key_id secret_key role')

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
        if 'default' in cfg.sections():
            return Credentials(
                cfg['default']['aws_access_key_id'],
                cfg['default']['aws_secret_access_key'])


class AwsFacade():
    """Common facade functionality across AWS service facades"""
    @abc.abstractproperty
    def client(self):
        pass

    @abc.abstractproperty
    def resource(self):
        pass

    def _get_resource(self, restype, **kwargs):
        """Returns a list of AWS resources"""
        method = getattr(self.client, "describe_{}s".format(
            inflection.underscore(restype)))

        def describe():
            return method(**kwargs)

        resource = getattr(self.resource, restype)
        return (resource(v[_get_id_field(restype)])
                for v in describe()[restype + 's'])
