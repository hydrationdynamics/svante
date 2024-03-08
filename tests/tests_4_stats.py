"""Tests for data ingestion."""
import pytest
import sh

from . import STATS_FILE
from . import help_check
from . import print_docstring


# global constants
svante = sh.Command("svante")
SUBCOMMAND = "stats"
DELTA_H_STAT = "ΔH(k_D2O)"
DELTA_H_VAL = "77±2 kJ/mol\n"
STAT_TABLE = """
============  ========  =======  =====================  =====
Name          Value     Units    Description              Run
============  ========  =======  =====================  =====
n_points      15                                            1
T_min         190       K        [min temperature]          1
T_max         260       K        [max temperature]          1
ΔH(k_H2O)     46±1      kJ/mol   [activation enthalpy]      2
log A(k_H2O)  15.2±0.3  1/s      [Pre-exponential]          2
ΔH(k_D2O)     77±2      kJ/mol   [activation enthalpy]      2
log A(k_D2O)  22.5±0.4  1/s      [Pre-exponential]          2
============  ========  =======  =====================  =====
\n"""


def test_subcommand_help():
    """Test subcommand help message."""
    help_check(SUBCOMMAND)


@print_docstring()
def test_all_stats(datadir_mgr):
    """Test global stats production."""
    with datadir_mgr.in_tmp_dir(inpathlist=[STATS_FILE]):
        args = [SUBCOMMAND]
        try:
            output = svante(args)
        except sh.ErrorReturnCode as errors:
            print(errors)
            pytest.fail(f" {SUBCOMMAND} failed")
        assert STAT_TABLE in output


@print_docstring()
def test_one_stat(datadir_mgr):
    """Test specific stat production."""
    with datadir_mgr.in_tmp_dir(inpathlist=[STATS_FILE]):
        args = [SUBCOMMAND, f"--name={DELTA_H_STAT}"]
        try:
            output = svante(args)
        except sh.ErrorReturnCode as errors:
            print(errors)
            pytest.fail(f" {SUBCOMMAND} failed")
        assert output == DELTA_H_VAL
