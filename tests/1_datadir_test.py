# -*- coding: utf-8 -*-
"""Tests for input table creation."""
# standard library imports
import shutil
from pathlib import Path

from . import print_docstring

# module imports


@print_docstring()
def test_clean_datadir(request):
    """Clean up datadir."""
    testdir = Path(request.fspath.dirpath())
    datadir = testdir / "data"
    if datadir.exists():
        shutil.rmtree(datadir)  # remove anything left in data directory


@print_docstring()
def test_setup_datadir(request, datadir_mgr, capsys):
    """Copy in and download static data."""
    testdir = Path(request.fspath.dirpath())
    datadir = testdir / "data"
    filesdir = testdir / "testdata"
    shutil.copytree(filesdir, datadir)
