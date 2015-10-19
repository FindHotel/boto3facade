import boto3facade.utils as utils
import logging
from boto3facade.aws import AwsFacade
from boto3facade.exceptions import CredentialsError


logger = logging.getLogger(__name__)


@utils.cached_client('redshift')
@utils.cached_resource('redshift')
class Redshift(AwsFacade):
    pass


# Utility methods
def make_copy_s3_credentials(creds):
    """Creates the credentials parameter for the copy command"""
    if len(creds) == 2:
        # Permanent credentials: no token
        cr = "aws_access_key_id={};aws_secret_access_key={}".format(
            creds.key_id, creds.secret_key)
    elif len(creds) == 3:
        # Temporary (role) credentials: temporary token
        cr = "aws_access_key_id={};aws_secret_access_key={};token={}".format(
            creds.key_id, creds.secret_key, creds.token)
    else:
        raise CredentialsError("Wrongly formatted credentials: {}".format(
            creds), logger=logger)
    return cr
