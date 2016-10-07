"""Generic AWS facade class."""

import abc
import inflection
import os
from configparser import ConfigParser
from collections import namedtuple

import botocore.config
from boto3.session import Session

from . import utils
from .config import Config
from .exceptions import CredentialsError


Credentials = namedtuple('Credentials', 'key_id secret_key')


class AwsFacade(object):
    """Common facade functionality across AWS service facades"""
    def __init__(self, config=None, **kwargs):
        """Initializes the proxy object configuration object"""

        if config is None:
            self.config = Config(**kwargs)
        else:
            self.config = config

        # To cache boto3 stuff
        self.__session = None
        self.__client = None
        self.__resource = None
        self.__botocore_config = None

    @abc.abstractproperty
    def service(self):
        pass

    @property
    def session(self):
        if self.__session is None:
            aws_profile = self.config.profile.get('aws_profile')
            if aws_profile == '' or aws_profile == 'default':
                # Use the default creds for this system (maybe temporary
                # creds from a role)
                aws_region = self.config.profile.get('aws_region') or \
                    os.environ.get("AWS_REGION") or \
                    os.environ.get("AWS_DEFAULT_REGION")
                if aws_region:
                    # Region specified in the boto3facade profile.
                    self.__session = Session(region_name=aws_region)
                else:
                    # Use the settings in ~/.aws/config
                    self.__session = Session()
            else:
                self.__session = Session(
                    profile_name=self.config.profile.get('aws_profile'))
        return self.__session

    @property
    def botocore_config(self):
        """Advanced client/resource configuration options."""
        if self.__botocore_config is None:
            # Among other things, using KMS with S3 requires v4
            self.__botocore_config = botocore.config.Config(
                signature_version="s3v4")
        return self.__botocore_config

    @property
    def client(self):
        if self.__client is None:
            self.__client = self.session.client(
                self.service, config=self.botocore_config)
        return self.__client

    @property
    def resource(self):
        if self.__resource is None:
            self.__resource = self.session.resource(
                self.service, config=self.botocore_config)
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
            if self.config.active_profile not in profiles:
                msg = ("No credentials for profile {} could be found in "
                       "~/.aws/credentials").format(self.config.active_profile)
                raise CredentialsError(msg)
            aws_profile = self.config.profile.get('aws_profile')
            key_id = cfg[aws_profile]['aws_access_key_id']
            secret_key = cfg[aws_profile]['aws_secret_access_key']

        if key_id is not None:
            return Credentials(key_id, secret_key)

    @staticmethod
    def _get_id_field(restype):
        if restype == 'SecurityGroup':
            return 'GroupId'
        else:
            return restype + 'Id'
