"""Redshift facade."""


from . import ec2
from .aws import AwsFacade
from .exceptions import CredentialsError


class Redshift(AwsFacade):
    @property
    def service(self):
        return 'redshift'

    def get_cluster_by_identifier(self, identifier, **kwargs):
        """Get Redshift cluster by identifier."""
        cluster = [c for c in self.client.describe_clusters()["Clusters"]
                   if c["ClusterIdentifier"] == identifier]
        if cluster:
            return cluster[0]

    def get_current_cluster_snapshot(self, identifier, **kwargs):
        """Get Redshift cluster snapshot by identifier."""
        snapshots = self.get_cluster_snapshots(identifier)
        if snapshots:
            return snapshots[0]

    def get_cluster_snapshots(self, identifier, **kwargs):
        """Get the list of existing cluster snapshots."""
        return sorted([c for c
                       in self.client.describe_cluster_snapshots()["Snapshots"]
                       if c["ClusterIdentifier"] == identifier],
                      key=lambda c: c["SnapshotCreateTime"], reverse=True)

    def get_subnet_group_by_name(self, name, **kwargs):
        """Get the Redshift subnet group with the given name"""
        raise NotImplementedError()

    def get_copy_credentials(self):
        """Produce the credentials parameter for the copy command"""
        # Attempt to get temporary (role) creds
        creds = ec2.get_temporary_credentials()
        if creds is not None:
            return ("aws_access_key_id={};"
                    "aws_secret_access_key={};"
                    "token={}").format(creds.key_id,
                                       creds.secret_key,
                                       creds.token)
        # Attempt to get AWS CLI credentials
        creds = self.get_credentials()
        if creds is None:
            msg = "Unable to retrieve AWS credentials"
            raise CredentialsError(msg, logger=self.config.logger)
        else:
            return "aws_access_key_id={};aws_secret_access_key={}".format(
                creds.key_id, creds.secret_key)
