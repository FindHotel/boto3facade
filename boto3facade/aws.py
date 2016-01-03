#!/usr/bin/env python
# -*- coding: utf-8 -*-


import abc
import inflection
import logging
import os
from configparser import ConfigParser
from collections import namedtuple
import boto3facade.utils as utils
from boto3facade.config import Config
from boto3facade.exceptions import (CredentialsError, ProfileNotFoundError,
                                    InitError)
from boto3.session import Session


Credentials = namedtuple('Credentials', 'key_id secret_key')


class AwsFacade():
    """Common facade functionality across AWS service facades"""
    def __init__(self, profile=None, profile_name=None, config_file=None,
                 logger=None):
        """Initializes the proxy object configuration object"""
        self.config = Config(config_file=config_file)

        if profile_name is None:
            # There must be a profile associated to a keyring
            self.profile_name = self.config.get('default', 'profile')
        else:
            self.profile_name = profile_name

        if profile is None:
            # Either the user passes the profile as a dict, or must be read
            # from the config file.
            try:
                self.profile = self.config.get_profile(self.profile_name)
            except ProfileNotFoundError:
                self.config.initialize_profile(self.profile_name)
                self.profile = self.config.get_profile(self.profile_name)
        elif profile_name is None:
            raise InitError("You must provide parameter 'profile_name' when "
                            "providing a 'profile'")
        else:
            self.profile = profile

        if logger is None:
            logger_name = "boto3facade.{}".format(self.service)
            self.logger = logging.getLogger(logger_name)
        else:
            self.logger = logger

        # To cache boto3 stuff
        self.__session = None
        self.__client = None
        self.__resource = None

    @abc.abstractproperty
    def service(self):
        pass

    @property
    def session(self):
        if self.__session is None:
            aws_profile = self.profile.get('aws_profile')
            if aws_profile == '' or aws_profile == 'default':
                # Use the default creds for this system (maybe temporary
                # creds from a role)
                aws_region = self.profile.get('aws_region')
                if aws_region:
                    # Region specified in the boto3facade profile.
                    self.__session = Session(region_name=aws_region)
                else:
                    # Use the settings in ~/.aws/config
                    self.__session = Session()
            else:
                self.__session = Session(
                    profile_name=self.profile.get('aws_profile'))
        return self.__session

    @property
    def client(self):
        if self.__client is None:
            self.__client = self.session.client(self.service)
        return self.__client

    @property
    def resource(self):
        if self.__resource is None:
            self.__resource = self.session.resource(self.service)
        return self.__resource

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
            return (resource(v[AwsFacade._get_id_field(restype)])
                    for v in describe()[restype + 's'])
        else:
            return (r for r in describe()[restype + 's'])

    def get_credentials(self):
        """Produces a tuple with the local AWS credentials"""
        key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        if key_id is None or secret_key is None:
            aws_creds_ini = os.path.join(
                os.path.expanduser('~'), '.aws', 'credentials')
            cfg = ConfigParser()
            cfg.read(aws_creds_ini)
            profiles = cfg.sections()
            if self.profile_name not in profiles:
                msg = ("No credentials for profile {} could be found in "
                       "~/.aws/credentials").format(self.profile_name)
                raise CredentialsError(msg)
            key_id = cfg[self.profile_name]['aws_access_key_id']
            secret_key = cfg[self.profile_name]['aws_secret_access_key']

        if key_id is not None:
            return Credentials(key_id, secret_key)

    @staticmethod
    def _get_id_field(restype):
        if restype == 'SecurityGroup':
            return 'GroupId'
        else:
            return restype + 'Id'
