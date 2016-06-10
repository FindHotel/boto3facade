"""Kms facade."""


from boto3facade.aws import AwsFacade


class Kms(AwsFacade):
    @property
    def service(self):
        return 'kms'
