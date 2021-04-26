# -*- coding: utf-8 -*-
"""Tests for data ingestion."""
# standard library imports
import sys
from pathlib import Path

import pytest
import sh

from . import COMBINE_INPUTS
from . import COMBINE_OUTPUTS
from . import help_check
from . import print_docstring
from . import TOML_FILE
# third-party imports
# module imports

# global constants
svante = sh.Command("svante")
SUBCOMMAND = "combine"


def test_subcommand_help():
    """Test subcommand help message."""
    help_check(SUBCOMMAND)


@print_docstring()
def test_combine(datadir_mgr):
    """Test combining rate data."""
    with datadir_mgr.in_tmp_dir(
        inpathlist=COMBINE_INPUTS,
        save_outputs=True,
        outscope="global",
        excludepaths=["logs/"],
    ):
        args = ["--verbose", SUBCOMMAND, TOML_FILE]
        try:
            svante(
                args,
                _out=sys.stderr,
            )
        except sh.ErrorReturnCode as errors:
            print(errors)
            pytest.fail("combine failed")
        for filestring in COMBINE_OUTPUTS:
            assert Path(filestring).exists()
