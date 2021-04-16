# -*- coding: utf-8 -*-

# standard library imports
import sys
from pathlib import Path

# third-party imports
import pandas as pd
from loguru import logger
from uncertainties import unumpy

# module imports
from .common import read_toml_file

def combine(conf_file_path: Path,
            verbose=False) -> None:
    """Combine rate info from multiple files."""
    conf = read_toml_file(conf_file_path, 'configuration file')
    if 'inputs' not in conf:
        logger.error('"inputs" not found in configuration file')
        sys.exit(1)
    inputs = conf['inputs']
    outputs = conf['combined']['rates']
    logger.info(f'reading {len(inputs)} sets of {conf["combined"]["title"]} data:')
    frames = []
    output_cols = ['±T']
    delta_T_cols = []
    for i, dataset in enumerate(inputs):
        uri = dataset['uri']
        df = pd.read_csv(uri, sep="\t", index_col=dataset['T']['col'])
        df.index.name = 'T'
        rate_col_in = dataset['rate']['name']
        rate_col_out = outputs[i]['name']
        uncertainty_col_in = dataset['rate']['uncertainties']
        uncertainty_col_out = '±' + rate_col_out
        output_cols += [rate_col_out, uncertainty_col_out]
        T_uncertainty_col = f'±T.{rate_col_out}'
        delta_T_cols.append(T_uncertainty_col)
        if 'uncertainty' in dataset['T']:
            df[T_uncertainty_col] = dataset['T']['uncertainty']
        elif 'uncertainties' in dataset['T']:
            df[T_uncertainty_col] = df[dataset['T']['uncertainties']]
        else:
            logger.error('Neither T uncertainty value nor uncertainty column found')
            sys.exit(1)
        n_points = len(df)
        t_min = df.index.min()
        t_max = df.index.max()

        df.rename(columns={rate_col_in:rate_col_out,
                           uncertainty_col_in: uncertainty_col_out
                           }, inplace=True)
        df = df[[T_uncertainty_col, rate_col_out, uncertainty_col_out]]
        logger.info(f'   {uri}: {n_points} points from {t_min} to {t_max} K')
        if verbose:
            print(rf'   {outputs[i]["title"]}')
            print(df)
        frames.append(df)
    combined = pd.concat(frames, axis=1)
    combined["±T"] = combined[delta_T_cols].max(axis=1)
    combined = combined[output_cols]
    output_file =conf['combined']['filename']
    if verbose:
        print(combined)
    logger.info(f"{len(combined)} points written to {output_file}")
    combined.to_csv(output_file, sep="\t", float_format="%.4f")
