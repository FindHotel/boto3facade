"""Cloudformation facade."""

import time

from botocore.exceptions import ClientError

from .aws import AwsFacade
from .exceptions import AwsError, NoUpdatesError, StackNotFoundError
from . import utils


CF_TIMEOUT = 10*60
CACHE_TIMEOUT = 5  # seconds


class Cloudformation(AwsFacade):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.__stacks = None

    @property
    def service(self):
        return 'cloudformation'

    @property
    def stacks(self):
        """Produces a list of CF stack description objects."""
        if not self.__stacks or \
                (time.time() - self.__stacks["ts"]) > CACHE_TIMEOUT:
            self.__stacks = {
                'ts': time.time(),
                'stacks': self.client.describe_stacks().get('Stacks', [])}

        return self.__stacks["stacks"]

    @property
    def stack_statuses(self):
        """Returns a dict with the status of every stack in CF"""
        self.flush_cache()
        return self._get_stack_property('StackStatus')

    @property
    def stack_outputs(self):
        """Returns a dict with the outputs for every stack in CF."""
        return self._get_stack_property('Outputs')

    def flush_cache(self):
        """Flush the CF Stacks cache."""
        self.__stacks = None

    def _get_stack_property(self, property_name):
        """Gets the value of certain stack property for every stack in CF."""
        return {s.get('StackName'): s.get(property_name) for s
                in self.stacks}

    def delete_stack(self, stack_name, wait=CF_TIMEOUT):
        """Deletes a CF stack, if it exists in CF."""
        stack_status = self.stack_statuses.get(stack_name)
        if not stack_status or stack_status in \
                {'DELETE_COMPLETE', 'DELETE_IN_PROGRESS'}:
            stack_status = (stack_status, 'not in CF')[stack_status is None]
            msg = "Stack {} is {}: skipping".format(stack_name, stack_status)
            self.config.logger.info(msg)
            return

        self.client.delete_stack(StackName=stack_name)
        self.wait_for_status_change(stack_name, 'DELETE_IN_PROGRESS',
                                    nb_seconds=wait)
        stack_status = self.stack_statuses.get(stack_name)
        if stack_status and stack_status.find('FAILED') > -1:
            msg = "Failed to delete stack {}. Stack status is {}.".format(
                stack_name, stack_status)
            raise AwsError(msg, logger=self.config.logger)

    def create_stack(self, stack_name, template_body, notification_arns, tags,
                     wait=False):
        """Creates a CF stack, unless it already exists."""
        stack_status = self.stack_statuses.get(stack_name)
        if stack_status in {'CREATE_COMPLETE', 'CREATE_IN_PROGRESS'}:
            msg = "Stack {} already in status {}: skipping".format(
                stack_name, stack_status)
            self.config.logger.info(msg)
            self.wait_for_status_change(stack_name, 'CREATE_IN_PROGRESS')
            return

        self.client.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Capabilities=['CAPABILITY_IAM'],
            NotificationARNs=notification_arns,
            Tags=utils.roll_tags(tags))
        if wait:
            self.wait_for_status_change(stack_name, 'CREATE_IN_PROGRESS')
        stack_status = self.stack_statuses.get(stack_name)

        if stack_status and stack_status.find('FAILED') > -1:
            msg = "Failed to create stack {}. Stack status is {}.".format(
                stack_name, stack_status)
            raise AwsError(msg, logger=self.config.logger)

    def update_stack(self, stack_name, template_body, notification_arns,
                     wait=False):
        """Updates an existing stack."""
        stack_status = self.stack_statuses.get(stack_name)
        try:
            self.client.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_IAM'],
                NotificationARNs=notification_arns)
        except ClientError as error:
            msg = error.response.get('Error', {}).get('Message').lower()
            code = error.response.get('Error', {}).get('Code')
            if (code == 'ValidationError' and msg.find('no updates') > -1):
                # Translate into a higher-level exception
                msg = "No updates are to be performed: {}".format(error)
                raise NoUpdatesError(msg)
            else:
                raise

        if wait:
            self.wait_for_status_change(stack_name, 'UPDATE_IN_PROGRESS')
        stack_status = self.stack_statuses.get(stack_name)
        if stack_status.find('FAILED') > -1:
            msg = "Failed to update stack {}. Stack status is {}.".format(
                stack_name, stack_status)
            raise AwsError(msg, logger=self.config.logger)

    def stack_exists(self, stack_name):
        """Checks whether a stack exists in CF."""
        return stack_name in self.stack_statuses

    def stack_ok(self, stack_name):
        """Checks whether a stack is operational."""
        return self.stack_exists(stack_name) and \
            self.stack_statuses.get(stack_name) \
            in {'UPDATE_COMPLETE', 'CREATE_COMPLETE'}

    def wait_for_status_change(self, stack_name, status,
                               nb_seconds=CF_TIMEOUT):
        """Waits for a stack status to change"""
        counter = 0
        curr_status = status
        time.sleep(1)
        while curr_status and curr_status == status:
            time.sleep(1)
            counter += 1
            curr_status = self.stack_statuses.get(stack_name)
            if counter >= nb_seconds:
                msg = ("Stack {stack_name} has stayed over {nb_seconds} "
                       "seconds in status {status}").format(
                    stack_name=stack_name,
                    nb_seconds=nb_seconds,
                    status=status)
                raise AwsError(msg, logger=self.config.logger)

    def get_stack(self, stack_name):
        """Retrieves a stack object using the stack name."""
        y = [stack for stack in self.stacks
             if stack['StackName'] == stack_name]
        if len(y) > 0:
            return self.resource.Stack(y[0]['StackName'])

    def get_stack_resource(self, stack_name, resource_name):
        """Retrieves a resource object from a stack."""
        return [res for res in self.get_stack_resources(stack_name)
                if res.logical_resource_id == resource_name]

    def get_stack_resources(self, stack_name):
        """Retrieves all resources for a stack."""
        stack = self.get_stack(stack_name)
        if not stack:
            msg = "Cannot find stack '{}' in CloudFormation".format(stack_name)
            raise StackNotFoundError(msg)
        return stack.resource_summaries.all()

    def get_stack_outputs(self, stack_name):
        """Retrieves the outputs produced by a Stack."""
        stack = self.get_stack(stack_name)
        return {o['OutputKey']: o['OutputValue'] for o in stack.outputs}

    def get_stack_output(self, stack_name, output_name):
        """Retrieves one stack output."""
        return [v for k, v in self.get_stack_outputs(stack_name).items()
                if k == output_name]

    def get_stack_status(self, stack_name):
        """Gets the current status of a CF stack."""
        stack = self.get_stack(stack_name)
        if stack:
            return stack.stack_status

    def get_stack_events(self, stack_name):
        """Gets a list of stack events sorted by timestamp."""
        stack = self.get_stack(stack_name)
        if stack:
            return sorted(stack.events.all(), key=lambda ev: ev.timestamp)
        else:
            return []
