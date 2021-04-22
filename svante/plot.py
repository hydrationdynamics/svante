# -*- coding: utf-8 -*-
"""Make Arrhenius plot with fits."""
# standard library imports
from contextlib import nullcontext
from math import sqrt
from pathlib import Path

import matplotlib.pyplot as plt  # type: ignore
import numpy as np
import pandas as pd
import pydove as dv  # type: ignore
import typer
from sciplotlib import style as spstyle  # type: ignore
from scipy.constants import gas_constant  # type: ignore
from uncertainties import unumpy  # type: ignore

from .common import APP
from .common import GLOBAL_STATS
from .common import read_toml_file
from .common import STATE
# third-party imports
# module imports

# global constants
EPSILON = 0.001  # close to zero for ratio
ZERO_C = 273.15  # in K
R = gas_constant / 1000.0  # kJ/mol⋅K
LOG10_TO_E = 2.303
SEMICLASSICAL = sqrt(2)  # H/D semiclassical shift
TEXT_OFFSET = -1
LABEL_LOCS = {  # line labels in units of 1000/T and log k
    "H2O": (
        4.3,
        5.3,
    ),
    "D2O": (
        3.9,
        6.1,
    ),
}
RATIO_COL = "k_{H_2O}/k_{D_2O}"
INVERSE_T_COL = "1000/T, K^{-1}"
H2O_RATE_COL = "k_{H_2O}, s^{-1}"
D2O_RATE_COL = "k_{D_2O}, s^{-1}"
COLORS = {"H2O": "blue", "D2O": "orange", "KIE": "green"}
NATURE_OPTION = typer.Option(False, help="Use Nature style"),

def inverse_kilokelvin_to_c(inverse_kilo_kelvins: float) -> float:
    """Convert inverse kiloKelvin to degrees Celsius."""
    return (1000.0 / (inverse_kilo_kelvins + EPSILON)) - ZERO_C


def c_to_inverse_kilokelvin(c: float) -> float:
    """Convert degrees celsius to inverse kiloKelvin."""
    return 1000.0 / (c + ZERO_C)


@APP.command()
def plot(
    toml_file: Path,
    nature: bool = NATURE_OPTION,
) -> None:
    """Arrhenius plot with fits."""
    conf = read_toml_file(toml_file, "configuration file", "plot")
    combined = conf["combined"]
    df = pd.read_csv(combined["filename"], sep="\t", index_col=0)
    for ratio in conf["plot"]["ratio"]:
        num = ratio["numerator"]
        denom = ratio["denominator"]
        ratio_name = ratio["name"]
        uratio_name = "+" + ratio_name
        t_uncert_ratio_col = f"±T.{ratio_name}"
        t_uncert_num_col = f"±T.{num}"
        t_uncert_denom_col = f"±T.{denom}"
        unum = unumpy.uarray(df[num], df["±" + num])
        udenom = unumpy.uarray(df[denom], df["±" + denom])
        uratio = unum / udenom
        print(f"uratio={uratio}")
        df[ratio_name] = unumpy.to_nominal_values(uratio)
        df[uratio_name] = unumpy.to_std_devs(uratio)
        df[t_uncert_ratio_col] = df[
            [t_uncert_num_col, t_uncert_denom_col]
        ].std(axis=1)
    GLOBAL_STATS["KIE_ratio_min"] = df[RATIO_COL].min()
    GLOBAL_STATS["KIE_ratio_max"] = df[RATIO_COL].max()
    # make fits and plots
    if nature:
        stylecontext = plt.style.context(spstyle.get_style("nature"))
    else:
        stylecontext = nullcontext()
    with stylecontext:
        fig, ax = plt.subplots()
        res = {
            "H2O": dv.regplot(
                df[INVERSE_T_COL],
                np.log10(df[H2O_RATE_COL]),
                ax=ax,
                label="H2O",
            ),
            "D2O": dv.regplot(
                df[INVERSE_T_COL],
                np.log10(df[D2O_RATE_COL]),
                ax=ax,
                label="D2O",
            ),
        }
        handles, labels = ax.get_legend_handles_labels()
        delta_h = {}
        delta_h_std = {}
        log_preexp = {}
        log_preexp_std = {}
        log_preexp_string = {}
        v_offset = 0
        for i in ("H2O", "D2O"):
            log_preexp[i] = res[i].params[0]
            log_preexp_std[i] = res[i].bse[0]
            delta_h[i] = -1.0 * res[i].params[1] * R * 1000.0 * LOG10_TO_E
            delta_h_std[i] = res[i].bse[1] * R * 1000.0 * LOG10_TO_E
            if STATE['verbose']:
                print(res[i].summary())
            labelidx = labels.index(i)
            labels[labelidx] = (
                rf"$\rm {i[0]}_2O$"
                #    + rf":\rm \Delta H={delta_h[i]:.0f}$ kJ/mol, "
                #    + rf"$\log A={log_preexp[i]:.0f}$ "
            )
            GLOBAL_STATS[f"ΔH_{i}"] = delta_h[i]  #:.0f}
            # GLOBAL_STATS P{delta_h_std[i]:.0f} kJ/mol"
            log_preexp_string[
                i
            ] = f"log A({i}): {log_preexp[i]:0.0f}±{log_preexp_std[i]:0.0f}/s"
            print(log_preexp_string[i])
            v_offset += 2 * TEXT_OFFSET
            slope = res[i].params[1]
            xylabel = LABEL_LOCS[i]
            p1 = ax.transData.transform_point(xylabel)
            p2 = ax.transData.transform_point(
                (
                    xylabel[0] + 1.0,
                    xylabel[1] + slope,
                )
            )
            angle = np.degrees(
                np.arctan2(
                    p2[1] - p1[1],
                    p2[0] - p1[0],
                )
            )
            ax.annotate(
                "helo", xy=LABEL_LOCS[i], rotation=angle, color=COLORS[i]
            )
            ax2 = ax.twinx()
            ratio_handle = ax2.plot(
                df[INVERSE_T_COL], df[RATIO_COL], color="green"
            )
        ax2.set_ylabel("KIE Ratio")
        handles += ratio_handle
        labels.append("Ratio")
        ax.legend(handles, labels)
        ax.set_xlabel(r"$1000/T$, K")
        ax.set_ylabel(r"$\log k_c, s^{-1} $")
        secax = ax.secondary_xaxis(
            "top", functions=(inverse_kilokelvin_to_c, c_to_inverse_kilokelvin)
        )
        secax.set_xlabel(r"$T, ^{\circ}$C")
        plt.show()
        print(GLOBAL_STATS)
