#!/usr/bin/env python3
"""OpenQuake BooreEtAl2014 reference on existing feature CSVs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd
from openquake.hazardlib.gsim.boore_2014 import BooreEtAl2014
from openquake.hazardlib.imt import PGA, PGV, SA
from sklearn.metrics import mean_absolute_error, r2_score


G_CMPS2 = 980.665
IMTS = {"pga": PGA(), "pgv": PGV(), "sa03": SA(0.3), "sa10": SA(1.0), "sa30": SA(3.0)}


def gmpe_log10(df: pd.DataFrame, target: str) -> np.ndarray:
    ctx = np.recarray(len(df), dtype=[("mag", float), ("rake", float), ("rjb", float), ("vs30", float)])
    ctx.mag = pd.to_numeric(df["source_magnitude"], errors="coerce").fillna(5.0).to_numpy(float)
    ctx.rake = 0.0
    # ponytail: hypocentral/source distance used as Rjb proxy; replace with rupture geometry if available.
    ctx.rjb = pd.to_numeric(df["source_distance_km"], errors="coerce").clip(lower=1.0).fillna(10.0).to_numpy(float)
    ctx.vs30 = pd.to_numeric(df.get("station_vs30_mps"), errors="coerce").clip(lower=150, upper=1500).fillna(760.0).to_numpy(float)
    mean = np.zeros((1, len(df)))
    sig = np.zeros_like(mean)
    tau = np.zeros_like(mean)
    phi = np.zeros_like(mean)
    BooreEtAl2014().compute(ctx, [IMTS[target]], mean, sig, tau, phi)
    values = np.exp(mean[0])
    if target != "pgv":
        values = values * G_CMPS2
    return np.log10(values)


def eval_dataset(feature_dir: Path, dataset: str, target: str) -> dict | None:
    ycol = f"target_log10_{target}"
    train = pd.read_csv(feature_dir / f"{dataset}_held_station_train_features.csv").dropna(subset=[ycol])
    test = pd.read_csv(feature_dir / f"{dataset}_held_station_test_features.csv").dropna(subset=[ycol])
    if len(train) < 100 or len(test) < 50:
        return None
    pred_train = gmpe_log10(train, target)
    bias = float(np.median(train[ycol].to_numpy(float) - pred_train))
    pred = gmpe_log10(test, target) + bias
    y = test[ycol].to_numpy(float)
    return {
        "dataset": dataset,
        "target": target,
        "model": "boore_2014_bias_corrected",
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "bias_log10": bias,
        "mae_log10_target": float(mean_absolute_error(y, pred)),
        "r2_log10_target": float(r2_score(y, pred)),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--feature-dir", type=Path, default=Path("work/ground_motion_balanced_station_10s"))
    p.add_argument("--out", type=Path, default=Path("work/ground_motion_balanced_station_10s/openquake_reference.csv"))
    p.add_argument("--datasets", nargs="+", default=["instancegm", "knet"])
    p.add_argument("--targets", nargs="+", default=list(IMTS))
    args = p.parse_args()
    rows = [r for d in args.datasets for t in args.targets if t in IMTS and (r := eval_dataset(args.feature_dir, d, t))]
    assert rows
    with args.out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
