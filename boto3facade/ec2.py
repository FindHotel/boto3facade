#!/usr/bin/env python
# -*- coding: utf-8 -*-


import boto3facade.utils as utils
import requests
import json
import os
from boto3facade.aws import AwsFacade
from configparser import ConfigParser
from requests.adapters import ConnectTimeout


@utils.cached_client('ec2')
@utils.cached_resource('ec2')
class Ec2(AwsFacade):
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
        """Produces the Vpc that matches the requested name"""
        return filter(utils.tag_filter('Name', name),
                      self._get_resource('Subnet'))

    def get_sg_by_name(self, name):
        """Produces a SecurityGroup object that matches the requested name"""
        return filter(utils.tag_filter('Name', name),
                      self._get_resource('SecurityGroup'))

    def get_temporary_credentials(self, role_name=None):
        """Produces a tuple of 3 elements: key id, secret key and token"""
        if role_name is not None:
            try:
                resp = requests.get("http://169.254.169.254/latest/meta-data/"
                                    "iam/security-credentials/{}".format(
                                        role_name),
                                    timeout=1)
            except ConnectTimeout:
                # That's OK, probably we are running this outside the AWS cloud
                # and there are no temporary credentials available
                resp = None

            if resp is not None and resp.status_code == 200:
                resp = json.loads(resp.content.decode())
                return (resp['AccessKeyId'],
                        resp['SecretAccessKey'],
                        resp['Token'])

    def get_credentials(self):
        """Produces a tuple with the local AWS credentials"""
        key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        if key_id is None or secret_key is None:
            aws_creds_ini = os.path.join(
                os.path.expanduser('~'), '.aws', 'credentials')
            cfg = ConfigParser()
            cfg.read(aws_creds_ini)
            if 'default' in cfg.sections():
                return (cfg['default']['aws_secret_access_key'],
                        cfg['default']['aws_access_key_id'])
