"""IAM facade."""


from .aws import AwsFacade


class Iam(AwsFacade):
    @property
    def service(self):
        return 'iam'

    def get_instance_profile_by_id(self, profile_id):
        """Produces an InstanceProfile object for the provided profile Id"""
        profiles = self.client.list_instance_profiles().get('InstanceProfiles')
        if profiles is None:
            return
        pinfo = [p for p in profiles if p['InstanceProfileId'] == profile_id]
        if len(pinfo) < 1:
            return
        return self.resource.InstanceProfile(pinfo[0]['InstanceProfileName'])
