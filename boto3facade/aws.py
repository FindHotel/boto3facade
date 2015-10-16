#!/usr/bin/env python
# -*- coding: utf-8 -*-


import abc
import boto3facade.utils as utils
import inflection


class AwsFacade():
    """Common facade functionality across AWS service facades"""
    @abc.abstractproperty
    def client(self):
        pass

    @abc.abstractproperty
    def resource(self):
        pass

    def _get_resource_by_tag(self, res_type, key, value):
        """Finds EC2 resources by tags"""
        method = getattr(self.client, "describe_{}s".format(
            inflection.underscore(res_type)))
        resource = getattr(self.resource, res_type)
        return [resource(v[res_type + 'Id']) for v in method()[res_type + 's']
                if utils.has_tag(v.get('Tags', {}), key, value)]
