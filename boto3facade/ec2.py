#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import logging
import boto3facade.utils as utils
from boto3facade.iam import Iam
from boto3facade.aws import AwsFacade
from collections import namedtuple
import requests
from requests.adapters import ConnectTimeout
from requests.exceptions import ConnectionError
from boto3facade.exceptions import InvalidInstanceMetadataFieldError


logger = logging.getLogger(__name__)


TemporaryCredentials = namedtuple('TemporaryCredentials',
                                  'key_id secret_key token')


def get_temporary_credentials():
    """Produces a tuple of 3 elements: key id, secret key and token"""
    # The Role attached to the instance profile associated with the current EC2
    # instance at launch
    role = get_instance_profile_role()
    if role is None:
        # Either not running in AWS-EC2 or no role has been associated to the
        # instance
        return

    creds = get_instance_metadata('iam/security-credentials/' + role.name)
    return TemporaryCredentials(creds['AccessKeyId'],
                                creds['SecretAccessKey'],
                                creds['Token'])


def get_instance_profile_role():
    """Gets the role name for the current instance, if any"""
    info = get_instance_metadata('iam/info')
    if info:
        profile_id = info.get('InstanceProfileId')
        if profile_id:
            iam = Iam()
            iprofile = iam.get_instance_profile_by_id(profile_id)
            roles = iprofile.roles_attribute
            if len(roles) < 1:
                return
            return iam.resource.Role(roles[0]['RoleName'])


def in_ec2():
    """Returns true if running within an EC2 instance"""
    try:
        requests.get("http://169.254.169.254/latest/meta-data/hostname",
                     timeout=1)
        return True
    except (ConnectTimeout, ConnectionError):
        return False


def get_instance_metadata(field):
    """Gets instance meta-data from the currently running EC2 instances"""
    if not in_ec2():
        return
    try:
        resp = requests.get("http://169.254.169.254/latest/meta-data/" + field,
                            timeout=1)
        if resp is not None and resp.status_code == 200:
            return json.loads(resp.content.decode())
    except (ConnectTimeout, ConnectionError):
        # Probably not running in an EC2 instance
        msg = "Unable to retrieve instance meta-data '{}'".format(field)
        raise InvalidInstanceMetadataFieldError(msg, logger=logger)


class Ec2(AwsFacade):
    @property
    def service(self):
        return 'ec2'

    def get_ami_by_tag(self, tags, owners=['self']):
        """Returns the AMIs that match the provided tags"""
        imgs = self.client.describe_images(Owners=owners).get('Images', [])
        sel_imgs = []
        for img in imgs:
            matched = True
            img_tags = utils.unroll_tags(img.get('Tags', {}))
            for k, v in tags.items():
                if k not in img_tags or v != img_tags[k]:
                    matched = False
            if matched:
                sel_imgs.append(img)
        return sel_imgs

    def get_ami_by_name(self, name):
        """Returns AMIs with a matching Name tag"""
        return filter(utils.tag_filter('Name', name),
                      self._get_resource('Image', Owners=['self']))

    def get_vpc_by_name(self, name):
        """Produces the Subnet that matches the requested name"""
        return filter(utils.tag_filter('Name', name),
                      self._get_resource('Vpc'))

    def get_subnet_by_name(self, name):
        """Produces the Subnet that matches the requested name"""
        return filter(utils.tag_filter('Name', name),
                      self._get_resource('Subnet'))

    def get_sg_by_name(self, name):
        """Produces a SecurityGroup object that matches the requested name"""
        props = {'GroupName': name}
        return self.filter_resource_by_property('SecurityGroup', props)
