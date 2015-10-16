import boto3facade.utils as utils
from boto3facade.aws import AwsFacade


@utils.cached_client('redshift')
@utils.cached_resource('redshift')
class Redshift(AwsFacade):
    pass
