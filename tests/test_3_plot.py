"""Tests for data ingestion."""
# standard library imports
import shutil
import sys
from pathlib import Path

import pytest
import sh

from . import COMBINE_OUTPUTS
from . import STATS_FILE
from . import TOML_FILE
from . import help_check
from . import print_docstring


# global constants
svante = sh.Command("svante")
SUBCOMMAND = "plot"
OUTPUTS = ["arrhenius_plot.png", "svante_stats.json"]


def test_subcommand_help():
    """Test subcommand help message."""
    help_check(SUBCOMMAND)


@print_docstring()
def test_combine(datadir_mgr):
    """Test Arrhenius plots and fits."""
    datadir_mgr.add_scope("outputs from combine", module="test_2_combine")
    with datadir_mgr.in_tmp_dir(
        inpathlist=[*COMBINE_OUTPUTS, TOML_FILE],
        save_outputs=True,
        outscope="global",
    ):
        # Copy stats file so it will get saved.
        stats_path = Path(STATS_FILE)
        input_stats_path = datadir_mgr[Path(stats_path)]
        shutil.copy2(input_stats_path, stats_path)
        args = [SUBCOMMAND, TOML_FILE]
        try:
            svante(
                args,
                _out=sys.stderr,
            )
        except sh.ErrorReturnCode as errors:
            print(errors)
            pytest.fail(f" {SUBCOMMAND} failed")
        for filestring in OUTPUTS:
            assert Path(filestring).exists()
