# -*- coding: utf-8 -*-

# standard library imports
from pathlib import Path

# third-party imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pydove as dv
import sys
from contextlib import nullcontext
from math import sqrt
from sciplotlib import style as spstyle
from scipy.constants import gas_constant

# module imports
from .stat_dict import StatDict

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

# GLOBAL_STATS = StatDict()
# GLOBAL_STATS["Δ H"] = 4223  # , 20.02, "kJ/mol", desc='Activation Enthalpy',)
# print(GLOBAL_STATS)
# b = Stat(23.37, units="K", sig_digits=3, desc="Temperature")
# print(b)
# c = Stat("This is not a quantity [or is it?]", desc="random description")
# print(c)
# d = Stat(True, desc="test of boolean")
# print(d)
#
# sys.exit(1)


def inverse_kilokelvin_to_c(kK: float) -> float:
    """Convert inverse kiloKelvin to degrees Celsius."""
    return (1000.0 / (kK + EPSILON)) - ZERO_C


def c_to_inverse_kilokelvin(c: float) -> float:
    """Convert degrees celsius to inverse kiloKelvin."""
    return 1000.0 / (c + ZERO_C)


def plot(
    config_file: Path,
    nature: bool,
    verbose: bool = False,
) -> None:
    """Plot dielectric relaxation"""
    df = pd.read_csv(datafile, sep="\t", index_col=0)
    for ratio in conf['combined']['ratio']:
        num = ratio['numerator']
        denom = ratio['denominator']
        ratio_name = ratio['name']
        uratio_name = '+' + ratio_name
        T_uncert_ratio_col = f'±T.{ratio_name}'
        T_uncert_num_col = f'±T.{num}'
        T_uncert_denom_col = f'±T.{denom}'
        unum = unumpy.uarray(combined[num], combined['±'+num])
        udenom= unumpy.uarray(combined[denom], combined['±'+denom])
        uratio = unum / udenom
        print(f'uratio={uratio}')
        combined[ratio_name] = unumpy.to_nominal_values(uratio)
        combined[uratio_name] = unumpy.to_std_devs(uratio)
        combined[T_uncert_ratio_col] = combined[[T_uncert_num_col,
                                        T_uncert_denom_col]].std(axis=1)
        output_cols.append(ratio_name)
        output_cols.append(uratio_name)
        output_cols.append(T_uncert_ratio_col)
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
        delta_H = {}
        delta_H_std = {}
        delta_H_string = {}
        log_preexp = {}
        log_preexp_std = {}
        log_preexp_string = {}
        v_offset = 0
        for i in ("H2O", "D2O"):
            log_preexp[i] = res[i].params[0]
            log_preexp_std[i] = res[i].bse[0]
            delta_H[i] = -1.0 * res[i].params[1] * R * 1000.0 * LOG10_TO_E
            delta_H_std[i] = res[i].bse[1] * R * 1000.0 * LOG10_TO_E
            if verbose:
                print(res[i].summary())
            labelidx = labels.index(i)
            labels[labelidx] = (
                rf"$\rm {i[0]}_2O$"
                #    + rf":\rm \Delta H={delta_H[i]:.0f}$ kJ/mol, "
                #    + rf"$\log A={log_preexp[i]:.0f}$ "
            )
            GLOBAL_STATS[f"ΔH_{i}"] = delta_H[i]  #:.0f}
            # GLOBAL_STATS P{delta_H_std[i]:.0f} kJ/mol"
            log_preexp_string[
                i
            ] = f"log A({i}): {log_preexp[i]:0.0f}±{log_preexp_std[i]:0.0f}/s"
            print(delta_H_string[i])
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
