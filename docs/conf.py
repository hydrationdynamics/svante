"""Sphinx configuration."""


project = "Svante"
author = "Joel Berendzen"
copyright = "2024 Joel Berendzen"  # noqa: A001
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser"
]
autodoc_typehints = "description"
html_theme = "furo"
