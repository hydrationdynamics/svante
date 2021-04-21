# -*- coding: utf-8 -*-
# standard-library imports
import json
from numbers import Number
from pathlib import Path
from typing import Any

import attr
from pint import UnitRegistry  # type: ignore
from uncertainties import ufloat  # type: ignore
# third-party imports

# global constants
UREG = UnitRegistry()


class StatDict(object):
    """Holds a class of Stat objects that can be serialized to JSON."""

    class Stat(object):
        """Float with optional uncertainty, significant digits, units, and description."""

        def __init__(
            self,
            value: Any,
            uncert: float = None,
            units: str = None,
            sig_digits: int = None,
            desc: str = None,
            is_count: bool = False,
        ):
            """Initialize the value."""
            self.type = value.__class__.__name__
            if self.type not in ("int", "float", "str", "bool"):
                raise ValueError(f"unsupported value type {self.type}")
            self.is_number = isinstance(value, Number)
            self.has_units = units is not None
            if self.is_number:
                if uncert is not None:
                    self.value = ufloat(value, uncert)
                else:
                    self.value = value
                if self.has_units:
                    self.value *= UREG(units)
                if sig_digits is not None:
                    self.sig_digits = sig_digits
            else:
                self.value = value
            if desc is not None:
                self.desc = desc

        def __str__(self):
            if self.is_number:
                if self.has_units:
                    fmt_str = "{0:~"  # use abbreviated units
                else:
                    fmt_str = "{0:"
                if hasattr(self, "sig_digits"):
                    fmt_str += f".{self.sig_digits:d}g"
                fmt_str += "}"
                val_str = fmt_str.format(self.value)
            else:
                val_str = str(self.value)
            if hasattr(self, "desc"):
                metadata_str = f" [{self.type},{self.desc}]"
            else:
                metadata_str = f" [{self.type}]"
            return val_str + metadata_str

    def __init__(self, save_dir="."):
        self.stat_dict = {}
        self.save_path = Path(save_dir) / (__name__ + "_stats.json")

    def __setitem__(
        self,
        key,
        value,
        uncert=None,
        units=None,
        sig_digits=None,
        is_count=False,
    ):
        self.stat_dict[key] = self.Stat(
            value,
            uncert=uncert,
            units=units,
            sig_digits=sig_digits,
            is_count=is_count,
        )

    def __getitem__(self, key):
        return self.stat_dict[key]

    def __delitem__(self, key):
        del self.stat_dict[key]

    def __contains__(self, key):
        return key in self.stat_dict

    def __str__(self):
        ret_str = ""
        for key, value in self.stat_dict.items():
            ret_str += f"{key}: {value}"
        return ret_str

    def save(self) -> None:
        stringified = {}
        for key, value in self.stat_dict.items():
            stringified[key] = str(value)
        with self.save_path.open() as fh:
            json.dump(stringified, fh, indent=1)
