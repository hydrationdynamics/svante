"""Sphinx configuration."""
from datetime import datetime


project = "Svante"
author = "Joel Berendzen"
copyright = f"{datetime.now().year}, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme",
    "sphinx_click",
]
autodoc_typehints = "description"
html_theme = "sphinx_rtd_theme"
