# -*- coding: utf-8 -*-
"""Tests for data ingestion."""
# standard library imports
import sys
from pathlib import Path

# third-party imports
import pytest
import sh

# module imports
from . import COMBINE_OUTPUTS
from . import help_check
from . import print_docstring
from . import TOML_FILE

# global constants
svante = sh.Command("svante")
SUBCOMMAND = "plot"
OUTPUTS = ["arrhenius_plot.png"]


def test_subcommand_help():
    """Test subcommand help message."""
    help_check(SUBCOMMAND)


@print_docstring()
def test_combine(datadir_mgr):
    """Test combining rate data."""
    with datadir_mgr.in_tmp_dir(
        inpathlist=COMBINE_OUTPUTS + [TOML_FILE],
        save_outputs=True,
        outscope="global",
        excludepaths=["logs/"],
    ):
        args = [SUBCOMMAND, TOML_FILE]
        try:
            svante(
                args,
                _out=sys.stderr,
            )
        except sh.ErrorReturnCode as errors:
            print(errors)
            pytest.fail(f' {SUBCOMMAND} failed')
        for filestring in OUTPUTS:
            assert Path(filestring).exists()
