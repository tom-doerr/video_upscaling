"""Pytest configuration and shared fixtures"""

import pytest
from click.testing import CliRunner

@pytest.fixture(scope="module")
def cli_runner():
    """CLI test runner fixture"""
    return CliRunner()
