#!/usr/bin/env python
# -*- coding: utf-8 -*-


import boto3facade.ec2 as ec2
from boto3facade.aws import AwsFacade
from boto3facade.exceptions import CredentialsError


class Redshift(AwsFacade):
    @property
    def service(self):
        return 'redshift'

    def get_cluster_by_tag(self, tags, **kwargs):
        """Gets a list of clusters that match the provided set of tags"""
        return self.get_resource_by_tag('Cluster', tags, **kwargs)

    def get_subnet_group_by_name(self, name, **kwargs):
        """Gets the Redshift subnet group with the given name"""
        raise NotImplementedError()

    def get_copy_credentials(self):
        """Produces the credentials parameter for the copy command"""
        # Attempt to get temporary (role) creds
        creds = ec2.get_temporary_credentials()
        if creds is not None:
            return ("aws_access_key_id={};"
                    "aws_secret_access_key={};"
                    "token={}").format(creds.key_id,
                                       creds.secret_key,
                                       creds.token)
        # Attempt to get AWS CLI credentials
        creds = self.get_credentials()
        if creds is None:
            msg = "Unable to retrieve AWS credentials"
            raise CredentialsError(msg, logger=self.config.logger)
        else:
            return "aws_access_key_id={};aws_secret_access_key={}".format(
                creds.key_id, creds.secret_key)
