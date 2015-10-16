#!/usr/bin/env python
# -*- coding: utf-8 -*-


import boto3facade.utils as utils
from boto3facade.aws import AwsFacade


@utils.cached_client('ec2')
@utils.cached_resource('ec2')
class Ec2(AwsFacade):
    def get_ami_by_tag(self, tags, owners=['self']):
        """Returns the AMIs that match the provided tags"""
        imgs = self.client.describe_images(Owners=owners).get('Images', [])
        sel_imgs = []
        for img in imgs:
            matched = True
            img_tags = {tag['Key']: tag['Value']
                        for tag in img.get('Tags', [])}
            for k, v in tags.items():
                if k not in img_tags or v != img_tags[k]:
                    matched = False
            if matched:
                sel_imgs.append(img)
        return sel_imgs

    def get_vpc_by_tag(self, key, value):
        """Produces the Vpc that matches the requested name"""
        return self._get_resource_by_tag('Vpc', key, value)

    def get_sg_by_tag(self, key, value):
        """Produces a SecurityGroup object that matches the requested name"""
        return self._get_resource_by_tag('SecurityGroup', key, value)
