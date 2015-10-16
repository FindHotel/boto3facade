#!/usr/bin/env python
# -*- coding: utf-8 -*-


import abc
import inflection


def _get_id_field(restype):
    if restype == 'SecurityGroup':
        return 'GroupId'
    else:
        return restype + 'Id'


class AwsFacade():
    """Common facade functionality across AWS service facades"""
    @abc.abstractproperty
    def client(self):
        pass

    @abc.abstractproperty
    def resource(self):
        pass

    def _get_resource(self, restype, describe_params=None):
        """Returns a list of AWS resources"""
        method = getattr(self.client, "describe_{}s".format(
            inflection.underscore(restype)))
        if describe_params is not None:
            def describe():
                return method(describe_params)
        else:
            describe = method

        resource = getattr(self.resource, restype)
        return (resource(v[_get_id_field(restype)])
                for v in describe()[restype + 's'])
