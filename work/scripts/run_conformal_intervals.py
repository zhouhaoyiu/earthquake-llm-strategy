#!/usr/bin/env python3
"""Split-conformal intervals for existing ground-motion feature CSVs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline

from run_ground_motion_baseline import METADATA_FEATURES, TARGET_COLUMNS


def waveform_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if "_early_" in c or c in ["h_early_absmax", "vec_early_absmax", "vec_early_rms"]]


def conformal_q(scores: np.ndarray, alpha: float) -> float:
    assert 0 < alpha < 1
    assert len(scores) > 0
    k = int(np.ceil((len(scores) + 1) * (1 - alpha)))
    return float(np.sort(scores)[min(k, len(scores)) - 1])


def fit_predict(train: pd.DataFrame, test: pd.DataFrame, target: str, features: list[str], alpha: float) -> dict[str, Any] | None:
    ycol = f"target_log10_{target}"
    train = train.dropna(subset=[ycol]).copy()
    test = test.dropna(subset=[ycol]).copy()
    if len(train) < 100 or len(test) < 50:
        return None
    train = train.sample(frac=1, random_state=17)
    n_cal = max(100, int(len(train) * 0.2))
    cal, proper = train.iloc[:n_cal], train.iloc[n_cal:]
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_leaf_nodes=31, random_state=17, l2_regularization=0.01),
    )
    model.fit(proper[features], proper[ycol].astype(float))
    q = conformal_q(np.abs(model.predict(cal[features]) - cal[ycol].to_numpy(float)), alpha)
    pred = model.predict(test[features])
    y = test[ycol].to_numpy(float)
    cover = np.mean((y >= pred - q) & (y <= pred + q))
    return {
        "target": target,
        "train_rows": int(len(proper)),
        "calibration_rows": int(len(cal)),
        "test_rows": int(len(test)),
        "q90_abs_residual": q,
        "interval_width": 2 * q,
        "coverage": float(cover),
        "mae": float(np.mean(np.abs(pred - y))),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--feature-dir", type=Path, default=Path("work/ground_motion_balanced_station_10s"))
    p.add_argument("--out", type=Path, default=Path("work/ground_motion_balanced_station_10s/conformal_intervals.csv"))
    p.add_argument("--datasets", nargs="+", default=["instancegm", "knet"])
    p.add_argument("--targets", nargs="+", default=["pga", "pgv", "sa03", "sa10", "sa30"])
    p.add_argument("--alpha", type=float, default=0.1)
    args = p.parse_args()
    rows = []
    for dataset in args.datasets:
        train = pd.read_csv(args.feature_dir / f"{dataset}_held_station_train_features.csv")
        test = pd.read_csv(args.feature_dir / f"{dataset}_held_station_test_features.csv")
        features = [c for c in METADATA_FEATURES if c in train.columns] + waveform_cols(train)
        for target in args.targets:
            if target not in TARGET_COLUMNS:
                continue
            row = fit_predict(train, test, target, features, args.alpha)
            if row:
                rows.append({"dataset": dataset, "split": "balanced_held_station", **row})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
