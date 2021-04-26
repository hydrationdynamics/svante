# -*- coding: utf-8 -*-
"""Base for pytest testing."""
# standard library imports
import contextlib
import functools
import os
import sys
from pathlib import Path
from typing import Callable

import pytest
import sh
from sh import ErrorReturnCode
# third-party imports

# global constants
TOML_FILE = "dielectric_relaxation.toml"
COMBINE_INPUTS = [TOML_FILE, "fake_d2o.tsv", "fake_h2o.tsv"]
COMBINE_OUTPUTS = ["dielectric_relaxation.tsv"]


@contextlib.contextmanager
def working_directory(path: str) -> None:
    """Change working directory in context."""
    prev_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def help_check(subcommand: str) -> None:
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


def print_docstring() -> Callable:
    """Decorator to print a docstring."""

    def decorator(func: Callable) -> Callable:
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
