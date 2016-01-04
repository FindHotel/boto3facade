#!/usr/bin/env python
# -*- coding: utf-8 -*-


from boto3facade.aws import AwsFacade
from botocore.exceptions import ClientError
from boto3facade.utils import log_exception


class S3(AwsFacade):
    @property
    def service(self):
        return 's3'

    @log_exception(ClientError)
    def cp(self, local_path, s3_bucket, s3_key):
        """Uploads a local file to a S3 bucket"""
        return self.client.upload_file(local_path, s3_bucket, s3_key)

    def exists(s3_bucket, s3_key):
        """Returns True if a key exists in a bucket"""
        pass
