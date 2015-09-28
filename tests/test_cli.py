# -*- coding: utf-8 -*-

# The parametrize function is generated, so this doesn't work:
#
#     from pytest.mark import parametrize
#
import pytest
from boto3facade.cli import boto3facade
from click.testing import CliRunner
parametrize = pytest.mark.parametrize


class TestCli(object):
    @parametrize('helparg', ['--help'])
    def test_help(self, helparg, capsys):
        runner = CliRunner()
        result = runner.invoke(boto3facade, [helparg])
        assert result.exit_code == 0
        assert 'boto3facade' in result.output
