# -*- coding: utf-8 -*-
"""Combine multiple TSV files containing rates into one file."""
# standard library imports
import sys
from pathlib import Path

import pandas as pd
from loguru import logger

from .common import APP
from .common import read_conf_file
from .common import STATE
from .common import STATS
from .statsdict import Stat


@APP.command()
@STATS.auto_save_and_report
def combine(toml_file: Path) -> None:
    """Combine rate info from multiple files."""
    conf = read_conf_file(toml_file, "configuration file", "combine")
    inputs = conf["inputs"]
    outputs = conf["combined"]["rates"]
    logger.info(
        f'reading {len(inputs)} sets of {conf["combined"]["title"]} data:'
    )
    frames = []
    output_cols = ["±T"]
    delta_t_cols = []
    for i, dataset in enumerate(inputs):
        uri = dataset["uri"]
        df = pd.read_csv(uri, sep="\t", index_col=dataset["T"]["col"])
        df.index.name = "T"
        rate_col_in = dataset["rate"]["name"]
        rate_col_out = outputs[i]["name"]
        uncertainty_col_in = dataset["rate"]["uncertainties"]
        uncertainty_col_out = "±" + rate_col_out
        output_cols += [rate_col_out, uncertainty_col_out]
        t_uncertainty_col = f"±T.{rate_col_out}"
        delta_t_cols.append(t_uncertainty_col)
        if "uncertainty" in dataset["T"]:
            df[t_uncertainty_col] = dataset["T"]["uncertainty"]
        elif "uncertainties" in dataset["T"]:
            df[t_uncertainty_col] = df[dataset["T"]["uncertainties"]]
        else:
            logger.error(
                "Neither T uncertainty value nor uncertainty column found"
            )
            sys.exit(1)
        n_points = len(df)
        t_min = df.index.min()
        t_max = df.index.max()
        df.rename(
            columns={
                rate_col_in: rate_col_out,
                uncertainty_col_in: uncertainty_col_out,
            },
            inplace=True,
        )
        df = df[[t_uncertainty_col, rate_col_out, uncertainty_col_out]]
        logger.info(f"   {uri}: {n_points} points from {t_min} to {t_max} K")
        if STATE["verbose"]:
            print(rf'   {outputs[i]["label"]}')
            print(df)
        frames.append(df)
    combined = pd.concat(frames, axis=1)
    combined["±T"] = combined[delta_t_cols].max(axis=1)
    combined = combined[output_cols]
    t_min = float(combined.index.min())
    t_max = float(combined.index.max())
    n_points = len(combined)
    output_file = conf["combined"]["filename"]
    if STATE["verbose"]:
        print(combined)
    logger.info(f"{n_points} points from {t_min} to {t_max} K")
    STATS["n_points"] = Stat(n_points)
    STATS["T_min"] = Stat(t_min, desc="min temperature", units="K")
    STATS["T_max"] = Stat(t_max, desc="max temperature", units="K")
    logger.info(f"written to {output_file}")
    combined.to_csv(output_file, sep="\t", float_format="%.4f")
