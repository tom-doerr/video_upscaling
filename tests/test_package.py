"""Tests for package metadata and structure"""

from vidscale import __version__

def test_package_version():
    """Verify package version is set and valid"""
    assert __version__ == "0.1.0"
