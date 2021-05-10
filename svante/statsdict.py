# -*- coding: utf-8 -*-
"""Saveable dictionary of statistics with uncertainties and units."""
# standard-library imports
from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from functools import partial
from functools import wraps
from math import sqrt
from pathlib import Path
from typing import Any
from typing import Callable
from typing import cast
from typing import Dict
from typing import List
from typing import Optional
from typing import SupportsFloat
from typing import TypeVar
from typing import Union

import attr
import loguru
import typer
from pint import UnitRegistry  # type: ignore
from tabulate import tabulate
from uncertainties import ufloat  # type: ignore

F = TypeVar("F", bound=Callable[..., Any])
NUMBER_CASTS = {"int": int, "float": float}
VALUE_TYPES = Union[int, SupportsFloat]
# valid table formats from tabular
TABLE_FORMATS = (
    "plain",
    "simple",
    "github",
    "grid",
    "fancy_grid",
    "pipe",
    "orgtbl",
    "jira",
    "presto",
    "pretty",
    "psql",
    "rst",
    "mediawiki",
    "moinmoin",
    "youtrack",
    "html",
    "unsafehtml",
    "latex",
    "latex_raw",
    "latex_booktabs",
    "latex_longtable",
    "textile",
    "tsv",
)
DEFAULT_TABLE_FORMAT = "rst"
UREG = UnitRegistry()
TIMESTAMP: float = time.time()
ALL = ["Stat", "StatDict"]
NAME_OPTION = typer.Option("", help="Show only named stat.")


class Stat(object):
    """Stat with optional metadata."""

    def __init__(
        self,
        val: VALUE_TYPES,
        val_type: Optional[str] = None,
        uncert: Optional[float] = None,
        units: Optional[str] = None,
        desc: Optional[str] = None,
        run_no: int = -1,
        is_count: bool = False,
    ) -> None:
        """Initialize the value with metadata."""
        self.val = val
        self.run_no = run_no
        if units is not None:
            self.units = units
        if desc is not None:
            self.desc = desc
        value_type_name = val.__class__.__name__
        if val_type is None:
            self.val_type = value_type_name
        else:
            self.val_type = val_type
        if self.val_type not in NUMBER_CASTS:
            raise ValueError(f'unsupported type for stat "{val_type}"')
        if self.val_type != value_type_name:
            self.val = NUMBER_CASTS[self.val_type](val)
        if is_count:
            self.uncert = sqrt(self.val)
        elif uncert is not None:
            self.uncert = uncert

    def __str__(self) -> str:
        """Return stat as a formatted string."""
        val_str = self.format_value()
        unit_str = self.format_units()
        return f"{val_str} {unit_str}"

    def to_dict(self) -> Dict[str, Any]:
        """Return attributes needed to be saved."""
        return self.__dict__.copy()

    def format_units(self) -> str:
        """Format stat units."""
        if not hasattr(self, "units"):
            return ""
        else:
            units = UREG(self.units)
            return f"{units.units:~P}"

    def format_value(self) -> str:
        """Format value with optional uncertainty."""
        if not hasattr(self, "uncert"):
            return f"{self.val:g}"
        else:
            uval = ufloat(self.val, self.uncert)
            return f"{uval:.1uP}"

    def format_desc(self) -> str:
        """Format the optional description."""
        if not hasattr(self, "desc"):
            return ""
        else:
            return f"[{self.desc}]"


