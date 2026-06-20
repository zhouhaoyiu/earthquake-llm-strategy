#!/usr/bin/env python3
"""Stress-test AQ2009GM full-manifest feature tables."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline

from run_aq2009gm_chunk_baseline import METADATA_FEATURES, TARGETS, waveform_feature_cols


def load_features(feature_dir: Path) -> pd.DataFrame:
    files = sorted(feature_dir.glob("aq2009gm_chunk*_features.csv.gz"))
    if not files:
        raise FileNotFoundError(f"no feature tables under {feature_dir}")
    print(f"[load] {len(files)} chunk feature tables", flush=True)
    return pd.concat((pd.read_csv(path, low_memory=False) for path in files), ignore_index=True)


def take_sample(df: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    return df.sample(n, random_state=seed) if len(df) > n else df.copy()


def split_stats(train: pd.DataFrame, test: pd.DataFrame, name: str, target: str) -> dict[str, Any]:
    train_events = set(train["source_id"].fillna("").astype(str))
    test_events = set(test["source_id"].fillna("").astype(str))
    train_stations = set(train["station_group"].fillna("").astype(str))
    test_stations = set(test["station_group"].fillna("").astype(str))
    return {
        "split": name,
        "target": target,
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_events": int(len(train_events - {""})),
        "test_events": int(len(test_events - {""})),
        "event_overlap": int(len((train_events & test_events) - {""})),
        "train_stations": int(len(train_stations - {"", "."})),
        "test_stations": int(len(test_stations - {"", "."})),
        "station_overlap": int(len((train_stations & test_stations) - {"", "."})),
        "train_magnitude_min": float(pd.to_numeric(train["source_magnitude"], errors="coerce").min()),
        "train_magnitude_max": float(pd.to_numeric(train["source_magnitude"], errors="coerce").max()),
        "test_magnitude_min": float(pd.to_numeric(test["source_magnitude"], errors="coerce").min()),
        "test_magnitude_max": float(pd.to_numeric(test["source_magnitude"], errors="coerce").max()),
        "train_distance_median": float(pd.to_numeric(train["path_hyp_distance_km"], errors="coerce").median()),
        "test_distance_median": float(pd.to_numeric(test["path_hyp_distance_km"], errors="coerce").median()),
    }


def high_magnitude_split(base: pd.DataFrame, train_size: int, test_size: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = base[base["source_id"].notna()].copy()
    group_mag = pd.to_numeric(work["source_magnitude"], errors="coerce").groupby(work["source_id"].astype(str)).median()
    group_sizes = work["source_id"].astype(str).value_counts()
    test_groups: list[str] = []
    test_rows = 0
    for group in group_mag.sort_values(ascending=False).index:
        test_groups.append(str(group))
        test_rows += int(group_sizes.get(group, 0))
        if test_rows >= test_size:
            break
    test = work[work["source_id"].astype(str).isin(test_groups)]
    train = work[~work["source_id"].astype(str).isin(test_groups)]
    return take_sample(train, train_size, seed + 1), take_sample(test, test_size, seed + 2)


def far_distance_split(base: pd.DataFrame, train_size: int, test_size: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = base.copy()
    work["_dist"] = pd.to_numeric(work["path_hyp_distance_km"], errors="coerce")
    work = work[work["_dist"].notna()].sort_values("_dist")
    test = work.tail(test_size)
    train = work.drop(test.index)
    return take_sample(train, train_size, seed + 3), test.copy()


def target_tail_split(base: pd.DataFrame, target: str, train_size: int, test_size: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    col = f"target_log10_{target}"
    work = base[pd.to_numeric(base[col], errors="coerce").notna()].copy().sort_values(col)
    test = work.tail(test_size)
    train = work.drop(test.index)
    return take_sample(train, train_size, seed + 5), test.copy()


def fit_eval(train: pd.DataFrame, test: pd.DataFrame, cols: list[str], target_col: str) -> tuple[dict[str, float], np.ndarray, np.ndarray]:
    model = HistGradientBoostingRegressor(
        max_iter=200,
        learning_rate=0.05,
        max_leaf_nodes=31,
        random_state=17,
        l2_regularization=0.01,
    )
    pipe = make_pipeline(SimpleImputer(strategy="median"), model)
    y_train = train[target_col].astype(float).to_numpy()
    y_test = test[target_col].astype(float).to_numpy()
    pipe.fit(train[cols], y_train)
    pred_train = pipe.predict(train[cols])
    pred_test = pipe.predict(test[cols])
    err = np.abs(y_test - pred_test)
    return (
        {
            "mae": float(mean_absolute_error(y_test, pred_test)),
            "rmse": float(mean_squared_error(y_test, pred_test) ** 0.5),
            "q95_abs_error": float(np.nanpercentile(err, 95)),
            "r2": float(r2_score(y_test, pred_test)),
        },
        y_train - pred_train,
        y_test - pred_test,
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature-dir", type=Path, default=Path("work/aq2009gm_full_stream_validation/features"))
    parser.add_argument("--out-dir", type=Path, default=Path("work/aq2009gm_full_stream_stress_tests"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/aq2009gm_full_stream_stress_tests_summary.md"))
    parser.add_argument("--windows", nargs="+", type=float, default=[1.0, 3.0, 10.0])
    parser.add_argument("--train-size", type=int, default=30000)
    parser.add_argument("--test-size", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=43)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    features = load_features(args.feature_dir)
    first_window = float(min(args.windows))
    base = features[features["early_seconds"].eq(first_window)].drop_duplicates("row_id").copy()
    metadata_cols = [col for col in METADATA_FEATURES if col in features.columns]
    wave_cols = waveform_feature_cols(features)
    feature_sets = {
        "metadata_only": metadata_cols,
        "metadata_plus_early_velocity": metadata_cols + wave_cols,
    }

    metrics: list[dict[str, Any]] = []
    uncertainty: list[dict[str, Any]] = []
    split_rows: list[dict[str, Any]] = []

    for target in TARGETS:
        target_col = f"target_log10_{target}"
        split_defs = {
            "high_magnitude_event": high_magnitude_split(base, args.train_size, args.test_size, args.seed),
            "far_distance_path": far_distance_split(base, args.train_size, args.test_size, args.seed),
            "high_target_tail": target_tail_split(base, target, args.train_size, args.test_size, args.seed),
        }
        for split_name, (train_base, test_base) in split_defs.items():
            split_rows.append(split_stats(train_base, test_base, split_name, target))
            train_ids = set(train_base["row_id"])
            test_ids = set(test_base["row_id"])
            for seconds in args.windows:
                sub = features[features["early_seconds"].eq(float(seconds))]
                train = sub[sub["row_id"].isin(train_ids)].dropna(subset=[target_col]).copy()
                test = sub[sub["row_id"].isin(test_ids)].dropna(subset=[target_col]).copy()
                if len(train) == 0 or len(test) == 0:
                    continue
                fitted: dict[str, tuple[dict[str, float], np.ndarray, np.ndarray]] = {}
                for feature_set, cols in feature_sets.items():
                    print(f"[fit] {split_name} {target} {seconds:g}s {feature_set}", flush=True)
                    fitted[feature_set] = fit_eval(train, test, cols, target_col)
                    score, _, _ = fitted[feature_set]
                    metrics.append(
                        {
                            "dataset": "aq2009gm_full_stream",
                            "split": split_name,
                            "target": target,
                            "early_seconds": float(seconds),
                            "feature_set": feature_set,
                            "train_rows": int(len(train)),
                            "test_rows": int(len(test)),
                            **score,
                        }
                    )
                meta, _, _ = fitted["metadata_only"]
                comb, train_res, test_res = fitted["metadata_plus_early_velocity"]
                uncertainty.append(
                    {
                        "dataset": "aq2009gm_full_stream",
                        "split": split_name,
                        "target": target,
                        "early_seconds": float(seconds),
                        "metadata_mae": meta["mae"],
                        "combined_mae": comb["mae"],
                        "mae_reduction_pct": 100.0 * (meta["mae"] - comb["mae"]) / meta["mae"] if meta["mae"] else math.nan,
                        "combined_r2": comb["r2"],
                        "train_q90_abs_error": float(np.nanquantile(np.abs(train_res), 0.9)),
                        "test_q90_coverage": float(np.mean(np.abs(test_res) <= np.nanquantile(np.abs(train_res), 0.9))),
                        "train_q95_abs_error": float(np.nanquantile(np.abs(train_res), 0.95)),
                        "test_q95_coverage": float(np.mean(np.abs(test_res) <= np.nanquantile(np.abs(train_res), 0.95))),
                    }
                )

    write_csv(args.out_dir / "aq2009gm_stream_stress_metrics.csv", metrics)
    write_csv(args.out_dir / "aq2009gm_stream_stress_uncertainty.csv", uncertainty)
    write_csv(args.out_dir / "aq2009gm_stream_stress_splits.csv", split_rows)

    u = pd.DataFrame(uncertainty)
    lines = [
        "# AQ2009GM full-manifest stress tests",
        "",
        f"- feature rows: {len(features)}",
        f"- unique valid records: {base['row_id'].nunique()}",
        f"- train/test cap: {args.train_size}/{args.test_size}",
        "",
        "| Split | Target | Window | MAE reduction | Combined R2 | Q90 coverage | Q95 coverage |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in u.sort_values(["split", "target", "early_seconds"]).itertuples(index=False):
        lines.append(
            f"| {row.split} | {row.target.upper()} | {row.early_seconds:.0f}s | "
            f"{row.mae_reduction_pct:.1f}% | {row.combined_r2:.3f} | "
            f"{row.test_q90_coverage:.3f} | {row.test_q95_coverage:.3f} |"
        )
    lines.extend(
        [
            "",
            "Files:",
            f"- `{args.out_dir / 'aq2009gm_stream_stress_metrics.csv'}`",
            f"- `{args.out_dir / 'aq2009gm_stream_stress_uncertainty.csv'}`",
            f"- `{args.out_dir / 'aq2009gm_stream_stress_splits.csv'}`",
        ]
    )
    args.summary.write_text("\n".join(lines) + "\n")
    print(json.dumps({"summary": str(args.summary), "rows": len(uncertainty)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
