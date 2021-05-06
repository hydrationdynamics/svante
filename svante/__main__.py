# -*- coding: utf-8 -*-
"""Command-line interface and logging configuration."""
# standard-library imports
from typing import Optional

import typer

from . import __version__
from .combine import combine
from .common import APP
from .common import STATE
from .plot import plot

# global constants
unused_cli_funcs = (combine, plot)  # noqa: F841


def version_callback(value: bool) -> None:
    """Print version info."""
    if value:
        typer.echo(f"{APP.info.name} version {__version__}")
        raise typer.Exit()


VERSION_OPTION = typer.Option(
    None,
    "--version",
    callback=version_callback,
    help="Print version string.",
)


@APP.callback()
def main(
    verbose: bool = False,
    quiet: bool = False,
    version: Optional[bool] = VERSION_OPTION,
) -> None:
    """Run the APP and do global-state actions."""
    if verbose:
        STATE["verbose"] = True
        STATE["log_level"] = "DEBUG"
    elif quiet:
        STATE["log_level"] = "ERROR"
    unused_state_str = f"{version}"  # noqa: F841


APP()