@attr.s(auto_attribs=True)
class _RunDict(Dict[str, Any]):
    """Holder of run-related items."""

    run_no: int = 1
    start_time: float = TIMESTAMP
    command: List[str] = sys.argv[1:]
    subtitle: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Return attributes as a dictionary."""
        return self.__dict__.copy()


class StatsDict(object):
    """Holds a class of Stat objects that can be serialized to JSON."""

    def __init__(  # noqa: C901
        self,
        logger: Optional[loguru.Logger] = None,
        module_name: Optional[str] = None,
        save_dir: Optional[str] = None,
        title: Optional[str] = None,
        table_fmt: Optional[str] = None,
        app: Optional[typer.Typer] = None,
        verbose: bool = False,
        log_stats: bool = False,
        load_existing: bool = True,
        show_runs: bool = True,
    ) -> None:
        """Create saveable dictionary of stat values."""
        self._app: Optional[typer.Typer] = app
        self._stat_dict: Dict[str, Stat] = {}
        self._unit_defs: List[str] = []
        self._run_list: List[_RunDict] = []
        self._verbose = verbose
        self._log_stats = log_stats
        self._show_runs = show_runs
        self._show_run_no = 0
        self._table_format = DEFAULT_TABLE_FORMAT
        self.run_no = 1
        self._metadata_handlers: Dict[str, Any] = {
            "_run_list": self._load_run_list,
            "_title": self._load_title,
            "_unit_defs": self.define_units,
        }
        if (defaulted_module_name := module_name) is None:
            if __name__ == "__main__":
                defaulted_module_name = "global"
            else:
                defaulted_module_name = __name__.split(".")[0]
        if logger is None:
            self._logger = loguru.logger
        else:
            self._logger = logger
        if title is None:
            self._title = f"Stats from {defaulted_module_name}"
        if (defaulted_save_dir := save_dir) is None:
            defaulted_save_dir = "."
        self._save_path = (
            Path(defaulted_save_dir) / f"{defaulted_module_name}_stats.json"
        ).resolve()
        self.set_table_format(table_fmt)
        append_run = True
        if load_existing:
            try:
                self.load()
            except FileNotFoundError:
                pass
            if len(self._run_list) > 0:
                run_dict = self._run_list[-1]
                maxrun_no = run_dict.run_no
                max_start = run_dict.start_time
                if max_start == TIMESTAMP:
                    append_run = False
                    self.run_no = maxrun_no
                else:
                    self.run_no = maxrun_no + 1
        self._run_dict = _RunDict(self.run_no)
        if append_run:
            self._run_list.append(self._run_dict)
        self._logger.debug(f'Run {self.run_no} stats in "{self._save_path}"')
        if self._app is not None:

            @self._app.command()
            def stats(name: str = NAME_OPTION) -> None:
                """Print stats."""
                if name == "":
                    print(self)
                else:
                    if name not in self._stat_dict:
                        self._logger.error(f'Stat "{name}" not found')
                        print("Known stats are:")
                        for stat_name in self._stat_dict:
                            print(f'   "{stat_name}"')
                        sys.exit(1)
                    else:
                        print(self._stat_dict[name])

    def __setitem__(self, key: str, value: Stat) -> None:
        """Add stat to dictionary."""
        if key.startswith("_"):
            raise KeyError("StatDict key may not start with underscore.")
        if key in self._stat_dict:
            old_run = self._stat_dict[key].run_no
            self._logger.debug(f'Redefining stat "{key}" from run {old_run}')
        value.run_no = self.run_no
        self._stat_dict[key] = value
        if self._log_stats:
            if (desc_str := value.format_desc()) != "":
                desc_str = " " + desc_str
            self._logger.info(f"Stat {key}{desc_str}:\t{value}")

    def __str__(self) -> str:
        """Format stats dictionary."""
        ret_str = ""
        show_runs = self._show_runs
        if self._verbose:
            ret_str += f'Stats file: "{self._save_path}"\n'
        if self._show_run_no == 0:
            run_no_str = ""
            show_run_no = None
        else:
            if self._show_run_no < 0:
                show_run_no = self._show_run_no + self.run_no + 1
            else:
                show_run_no = self._show_run_no
            run_no_str = f" run {show_run_no}"
            show_runs = False
        ret_str += f"{self._title}{run_no_str}:\n"
        stat_table = []
        for key, stat in self._stat_dict.items():
            if show_run_no is not None and stat.run_no != show_run_no:
                continue
            stat_row = [
                key,
                stat.format_value(),
                stat.format_units(),
                stat.format_desc(),
            ]
            if show_runs:
                stat_row.append(f"{stat.run_no:d}")
            stat_table.append(stat_row)
        headers = ["Name", "Value", "Units", "Description"]
        if show_runs:
            headers += ["Run"]
        stat_table_str = tabulate(
            stat_table, tablefmt=self._table_format, headers=headers
        )
        ret_str += stat_table_str
        ret_str += "\n"
        if show_runs:
            ret_str += "\nTable of runs:\n"
            run_table = []
            for run_dict in self._run_list:
                run_no = run_dict.run_no
                subtitle = run_dict.subtitle
                command = '"' + " ".join(run_dict.command) + '"'
                time_str = datetime.fromtimestamp(
                    run_dict.start_time
                ).strftime("%x %X")
                run_table.append([run_no, subtitle, command, time_str])
            run_table_str = tabulate(
                run_table,
                tablefmt="plain",
                headers=["Run", "Subtitle", "Command", "Date&Time"],
            )
            ret_str += run_table_str
            ret_str += "\n"
        return ret_str

    def set_table_format(self, table_fmt: Optional[str]) -> None:
        """Set the format of the output table."""
        if table_fmt is None:
            self._table_format = DEFAULT_TABLE_FORMAT
        elif table_fmt in TABLE_FORMATS:
            self._table_format = table_fmt
        else:
            self._logger.error(f'Error--unknown table format "{table_fmt}"')
            self._logger.error(f"valid formats are {TABLE_FORMATS}")
            sys.exit(1)

    def auto_save_and_report(
        self,
        user_func: Optional[F] = None,
        subtitle: Optional[str] = None,
        print_run_stats: bool = True,
    ) -> F:
        """Decorator to save and optionally print run stats upon exit."""
        if user_func is None:
            func_name = ""
            return cast(
                F,
                partial(
                    self.auto_save_and_report,
                    subtitle=subtitle,
                    print_run_stats=print_run_stats,
                ),
            )
        else:
            func_name = user_func.__name__
            func = user_func

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            self.start_run(subtitle=func_name)
            returnobj = func(*args, **kwargs)
            self.save()
            if print_run_stats:
                self.configure_report(show_run_no=-1)
                print(self)
            return returnobj

        return cast(F, wrapper)

    def start_run(self, subtitle: Optional[str] = None) -> None:
        """Start a run, including run parameters."""
        if subtitle is None:
            self._run_dict.subtitle = f"Run of {__name__}"
        else:
            self._run_dict.subtitle = subtitle

    def define_units(self, unit_defs: List[str]) -> None:
        """Define new units in unit registry."""
        global UREG
        for definition in unit_defs:
            if definition not in self._unit_defs:
                self._unit_defs.append(definition)
            base_unit = definition.split()[0]
            if base_unit not in UREG:
                UREG.define(definition)

    def configure_report(
        self,
        show_runs: Optional[bool] = None,
        show_run_no: Optional[int] = None,
        verbose: Optional[bool] = None,
    ) -> None:
        """Configure report formatting."""
        if show_runs is not None:
            self._show_runs = show_runs
        if show_run_no is not None:
            self._show_run_no = show_run_no
            self._show_runs = False
        if verbose is not None:
            self._verbose = verbose

    def save(self) -> None:
        """Save stats and run info as a JSON file."""
        outdict = {
            "_unit_defs": self._unit_defs,
            "_run_list": [r.to_dict() for r in self._run_list],
            "_title": self._title,
        }
        for key, stat_obj in self._stat_dict.items():
            outdict[key] = stat_obj.to_dict()
        with self._save_path.open("w") as fh:
            json.dump(outdict, fh, indent=1)

    def _load_run_list(self, run_list: List[Dict[str, Any]]) -> None:
        """Load a run_list from a list of saved RunDicts."""
        run_nos = [r["run_no"] for r in self._run_list]
        for r in run_list:
            if r["run_no"] not in run_nos:
                self._run_list.append(_RunDict(**r))

    def _load_title(self, title: str) -> None:
        """Load a title."""
        self._title = title

    def load(self) -> None:
        """Load stats and list of run info from JSON file."""
        if not self._save_path.exists():
            raise FileNotFoundError
        with self._save_path.open() as fh:
            try:
                load_dict = json.load(fh)
            except json.JSONDecodeError as e:
                self._logger.error(
                    f'Error--malformed JSON in file "{self._save_path}"'
                )
                self._logger.error(e)
                sys.exit(1)
            previously_defined = 0
            for key in load_dict:
                if key in self._metadata_handlers:
                    self._metadata_handlers[key](load_dict[key])
                else:
                    if key in self._stat_dict:
                        previously_defined += 1
                    self._stat_dict[key] = Stat(**load_dict[key])
            if self._verbose:
                self._logger.debug(
                    f"{previously_defined} stats" + " were previously defined"
                )
            return


def _test() -> None:
    """Test command."""
    new_units = [
        "basepairs = [dimensionless] = bp",
        "kilobasepairs = 1000 * basepairs = kbp",
    ]

    def stderr_format_func(record: loguru.Record) -> str:
        """Do level-sensitive formatting."""
        if record["level"].no < 25:
            return "<level>{message}</level>\n"
        return "<level>{level}</level>: <level>{message}</level>\n"

    loguru.logger.remove()
    loguru.logger.add(sys.stderr, level="DEBUG", format=stderr_format_func)
    stats = StatsDict(logger=loguru.logger)

    @stats.auto_save_and_report
    def define_some_stats() -> None:
        """Stat definitions in a function."""
        run_no = stats.run_no
        stats.define_units(new_units)
        stats["k"] = Stat(23)
        if run_no % 2:
            stats["ΔH"] = Stat(
                40.0, units="kJ/mol", desc="activation enthalpy"
            )
            stats["ΔS"] = Stat(
                840.0, uncert=3.1, units="kJ/mol", desc="activation entropy"
            )
        if run_no % 3:
            stats["n_sigs"] = Stat(
                23400,
                units="basepairs",
                is_count=True,
                desc="bases in signatures",
            )
        print(stats)

    define_some_stats()
    loguru.logger.info("Test done")


if __name__ == "__main__":
    _test()
