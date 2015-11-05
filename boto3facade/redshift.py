import boto3facade.utils as utils
import logging
from boto3facade.aws import AwsFacade
from boto3facade.exceptions import CredentialsError


logger = logging.getLogger(__name__)


class InvalidCredentials(Exception):
    pass


@utils.cached_client('redshift')
@utils.cached_resource('redshift')
class Redshift(AwsFacade):
    def get_cluster_by_tag(self, tags, **kwargs):
        """Gets a list of clusters that match the provided set of tags"""
        return self.get_resource_by_tag('Cluster', tags, **kwargs)

    def get_subnet_group_by_name(self, name, **kwargs):
        """Gets the Redshift subnet group with the given name"""
        pass


# Utility methods
def make_copy_s3_credentials(creds):
    """Creates the credentials parameter for the copy command"""
    if creds is None:
        raise InvalidCredentials("Passed None when tuple was expected")
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
