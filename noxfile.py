"""Nox sessions."""
import os
import random
import shutil
from pathlib import Path

import nox


os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})

package = "flardl"
python_versions = ["3.12", "3.11", "3.10", "3.9"]
primary_python_version = "3.12"
nox.needs_version = ">= 2021.10.1"
nox.options.sessions = (
    "pre-commit",
    "safety",
    "mypy",
    "tests",
    "typeguard",
    "xdoctest",
    "docs-build",
)
nox.options.reuse_existing_virtualenvs = True

@nox.session(name="pre-commit", python=primary_python_version)
def precommit(session: nox.Session) -> None:
    """Lint using pre-commit."""
    args = session.posargs or [
        "run",
        "--all-files",
        "--hook-stage=manual",
        "--show-diff-on-failure",
    ]
    session.run_always("pdm", "install", "-G", "pre-commit", external=True)
    session.run("pre-commit", *args)


@nox.session(python=primary_python_version)
def safety(session: nox.Session) -> None:
    """Scan dependencies for insecure packages."""
    session.run_always("pdm", "install", "-G", "safety", external=True)
    session.run_always("pdm", "export", "-o", "requirements.txt",
                       "--without-hashes", external=True)
    session.run("safety", "check", "--full-report")
    Path("requirements.txt").unlink()


@nox.session(python=primary_python_version)
def mypy(session: nox.Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or ["src"]
    session.run_always("pdm", "install", "-G", "tests", external=True)
    session.run("mypy", "--check-untyped-defs", *args)


@nox.session(python=python_versions)
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    session.run_always("pdm", "install", "-G", "tests", external=True)
    try:
        session.run(
            "coverage",
            "run",
            "-m",
            "pytest",
            *session.posargs,
        )
        cov_path = Path(".coverage")
        if cov_path.exists():
            cov_path.rename(f".coverage.{random.randrange(100000)}")  # noqa: S311
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@nox.session(python=primary_python_version)
def coverage(session: nox.Session) -> None:
    """Produce the coverage report."""
    args = session.posargs or ["report"]
    session.run_always("pdm", "install", "-G", "coverage", external=True)
    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")
    session.run("coverage", *args)


@nox.session(python=primary_python_version)
def typeguard(session: nox.Session) -> None:
    """Runtime type checking using Typeguard."""
    session.run_always(
        "pdm", "install", "-G", "tests", external=True
    )
    session.run("pytest", f"--typeguard-packages={package}", *session.posargs)


@nox.session(python=primary_python_version)
def xdoctest(session: nox.Session) -> None:
    """Run examples with xdoctest."""
    if session.posargs:
        args = [package, *session.posargs]
    else:
        args = [f"--modname={package}", "--command=all"]
        if "FORCE_COLOR" in os.environ:
            args.append("--colored=1")
    session.run_always("pdm", "install", "-G", "xdoctest", external=True)
    session.run("python", "-m", "xdoctest", *args)


@nox.session(name="docs-build", python=primary_python_version)
def docs_build(session: nox.Session) -> None:
    """Build the documentation."""
    args = session.posargs or ["docs", "docs/_build"]
    if not session.posargs and "FORCE_COLOR" in os.environ:
        args.insert(0, "--color")
    session.run_always("pdm", "install", "-G", "docs", external=True)
    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    session.run("sphinx-build", *args)


@nox.session(python=primary_python_version)
def docs(session: nox.Session) -> None:
    """Build and serve the documentation with live reloading on file changes."""
    args = session.posargs or ["--open-browser", "docs", "docs/_build"]
    session.run_always("pdm", "install", "-G", "docs", external=True)
    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    session.run("sphinx-autobuild", *args)
