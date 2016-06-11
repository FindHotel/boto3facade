"""Dynamodb facade."""

from .aws import AwsFacade


class Dynamodb(AwsFacade):
    @property
    def service(self):
        return 'dynamodb'
