#!/usr/bin/env python
# -*- coding: utf-8 -*-


from boto3facade.aws import AwsFacade
from boto3facade.exceptions import ClientError


class S3(AwsFacade):
    @property
    def service(self):
        return 's3'

    def cp(self, local_path, s3_bucket, s3_key):
        """Uploads a local file to a S3 bucket"""
        try:
            return self.client.upload_file(local_path, s3_bucket, s3_key)
        except ClientError:
            msg = "Error uploading {} to {}/{}".format(
                local_path, s3_bucket, s3_key)
            self.logger.error(msg)
            raise
