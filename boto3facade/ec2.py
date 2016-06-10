"""EC2 facade."""


from __future__ import print_function

from collections import namedtuple
import json
import logging
import os
import requests
from requests.adapters import ConnectTimeout
from requests.exceptions import ConnectionError

from . import utils
from .iam import Iam
from .aws import AwsFacade
from .exceptions import InvalidInstanceMetadataFieldError


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

    def delete_key_pair(self, keyname):
        """Deletes an keypair in AWS EC2"""
        if self.key_pair_exists(keyname):
            self.client.delete_key_pair(KeyName=keyname)
            return True
        else:
            msg = "Keypair {} does not exist: nothing done"
            self.config.logger.warning(msg)
            return False

    def create_key_pair(self, keyname):
        """Creates a keypair in AWS EC2, if it doesn't exist already"""
        if not self.key_pair_exists(keyname):
            resp = self.client.create_key_pair(KeyName=keyname)
            keypair = self.resource.KeyPair(resp['KeyName'])
            self._save_key_pair(resp)
            return keypair
        else:
            msg = "Keypair {} already exists: not creating".format(keyname)
            self.config.logger.warning(msg)

    def _save_key_pair(self, keypair):
        """Saves an AWS keypair to a local directory"""
        target_dir = self.config.profile.get('keys_dir', os.path.curdir)
        target_dir = os.path.expanduser(target_dir)
        key_name = keypair['KeyName']
        target_file = os.path.join(target_dir, key_name)
        msg = "Saving AWS Key '{}' locally: {}".format(key_name,
                                                       target_file)
        self.config.logger.info(msg)

        if os.path.isfile(target_file):
            msg = "File {} already exists: NOT saving key".format(key_name)
            self.config.logger.info(msg)

        with open(target_file, 'a') as f:
            print(keypair['KeyMaterial'], file=f)

        return target_file

    def key_pair_exists(self, key_name):
        """Returns True if a key exists in AWS"""
        return key_name in [
            k['KeyName'] for k
            in self.client.describe_key_pairs().get('KeyPairs')]
