import boto3facade.utils as utils


@utils.cached_client('ec2')
class Redshift:
    pass
