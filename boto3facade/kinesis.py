"""Kinesis facade."""


from boto3facade.aws import AwsFacade


class Kinesis(AwsFacade):
    @property
    def service(self):
        return 'kinesis'
