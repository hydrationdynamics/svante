# -*- coding: utf-8 -*-
"""Command-line interface and logging configuration."""
# standard-library imports
from __future__ import annotations

import sys
from typing import Optional

import loguru
import typer
from loguru import logger

from .combine import combine
from .common import APP
from .common import STATE
from .common import VERSION
from .plot import plot
# third-party imports
# module imports

# global constants
NO_LEVEL_BELOW = 30  # Don't print level for messages below this level
unused_cli_funcs = (combine, plot)

def stderr_format_func(record: loguru.Record) -> str:
    """Do level-sensitive formatting."""
    if record["level"].no < NO_LEVEL_BELOW:
        return "<level>{message}</level>\n"
    return "<level>{level}</level>: <level>{message}</level>\n"


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{APP.info.name} version {VERSION}")
        raise typer.Exit()


@APP.callback()
def main(
    verbose: bool = False,
    quiet: bool = False,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        help="Print version string.",
    ),
) -> None:
    """Run the APP and do global-state actions."""
    pass
    if verbose:
        STATE["verbose"] = True
        STATE["log_level"] = "DEBUG"
    elif quiet:
        STATE["log_level"] = "ERROR"
    f"{version}"


logger.remove()
logger.add(sys.stderr, level=STATE["log_level"], format=stderr_format_func)
APP()
