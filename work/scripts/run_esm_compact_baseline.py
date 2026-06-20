#!/usr/bin/env python3
"""Held-out baselines for compact ESM early-window features."""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline


TARGETS = ["pga", "pgv"]
RAW_WAVEFORM_COLS = [
    "z_early_absmax",
    "z_early_rms",
    "z_early_std",
    "z_early_p95_abs",
    "n_early_absmax",
    "n_early_rms",
    "n_early_std",
    "n_early_p95_abs",
    "e_early_absmax",
    "e_early_rms",
    "e_early_std",
    "e_early_p95_abs",
    "h_early_absmax",
    "vec_early_absmax",
    "vec_early_rms",
]
DISTANCE_COLS = ["log10_source_distance_km", "log10_path_hyp_distance_km", "p_arrival_offset_s"]
SITE_COLS = ["log10_station_vs30_mps", "station_elevation_m"]


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in RAW_WAVEFORM_COLS:
        if col in out:
            values = pd.to_numeric(out[col], errors="coerce").astype(float)
            out[f"log10_{col}"] = np.log10(np.maximum(np.abs(values), 0.0) + 1e-12)
    for col in ["source_distance_km", "path_hyp_distance_km", "station_vs30_mps"]:
        if col in out:
            values = pd.to_numeric(out[col], errors="coerce").astype(float)
            out[f"log10_{col}"] = np.log10(np.maximum(values, 0.0) + 1e-6)
    return out


