# -*- coding: utf-8 -*-
"""Global constants and other objects in common."""
# standard library imports
import sys
from pathlib import Path
from typing import TypedDict

import toml
import typer
from loguru import logger  # type: ignore
from schema import And  # type: ignore
from schema import Optional  # type: ignore
from schema import Schema  # type: ignore
from schema import SchemaError  # type: ignore
from schema import Use  # type: ignore

from . import __doc__ as docstring
from .stat_dict import StatDict
# third-party imports
# module imports

# global constants
__version__ = "0.0.0"
VERSION = __version__
DEFAULT_STDERR_LOG_LEVEL = "INFO"

class StateDict(TypedDict):
    """Dictionary of global state variables."""
    verbose: bool
    log_level: str


STATE: StateDict = {"verbose": False, "log_level": DEFAULT_STDERR_LOG_LEVEL}
APP = typer.Typer(help=docstring, name="svante")
GLOBAL_STATS = StatDict()
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
        "rates": [Schema({"name": And(str, len), "title": And(str, len)})],
    }
)
PLOT_SCHEMA = Schema(
    {
        "secondary_axis_units": And(str, len),
        "add_fit_values": bool,
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
# GLOBAL_STATS["Δ H"] = 4223  # , 20.02, "kJ/mol", desc='Activation Enthalpy',)
# print(GLOBAL_STATS)
# b = Stat(23.37, units="K", sig_digits=3, desc="Temperature")
# print(b)
# c = Stat("This is not a quantity [or is it?]", desc="random description")
# print(c)
# d = Stat(True, desc="test of boolean")
# print(d)
#
# sys.exit(1)
# functions used in more than one module
def read_toml_file(
    toml_path: Path,
    file_desc: str,
    schema_type: str,
) -> dict:
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
