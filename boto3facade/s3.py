"""S3 facade."""

from .aws import AwsFacade
from .utils import log_exception

from botocore.exceptions import ClientError


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
