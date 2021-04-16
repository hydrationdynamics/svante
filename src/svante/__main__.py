# -*- coding: utf-8 -*-
"""Command-line interface and logging configuration."""

# standard-library imports
import sys
from pathlib import Path
from typing import Optional

# third-party imports
import typer
from loguru import logger

# module imports
from . import __doc__ as docstring
from .common import __version__
from .combine import combine as undeco_combine
from .plot import plot as undeco_plot

# global constants
DEFAULT_STDERR_LOG_LEVEL = 'INFO'
NO_LEVEL_BELOW = 30  # Don't print level for messages below this level
STATE = {'verbose': False,
         'log_level': DEFAULT_STDERR_LOG_LEVEL}

app = typer.Typer(help=docstring, name='svante')


def stderr_format_func(msgdict):
    """Do level-sensitive formatting."""
    if msgdict["level"].no < NO_LEVEL_BELOW:
        return "<level>{message}</level>\n"
    return "<level>{level}</level>: <level>{message}</level>\n"

@app.command()
def combine(toml_file: Path) -> None:
    """Combine rate info from multiple files."""
    undeco_combine(toml_file,
                   verbose=STATE['verbose']
                   )


@app.command()
def plot(
    toml_file: Path,
    nature: bool = typer.Option(False, help='Use Nature style')
) -> None:
    """Arrhenius plot with fits."""
    undeco_plot(toml_file,
                nature=nature,
                verbose=STATE['verbose'])


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f'{app.info.name} {__version__}')
        raise typer.Exit()


@app.callback()
def main(
    verbose: bool = False,
    quiet: bool = False,
    version: Optional[bool] = typer.Option(
        None, '--version', callback=version_callback,
        help='Print version string.'
    ),
) -> None:
    """Run the app and do global-state actions."""
    pass
    if verbose:
        STATE['verbose'] = True
        STATE['log_level'] = 'DEBUG'
    elif quiet:
        STATE['log_level'] = 'ERROR'
    f'{version}'


logger.remove()
logger.add(
    sys.stderr,
    level=STATE['log_level'],
    format=stderr_format_func
)
app()
