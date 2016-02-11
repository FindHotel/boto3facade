#!/usr/bin/env python
# -*- coding: utf-8 -*-


from boto3facade.aws import AwsFacade


class Kms(AwsFacade):
    @property
    def service(self):
        return 'kms'
