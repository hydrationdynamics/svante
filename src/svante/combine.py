# -*- coding: utf-8 -*-

# third-party imports
import pandas as pd


def main(h2o_file: str, d2o_file: str, output_file: str):
    """Combine H2O and D2O information.

    Example:
        svante combine Mb_H20.tsv Mb_D20.tsv mb_dielectric_relaxation.tsv
    """
    d2o = pd.read_csv(d2o_file, sep="\t", index_col=0)
    d2o.rename(
        columns={
            "k_c, s^{-1}": "k_{D_2O}, s^{-1}",
            "amplitude": "amplitude_{D_2O}",
        },
        inplace=True,
    )
    h2o = pd.read_csv(h2o_file, sep="\t", index_col=0)
    h2o.rename(
        columns={
            "k_c, s^{-1}": "k_{H_2O}, s^{-1}",
            "amplitude": "amplitude_{H_2O}",
        },
        inplace=True,
    )
    combined = pd.concat([h2o, d2o], axis=1)
    combined["1000/T, K^{-1}"] = 1000.0 / combined.index
    combined["k_{H_2O}/k_{D_2O}"] = (
        combined["k_{H_2O}, s^{-1}"] / combined["k_{D_2O}, s^{-1}"]
    )
    n_overlaps = combined["k_{H_2O}/k_{D_2O}"].notna().sum()
    print(
        f"{len(combined)} data points from {combined.index.min()} "
        + f"to {combined.index.max()} K, {n_overlaps} in common"
    )
    print(f"written to {output_file}")
    combined.to_csv(output_file, sep="\t", float_format="%.4f")
