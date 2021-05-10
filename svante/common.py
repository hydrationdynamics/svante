# -*- coding: utf-8 -*-
"""Global constants and shared functions in common."""
# standard library imports
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict

import loguru
import toml
import typer
from loguru import logger
from schema import And  # type: ignore
from schema import Optional  # type: ignore
from schema import Schema  # type: ignore
from schema import SchemaError  # type: ignore
from schema import Use  # type: ignore

from . import __doc__ as docstring
from .statsdict import StatsDict

# global constants
DEFAULT_STDERR_LOG_LEVEL = "INFO"
NO_LEVEL_BELOW = 30  # Don't print level for messages below this level
NAME = "svante"


class GlobalState(TypedDict):
    """Dictionary of global state variables."""

    verbose: bool
    log_level: str


STATE: GlobalState = {"verbose": False, "log_level": DEFAULT_STDERR_LOG_LEVEL}


INPUTS_SCHEMA = Schema(
    [
        {
            "uri": And(str, len),
            "T": Schema({"col": int, "uncertainty": Use(float)}),
            "rate": Schema(
                {"name": And(str, len), "uncertainties": And(str, len)}
            ),
        }
    ]
)
COMBINED_SCHEMA = Schema(
    {
        "title": And(str, len),
        "filename": And(str, len),
        "rates": [
            Schema(
                {
                    "name": And(str, len),
                    "label": And(str, len),
                    "line_label_loc": [float],
                }
            )
        ],
    }
)
PLOT_SCHEMA = Schema(
    {
        "secondary_axis_units": And(str, len),
        "y_label": And(str, len),
        "add_fit_values": bool,
        "savefig": Schema(
            {
                "filename": And(str, len),
                "format": And(str, len),
                "dpi": int,
                "facecolor": And(str, len),
                "edgecolor": And(str, len),
                "transparent": bool,
                "pad_inches": float,
            }
        ),
        "ratios": [
            Schema(
                {
                    "numerator": And(str, len),
                    "denominator": And(str, len),
                    "name": And(str, len),
                    "title": And(str, len),
                }
            )
        ],
    }
)
COMBINE_SCHEMA = Schema(
    {
        "inputs": INPUTS_SCHEMA,
        "combined": COMBINED_SCHEMA,
        Optional("plot"): PLOT_SCHEMA,
    }
)
PLOTTING_SCHEMA = Schema(
    {
        Optional("inputs"): INPUTS_SCHEMA,
        "combined": COMBINED_SCHEMA,
        "plot": PLOT_SCHEMA,
    }
)


def _stderr_format_func(record: loguru.Record) -> str:
    """Do level-sensitive formatting."""
    if record["level"].no < NO_LEVEL_BELOW:
        return "<level>{message}</level>\n"
    return "<level>{level}</level>: <level>{message}</level>\n"


logger.remove()
logger.add(sys.stderr, level=STATE["log_level"], format=_stderr_format_func)
APP = typer.Typer(help=docstring, name=NAME)
STATS = StatsDict(logger=logger, app=APP)
# functions used in more than one module


def read_conf_file(
    toml_path: Path,
    file_desc: str,
    schema_type: str,
) -> Any:
    """Read TOML configuration and verify against schema."""
    if not toml_path.exists():
        logger.error(f'{file_desc} file "{toml_path}" does not exist')
        sys.exit(1)
    try:
        toml_dict = toml.load(toml_path)
    except TypeError:
        logger.error(f'Error in {file_desc} filename "{toml_path}"')
        sys.exit(1)
    except toml.TomlDecodeError as e:
        logger.error(f"File {toml_path} is not valid TOML:")
        logger.error(e)
        sys.exit(1)
    if schema_type == "combine":
        file_schema = COMBINE_SCHEMA
    elif schema_type == "plot":
        file_schema = PLOTTING_SCHEMA
    else:
        logger.error(f"unknown schema type {schema_type}")
        sys.exit(1)
    try:
        validated = file_schema.validate(toml_dict)
    except SchemaError as e:
        logger.error(e)
        sys.exit(1)
    return validated
