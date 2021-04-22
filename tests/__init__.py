# -*- coding: utf-8 -*-
"""Base for pytest testing."""
# standard library imports
import contextlib
import functools
import os
import sys
from pathlib import Path

# third-party imports
import pytest
import sh
from sh import ErrorReturnCode

# global constants
TOML_FILE = "dielectric_relaxation.toml"
COMBINE_OUTPUTS = ["dielectric_relaxation.tsv"]
PLOT_OUTPUTS = []


@contextlib.contextmanager
def working_directory(path):
    """Change working directory in context."""
    prev_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def help_check(subcommand):
    """Test help function for subcommand."""
    print(f"Test {subcommand} help.")
    if subcommand == "global":
        help_command = ["--help"]
    else:
        help_command = [subcommand, "--help"]
    try:
        output = sh.svante(help_command)
    except ErrorReturnCode as errors:
        print(errors)
        pytest.fail(f"{subcommand} help test failed")
    print(output)
    assert "Usage:" in output
    assert "Options:" in output


def print_docstring():
    """Decorator to print a docstring."""

    def decorator(func):
        """Define decorator"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Print docstring and call function"""
            print(func.__doc__)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def run_svante(args, component):
    """Run svante with args."""
    command_string = " ".join(args)
    print(f"Testing {component} with" + f'"svange {command_string}"')
    try:
        sh.svante(
            args,
            _out=sys.stderr,
        )
    except ErrorReturnCode as errors:
        print(errors)
        pytest.fail(f"{component} failed")
