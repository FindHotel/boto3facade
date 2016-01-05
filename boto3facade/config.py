#!/usr/bin/env python
# -*- coding: utf-8 -*-


import configparser
import shutil
import os
import boto3facade
import logging
from boto3facade.exceptions import ProfileNotFoundError, InvalidConfiguration


AWS_CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.aws')
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
DEFAULT_FALLBACK = {}


class Config:
    def __init__(self, env_prefix=DEFAULT_ENV_PREFIX,
                 config_file=DEFAULT_CONFIG_FILE,
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
            shutil.copyfile(boto3facade.__default_config_file__, config_file)

        self.config = configparser.ConfigParser()
        self.load()

    def configure(self, ask=True, **kwargs):
        """Configures the keyring, requesting user input if necessary"""
        fallback = self.fallback
        for option in self.keys:
            value = kwargs.get(option) or \
                self._get_config(option, ask=ask, fallback=fallback)
            self.set_profile_option(self.active_profile, option, value)

        # We just updated the ini file: reload
        self.profile = self.get_profile(self.active_profile)
        self._configure_signature()
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

    def _configure_signature(self):
        """Sets up the AWS profile to use signature version 4"""
        aws_profile = self.get_profile_option(self.active_profile,
                                              'aws_profile')
        if aws_profile is None or aws_profile == 'default':
            section = 'default'
        else:
            section = "profile " + aws_profile

        cfg = self._read_aws_config()
        if section in cfg.sections():
            cfg[section]['s3'] = "\nsignature_version = s3v4"
        else:
            cfg[section] = {'s3': "\nsignature_version = s3v4"}
        self._write_aws_config(cfg)

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

    def load(self):
        """Load configuration from ini file"""
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
            raise ProfileNotFoundError(
                "Profile {} not found".format(profile_name))
        return self.config[section]

    def remove_profile(self, profile_name):
        """Removes a profile, if it exists. Otherwise does nothing."""
        removed = self.config.remove_section("profile:{}".format(profile_name))
        if removed:
            self.save()

    def get_profile_option(self, profile_name, param):
        """Reads a config option for a profile"""
        return self.get("profile:{}".format(profile_name), param)

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
