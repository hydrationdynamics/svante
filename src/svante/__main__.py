# -*- coding: utf-8 -*-
"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Svante -- configurable Arrhenius plots and fits."""


if __name__ == "__main__":
    main(prog_name="svante")  # pragma: no cover
