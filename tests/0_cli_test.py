# -*- coding: utf-8 -*-
"""Tests for basic CLI function."""
# third-party imports
import pytest
import sh

from . import help_check
from . import print_docstring
from . import working_directory

# global constants
svante = sh.Command("svante")


def test_cli():
    """Test global help function."""
    help_check("global")


@print_docstring()
def test_version(tmp_path):
    """Test version command."""
    with working_directory(tmp_path):
        try:
            output = svante(["--version"])
        except sh.ErrorReturnCode as errors:
            print(errors)
            pytest.fail(errors)
        assert "version" in output
