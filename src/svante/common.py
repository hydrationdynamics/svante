# -*- coding: utf-8 -*-
"""Global constants and other objects in common."""
# standard library imports
import sys
from pathlib import Path

# third-party imports
import toml
from loguru import logger

__version__ = "0.0.0"

def read_toml_file(toml_path: Path,
                   file_desc: str,
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
        logger.error(f'File {toml_path} is not valid TOML:')
        logger.error(e)
        sys.exit(1)
    return toml_dict
