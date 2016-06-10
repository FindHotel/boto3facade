"""Configuration management."""

import configparser
import logging
import os
import shutil

from boto3facade import __dir__
from .exceptions import InvalidConfiguration


AWS_CONFIG_DIR = os.path.expanduser('~/.aws')
AWS_CONFIG_FILE = os.path.join(AWS_CONFIG_DIR, 'config')

# Defaults for the Config constructor
DEFAULT_CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.boto3facade.ini')
DEFAULT_ENV_PREFIX = 'BOTO3_'
DEFAULT_ACTIVE_PROFILE = 'default'
DEFAULT_LOGGER = logging.getLogger(__name__)
# The configuration keys that will be configured with Config.configure
DEFAULT_KEYS = ['bucket', 'aws_profile', 'keys_dir']
DEFAULT_REQUIRED_KEYS = ['aws_profile']
# Fallback values for some configuration options
DEFAULT_FALLBACK = {'aws_profile': 'default'}

CONFIG_FILE_TEMPLATE = os.path.join(__dir__, "boto3facade.ini")


class Config:
    def __init__(self, env_prefix=DEFAULT_ENV_PREFIX,
                 config_file=DEFAULT_CONFIG_FILE,
                 config_file_template=CONFIG_FILE_TEMPLATE,
                 active_profile=DEFAULT_ACTIVE_PROFILE,
                 logger=DEFAULT_LOGGER,
                 required_keys=DEFAULT_REQUIRED_KEYS,
                 keys=DEFAULT_KEYS,
                 fallback=DEFAULT_FALLBACK):

        # If a None is provided, use the default
        env_prefix = env_prefix or DEFAULT_ENV_PREFIX
        config_file = config_file or DEFAULT_CONFIG_FILE
        active_profile = active_profile or DEFAULT_ACTIVE_PROFILE
        logger = logger or DEFAULT_LOGGER

        self.env_prefix = env_prefix
        self.active_profile = active_profile
        self.config_file = config_file
        self.logger = DEFAULT_LOGGER
        self.keys = keys
        self.fallback = fallback
        self.required_keys = required_keys

        if not os.path.isfile(config_file):
            shutil.copyfile(config_file_template, config_file)

        self.config = configparser.ConfigParser()
        self.load()

    def configure(self, ask=True, local=False, **kwargs):
        """Configures boto3facade.

        :param ask: If set to False will not ask anything to the user.
        :param local: If True will write config to a local config file.
        """
        if local:
            filename = os.path.basename(self.config_file)
            local_file = os.path.join(os.path.curdir, filename)
            if not os.path.isfile(local_file):
                shutil.copyfile(self.config_file, local_file)
            self.config_file = local_file
            self.load()
        fallback = self.fallback
        for option in self.keys:
            value = kwargs.get(option) or \
                self._get_config(option, ask=ask, fallback=fallback)
            self.set_profile_option(self.active_profile, option, value)

        # We just updated the ini file: reload
        self.profile = self.get_profile(self.active_profile)
        is_ok, msg = self._config_ok()
        if not is_ok:
            raise InvalidConfiguration(msg, logger=self.logger)

    def _read_aws_config(self):
        """Reads the config file used by the AWS CLI and SDK"""
        if not os.path.isdir(AWS_CONFIG_DIR):
            os.makedirs(AWS_CONFIG_DIR)
        cfg = configparser.ConfigParser()
        cfg.read(AWS_CONFIG_FILE)
        return cfg

    def _write_aws_config(self, cfg):
        """Writes a configuration set in the AWS CLI and SDK config file"""
        with open(AWS_CONFIG_FILE, 'w') as f:
            cfg.write(f)

    def _get_config(self, option, ask=True, fallback=None):
        val = self.profile.get(option.lower())
        if val is None or val == '':
            val = os.environ.get("{}{}".format(self.env_prefix,
                                               option.upper()))
        if fallback and val is None:
            val = fallback.get(option.lower())
        if ask:
            resp = input("{} [{}]: ".format(
                option.replace('_', ' ').title(), val))
            if len(resp) > 0:
                return resp
        return val

    def _config_ok(self):
        """Checks that the configuration is not obviously wrong"""
        missing_options = []
        for option in self.required_keys:
            val = self.profile.get(option, None)
            if val is None or len(val) == 0:
                missing_options.append(option)
        if len(missing_options) == 0:
            return True, 'No errors'
        else:
            msg = "Options {} are required".format(missing_options)
            return False, msg

    def activate_profile(self, profile_name):
        """Activates a named profile."""
        self.active_profile = profile_name
        self.load()

    def load(self):
        """Load configuration from ini file."""
        self.config.read(self.config_file)
        self.profile = self.get_profile(self.active_profile)

    def save(self):
        """Save configuration to ini file"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
            # Force flushing the file to disk
            f.flush()
            os.fsync(f.fileno())

    def get(self, section, param):
        """Get configuration option"""
        val = self.config.get(section, param)
        if val != '':
            return val

    def get_profile(self, profile_name):
        """Returns a dict-like object with profile options"""
        section = "profile:{}".format(profile_name)
        if section not in self.config:
            return {k: None for k in DEFAULT_KEYS}
        return self.config[section]

    def remove_profile(self, profile_name):
        """Removes a profile, if it exists. Otherwise does nothing."""
        removed = self.config.remove_section("profile:{}".format(profile_name))
        if removed:
            self.save()

    def get_profile_option(self, profile_name, param):
        """Reads a config option for a profile"""
        try:
            return self.get("profile:{}".format(profile_name), param)
        except configparser.NoOptionError:
            # Return None if an option is not found
            pass

    def initialize_profile(self, profile_name):
        """Initializes a profile in the config file"""
        self.config.add_section("profile:{}".format(profile_name))

    def set(self, section, param, value):
        """Writes a configuration parameter"""
        if not self.config.has_section(section):
            self.config.add_section(section)

        if value is None:
            value = ''
        self.config.set(section, param, value)
        self.save()

    def set_profile_option(self, profile_name, param, value):
        """Writes a profile parameter value"""
        self.set("profile:{}".format(profile_name), param, value)
