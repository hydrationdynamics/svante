# -*- coding: utf-8 -*-
"""Make Arrhenius plot with fits."""
# standard library imports
from pathlib import Path

import matplotlib.pyplot as plt  # type: ignore
import numpy as np
import pandas as pd
import pydove as dv  # type: ignore
import typer
from loguru import logger
from scipy.constants import gas_constant  # type: ignore

from .common import APP
from .common import read_conf_file
from .common import STATE
from .common import STATS
from .statsdict import Stat

# from uncertainties import unumpy  # type: ignore


# global constants
EPSILON = 0.001  # close to zero for T inversion
ZERO_C = 273.15  # in K
R = gas_constant / 1000.0  # kJ/mol⋅K
LOG10_TO_E = 2.303
INVERSE_T_COL = "1000/T"
SHOW_OPTION = typer.Option(False, help="Show plot.")
PLOT_STYLE = "default"


def inverse_kilokelvin_to_c(inverse_kilo_kelvins: float) -> float:
    """Convert inverse kiloKelvin to degrees Celsius."""
    return (1000.0 / (inverse_kilo_kelvins + EPSILON)) - ZERO_C


def c_to_inverse_kilokelvin(c: float) -> float:
    """Convert degrees celsius to inverse kiloKelvin."""
    return 1000.0 / (c + ZERO_C)


@APP.command()
@STATS.auto_save_and_report
def plot(
    toml_file: Path,
    show: bool = SHOW_OPTION,
) -> None:
    """Arrhenius plot with fits."""
    conf = read_conf_file(toml_file, "configuration file", "plot")
    combined = conf["combined"]
    plot_params = conf["plot"]
    df = pd.read_csv(combined["filename"], sep="\t", index_col=0)
    df[INVERSE_T_COL] = 1000.0 / df.index

    # make fits and plots
    with plt.style.context(PLOT_STYLE):
        unused_fig, ax = plt.subplots()
        res = {}
        for rate_col_params in combined["rates"]:
            col = rate_col_params["name"]
            res[col] = dv.regplot(
                df[INVERSE_T_COL],
                np.log10(df[col]),
                ax=ax,
                label=rate_col_params["label"],
            )
        handles, labels = ax.get_legend_handles_labels()
        ax.set_xlabel(r"$1/T$, kK$^{-1}$")
        ax.set_ylabel(
            r"$\log ($" + rf"{plot_params['y_label']}" + r"/s$^{-1})$"
        )
        ax.legend(handles, labels)
        secax = ax.secondary_xaxis(
            "top", functions=(inverse_kilokelvin_to_c, c_to_inverse_kilokelvin)
        )
        secax.set_xlabel(r"$T, ^{\circ}$C")
        # Now calculate parameters from the fits
        for rate_col in combined["rates"]:
            col = rate_col["name"]
            log_preexp = float(res[col].params[0])
            log_preexp_std = float(res[col].bse[0])
            delta_h = float(res[col].params[1] * R * -1000.0 * LOG10_TO_E)
            delta_h_std = float(res[col].bse[1] * R * 1000.0 * LOG10_TO_E)
            STATS[f"ΔH({col})"] = Stat(
                delta_h,
                uncert=delta_h_std,
                units="kJ/mol",
                desc="activation enthalpy",
            )
            STATS[f"log A({col})"] = Stat(
                log_preexp,
                uncert=log_preexp_std,
                units="1/s",
                desc="Pre-exponential",
            )
            if STATE["verbose"]:
                print(res[col].summary())
            label = (
                rf"$\rm \Delta H={delta_h:.0f}$ kJ/mol, "
                + r"$A=10^{"
                + f"{log_preexp:.0f}"
                + r"}s^{-1}$ "
            )
            ax.annotate(
                label,
                xy=rate_col["line_label_loc"],
                rotation=np.degrees(np.arctan2(res[col].params[1], 1.0)),
                rotation_mode="anchor",
                transform_rotates_text=True,
            )
        # Do ratio plots
        if len(plot_params["ratios"]) > 0:
            ax2 = ax.twinx()
            for ratio in plot_params["ratios"]:
                num_col = ratio["numerator"]
                denom_col = ratio["denominator"]
                ratio_col = ratio["name"]
                df[ratio_col] = df[num_col] / df[denom_col]
                # uratio_name = "+" + ratio_name
                # t_uncert_ratio_col = f"±T.{ratio_name}"
                # t_uncert_num_col = f"±T.{num}"
                # t_uncert_denom_col = f"±T.{denom}"
                # unum = unumpy.uarray(df[num], df["±" + num])
                # udenom = unumpy.uarray(df[denom], df["±" + denom])
                # uratio = unum / udenom
                # print(f"uratio={uratio}")
                ratio_handle = ax2.plot(
                    df[INVERSE_T_COL], df[ratio_col], color="green"
                )
                # df[ratio_name] = unumpy.to_nominal_values(uratio)
                # df[uratio_name] = unumpy.to_std_devs(uratio)
                # df[t_uncert_ratio_col] = df[
                #    [t_uncert_num_col, t_uncert_denom_col]
                # ].std(axis=1)
            # STATS["KIE_ratio_min"] = df[RATIO_COL].min()
            # STATS["KIE_ratio_max"] = df[RATIO_COL].max()
            ax2.set_ylabel("KIE Ratio")
            handles += ratio_handle
            labels.append("Ratio")
        ax.legend(handles, labels)
        sv_params = plot_params["savefig"]
        fig_format = sv_params["format"]
        fname = f'{sv_params["filename"]}.{fig_format}'
        logger.debug(f'saving {fig_format} figure to "{fname}"')
        plt.savefig(
            fname,
            dpi=sv_params["dpi"],
            facecolor=sv_params["facecolor"],
            edgecolor=sv_params["edgecolor"],
            format=fig_format,
            transparent=sv_params["transparent"],
            pad_inches=sv_params["pad_inches"],
        )
        if show:
            plt.show()