def split_by_group(
    df: pd.DataFrame,
    group_col: str,
    train_size: int,
    test_size: int,
    seed: int,
    station_test_groups: int = 0,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    work = df.copy()
    work["_group"] = work[group_col].fillna("").astype(str)
    work = work[work["_group"].ne("")].copy()
    group_sizes = work["_group"].value_counts()
    groups = np.array(group_sizes.index.tolist(), dtype=object)
    rng = np.random.default_rng(seed)
    rng.shuffle(groups)

    if station_test_groups:
        test_groups = [str(group) for group in groups[: min(station_test_groups, len(groups))]]
    else:
        test_groups = []
        test_rows = 0
        for group in groups:
            test_groups.append(str(group))
            test_rows += int(group_sizes.loc[group])
            if test_rows >= test_size:
                break

    test_set = set(test_groups)
    train = work[~work["_group"].isin(test_set)].copy()
    test = work[work["_group"].isin(test_set)].copy()
    if len(train) > train_size:
        train = train.sample(train_size, random_state=seed + 11)
    if len(test) > test_size:
        test = test.sample(test_size, random_state=seed + 17)

    overlap = set(train["_group"]).intersection(set(test["_group"]))
    if overlap:
        raise RuntimeError(f"group overlap in {group_col}: {sorted(overlap)[:3]}")
    info = {
        "group_column": group_col,
        "eligible_rows": int(len(work)),
        "eligible_groups": int(work["_group"].nunique()),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_groups": int(train["_group"].nunique()),
        "test_groups": int(test["_group"].nunique()),
        "group_overlap": int(len(overlap)),
    }
    return train.drop(columns=["_group"]), test.drop(columns=["_group"]), info


def fit_predict(train: pd.DataFrame, test: pd.DataFrame, cols: list[str], target_col: str, feature_set: str) -> np.ndarray:
    if feature_set == "median":
        model = DummyRegressor(strategy="median")
    else:
        model = HistGradientBoostingRegressor(
            max_iter=200,
            learning_rate=0.05,
            max_leaf_nodes=31,
            random_state=17,
            l2_regularization=0.01,
        )
    pipe = make_pipeline(SimpleImputer(strategy="median"), model)
    pipe.fit(train[cols], train[target_col].astype(float))
    return pipe.predict(test[cols])


def score(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    abs_err = np.abs(y - pred)
    return {
        "mae_log10_target": float(mean_absolute_error(y, pred)),
        "rmse_log10_target": float(mean_squared_error(y, pred) ** 0.5),
        "r2_log10_target": float(r2_score(y, pred)),
        "q90_abs_error_log10_target": float(np.nanquantile(abs_err, 0.9)),
        "q95_abs_error_log10_target": float(np.nanquantile(abs_err, 0.95)),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, rows: list[dict[str, Any]], splits: list[dict[str, Any]], out_dir: Path) -> None:
    df = pd.DataFrame(rows)
    lines = [
        "# ESM held-out early-window baseline",
        "",
        "This check uses compact features extracted from local ESM ASCII zip packages. P windows use a fixed-velocity theoretical onset.",
        "",
        "Splits:",
        "",
        "| Holdout | Window | Train rows | Test rows | Train groups | Test groups | Overlap |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in splits:
        lines.append(
            f"| {row['holdout']} | {row['early_seconds']:.0f}s | {row['train_rows']} | {row['test_rows']} | "
            f"{row['train_groups']} | {row['test_groups']} | {row['group_overlap']} |"
        )

    lines.extend(
        [
            "",
            "Held-station information gain:",
            "",
            "| Target | Window | Median MAE | P only MAE | P+distance MAE | P+distance+site MAE | Site gain vs P+distance |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    station = df[df["holdout"].eq("station")].copy()
    for target in TARGETS:
        for window in sorted(station["early_seconds"].unique()):
            sub = station[(station["target"].eq(target)) & (station["early_seconds"].eq(window))]
            vals = sub.set_index("feature_set")["mae_log10_target"].to_dict()
            dist = vals.get("p_waveform_plus_distance", np.nan)
            site = vals.get("p_waveform_distance_site", np.nan)
            gain = 100.0 * (dist - site) / dist if dist and np.isfinite(dist) else np.nan
            lines.append(
                f"| {target.upper()} | {window:.0f}s | {vals.get('median', np.nan):.3f} | "
                f"{vals.get('p_waveform_only', np.nan):.3f} | {dist:.3f} | {site:.3f} | {gain:.1f}% |"
            )

    lines.extend(
        [
            "",
            "Files:",
            f"- `{out_dir / 'esm_heldout_metrics.csv'}`",
            f"- `{out_dir / 'esm_heldout_split_info.csv'}`",
            f"- `{out_dir / 'esm_heldout_summary.json'}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", type=Path, default=Path("work/esm_compact_features_full/esm_compact_features.csv.gz"))
    parser.add_argument("--out-dir", type=Path, default=Path("work/esm_heldout_baseline"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/esm_heldout_baseline_summary.md"))
    parser.add_argument("--windows", nargs="+", type=float, default=[1.0, 2.0, 3.0, 5.0, 10.0])
    parser.add_argument("--train-size", type=int, default=20000)
    parser.add_argument("--test-size", type=int, default=6000)
    parser.add_argument("--station-test-groups", type=int, default=200)
    parser.add_argument("--seed", type=int, default=71)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)

    df = add_features(pd.read_csv(args.features, low_memory=False))
    log_waveform = [f"log10_{col}" for col in RAW_WAVEFORM_COLS if f"log10_{col}" in df.columns]
    feature_sets = {
        "median": ["early_seconds"],
        "p_waveform_only": log_waveform,
        "p_waveform_plus_distance": log_waveform + [col for col in DISTANCE_COLS if col in df.columns],
        "p_waveform_distance_site": log_waveform + [col for col in DISTANCE_COLS + SITE_COLS if col in df.columns],
    }

    rows: list[dict[str, Any]] = []
    splits: list[dict[str, Any]] = []
    for window in args.windows:
        sub = df[df["early_seconds"].astype(float).eq(float(window))].copy()
        sub = sub[sub["p_window_valid"].astype(bool)].copy()
        for holdout, group_col in [("event", "event_id"), ("station", "station_group")]:
            train, test, split = split_by_group(
                sub,
                group_col=group_col,
                train_size=args.train_size,
                test_size=args.test_size,
                seed=args.seed + int(window * 10) + (1000 if holdout == "station" else 0),
                station_test_groups=args.station_test_groups if holdout == "station" else 0,
            )
            split.update({"holdout": holdout, "early_seconds": float(window)})
            splits.append(split)
            for target in TARGETS:
                target_col = f"target_log10_{target}"
                train_target = train[pd.to_numeric(train[target_col], errors="coerce").notna()].copy()
                test_target = test[pd.to_numeric(test[target_col], errors="coerce").notna()].copy()
                y = test_target[target_col].astype(float).to_numpy()
                for feature_set, cols in feature_sets.items():
                    print(f"[fit] window={window:g}s holdout={holdout} target={target} features={feature_set}", flush=True)
                    pred = fit_predict(train_target, test_target, cols, target_col, feature_set)
                    rows.append(
                        {
                            "dataset": "esm",
                            "holdout": holdout,
                            "target": target,
                            "early_seconds": float(window),
                            "feature_set": feature_set,
                            "train_rows": int(len(train_target)),
                            "test_rows": int(len(test_target)),
                            "train_groups": split["train_groups"],
                            "test_groups": split["test_groups"],
                            "group_overlap": split["group_overlap"],
                            **score(y, pred),
                        }
                    )

    metrics_path = args.out_dir / "esm_heldout_metrics.csv"
    split_path = args.out_dir / "esm_heldout_split_info.csv"
    write_csv(metrics_path, rows)
    write_csv(split_path, splits)
    write_summary(args.summary, rows, splits, args.out_dir)
    report = {
        "metrics": str(metrics_path),
        "split_info": str(split_path),
        "summary": str(args.summary),
        "rows": len(rows),
    }
    (args.out_dir / "esm_heldout_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
