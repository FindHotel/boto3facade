import boto3facade.utils as utils
from boto3facade.aws import AwsFacade
from boto3facade.exceptions import CredentialsError


@utils.cached_client('redshift')
@utils.cached_resource('redshift')
class Redshift(AwsFacade):
    pass


# Utility methods
def make_copy_s3_credentials(ec2_creds):
    """Creates the credentials parameter for the copy command"""
    if len(ec2_creds) == 2:
        # Permanent credentials: no token
        cr = "aws_access_key_id={};aws_secret_access_key={}".format(
            *ec2_creds)
    elif len(ec2_creds) == 3:
        # Temporary (role) credentials: temporary token
        cr = "aws_access_key_id={};aws_secret_access_key={};token={}".format(
            *ec2_creds)
    else:
        raise CredentialsError("Can't retrieve AWS credentials")
    return cr
