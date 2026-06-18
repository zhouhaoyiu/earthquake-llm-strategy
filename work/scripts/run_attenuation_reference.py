#!/usr/bin/env python3
"""Simple attenuation-shaped reference for existing held-station features."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


TARGETS = ["pga", "pgv", "sa03", "sa10", "sa30"]


def design(df: pd.DataFrame) -> pd.DataFrame:
    r = pd.to_numeric(df["source_distance_km"], errors="coerce").clip(lower=0)
    h = pd.to_numeric(df["source_depth_km"], errors="coerce").clip(lower=0)
    out = pd.DataFrame(
        {
            "magnitude": pd.to_numeric(df["source_magnitude"], errors="coerce"),
            "log10_rhyp": np.log10(np.sqrt(r * r + h * h).clip(lower=1.0)),
            "depth_km": h,
            "log10_vs30": np.log10(pd.to_numeric(df.get("station_vs30_mps"), errors="coerce").clip(lower=100)),
        }
    )
    return out


def eval_target(train: pd.DataFrame, test: pd.DataFrame, target: str) -> dict | None:
    ycol = f"target_log10_{target}"
    train = train.dropna(subset=[ycol])
    test = test.dropna(subset=[ycol])
    if len(train) < 100 or len(test) < 50:
        return None
    model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=1.0))
    model.fit(design(train), train[ycol].astype(float))
    pred = model.predict(design(test))
    y = test[ycol].to_numpy(float)
    return {
        "target": target,
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "mae_log10_target": float(mean_absolute_error(y, pred)),
        "r2_log10_target": float(r2_score(y, pred)),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--feature-dir", type=Path, default=Path("work/ground_motion_balanced_station_10s"))
    p.add_argument("--out", type=Path, default=Path("work/ground_motion_balanced_station_10s/attenuation_reference.csv"))
    p.add_argument("--datasets", nargs="+", default=["instancegm", "knet"])
    args = p.parse_args()
    rows = []
    for dataset in args.datasets:
        train = pd.read_csv(args.feature_dir / f"{dataset}_held_station_train_features.csv")
        test = pd.read_csv(args.feature_dir / f"{dataset}_held_station_test_features.csv")
        for target in TARGETS:
            row = eval_target(train, test, target)
            if row:
                rows.append({"dataset": dataset, "split": "balanced_held_station", "model": "attenuation_ridge", **row})
    assert rows
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
