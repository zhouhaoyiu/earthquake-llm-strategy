#!/usr/bin/env python3
"""Ground-motion baseline using metadata and early waveform features.

This is a quick feasibility baseline. It predicts log10 ground-motion targets
within each dataset from metadata, early post-P waveform features, and their
combination.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline


METADATA_FEATURES = [
    "source_magnitude",
    "source_depth_km",
    "source_distance_km",
    "station_elevation_m",
    "station_vs30_mps",
    "year",
    "n_samples",
]

TARGET_COLUMNS = {
    "pga": "pga_cmps2",
    "pgv": "pgv_cmps",
    "sa03": "sa03_cmps2",
    "sa10": "sa10_cmps2",
    "sa30": "sa30_cmps2",
}


def to_float(value: Any) -> float | None:
    try:
        if value is None or pd.isna(value) or str(value) == "":
            return None
        value_f = float(value)
        return value_f if math.isfinite(value_f) else None
    except Exception:
        return None


def to_int(value: Any, default: int = 0) -> int:
    value_f = to_float(value)
    return default if value_f is None else int(round(value_f))


def sampling_rate(row: dict[str, Any]) -> float:
    sr = to_float(row.get("sampling_rate_hz"))
    if sr and sr > 0:
        return sr
    return 100.0


def select_rows(
    manifest: Path,
    dataset: str,
    split: str,
    n_rows: int,
    seed: int,
    max_samples: int,
    target_columns: list[str],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for chunk in pd.read_csv(manifest, chunksize=200_000, dtype=str):
        sub = chunk[
            (chunk["dataset"] == dataset)
            & (chunk["split"] == split)
            & (chunk["has_ground_motion_task"] == "1")
        ].copy()
        target_mask = np.zeros(len(sub), dtype=bool)
        for target_col in target_columns:
            if target_col in sub.columns:
                target_mask |= pd.to_numeric(sub[target_col], errors="coerce").fillna(0).to_numpy() > 0
        sub = sub[target_mask]
        if max_samples:
            sub["n_samples_num"] = pd.to_numeric(sub["n_samples"], errors="coerce")
            sub = sub[sub["n_samples_num"] <= max_samples]
        rows.extend(sub.drop(columns=[c for c in ["n_samples_num"] if c in sub]).to_dict("records"))
    rng = np.random.default_rng(seed)
    if len(rows) > n_rows:
        idx = np.arange(len(rows))
        rng.shuffle(idx)
        rows = [rows[int(i)] for i in idx[:n_rows]]
    return rows


def load_waveform(row: dict[str, Any]) -> np.ndarray:
    start = to_int(row.get("sample_start"), 0)
    stop = to_int(row.get("sample_stop"), to_int(row.get("n_samples"), 0))
    with h5py.File(row["waveform_store"], "r") as h5:
        if row["dataset"] == "knet":
            arr = h5[row["hdf5_key"]][:, start:stop]
        else:
            arr = h5[row["hdf5_key"]][to_int(row["hdf5_index"]), :, start:stop]
    return np.asarray(arr, dtype=np.float32)


def early_window(arr: np.ndarray, row: dict[str, Any], seconds: float) -> np.ndarray:
    sr = sampling_rate(row)
    p_sample = to_int(row.get("p_pick_sample"), 0)
    start = max(0, p_sample)
    stop = min(arr.shape[1], start + int(round(seconds * sr)))
    if stop <= start:
        return arr[:, : min(arr.shape[1], int(round(seconds * sr)))]
    return arr[:, start:stop]


def waveform_features(row: dict[str, Any], arr: np.ndarray, seconds: float) -> dict[str, float]:
    win = early_window(arr, row, seconds)
    feats: dict[str, float] = {"early_seconds": seconds}
    if win.size == 0:
        return feats
    comps = ["z", "n", "e"]
    abs_win = np.abs(win)
    for idx, comp in enumerate(comps):
        x = win[idx]
        ax = abs_win[idx]
        feats[f"{comp}_early_absmax"] = float(np.nanmax(ax))
        feats[f"{comp}_early_rms"] = float(np.sqrt(np.nanmean(x * x)))
        feats[f"{comp}_early_std"] = float(np.nanstd(x))
        feats[f"{comp}_early_p95_abs"] = float(np.nanpercentile(ax, 95))
    horiz = np.sqrt(win[1] ** 2 + win[2] ** 2)
    vec = np.sqrt(np.sum(win**2, axis=0))
    feats["h_early_absmax"] = float(np.nanmax(horiz))
    feats["vec_early_absmax"] = float(np.nanmax(vec))
    feats["vec_early_rms"] = float(np.sqrt(np.nanmean(vec * vec)))
    return feats


def metadata_features(row: dict[str, Any]) -> dict[str, float]:
    return {name: np.nan if to_float(row.get(name)) is None else float(row[name]) for name in METADATA_FEATURES}


def build_frame(rows: list[dict[str, str]], early_seconds: float, targets: dict[str, str]) -> pd.DataFrame:
    records = []
    for row in rows:
        try:
            arr = load_waveform(row)
            rec = {
                "global_id": row["global_id"],
                "record_id": row.get("record_id", ""),
                "event_id": row.get("event_id", ""),
                "station_network_code": row.get("station_network_code", ""),
                "station_code": row.get("station_code", ""),
                "dataset": row["dataset"],
                "split": row["split"],
            }
            valid_target = False
            for target_name, target_col in targets.items():
                target = to_float(row.get(target_col))
                if target is not None and target > 0:
                    rec[f"target_{target_name}"] = target
                    rec[f"target_log10_{target_name}"] = math.log10(target)
                    valid_target = True
                else:
                    rec[f"target_{target_name}"] = np.nan
                    rec[f"target_log10_{target_name}"] = np.nan
            if not valid_target:
                continue
            rec.update(metadata_features(row))
            rec.update(waveform_features(row, arr, early_seconds))
            records.append(rec)
        except Exception as exc:
            records.append(
                {
                    "global_id": row.get("global_id", ""),
                    "dataset": row.get("dataset", ""),
                    "split": row.get("split", ""),
                    "error": repr(exc),
                }
            )
    return pd.DataFrame(records)


def train_eval(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    features: list[str],
    model_name: str,
    dataset: str,
    target: str,
) -> dict[str, Any]:
    target_col = f"target_log10_{target}"
    train = train_df.dropna(subset=[target_col])
    test = test_df.dropna(subset=[target_col])
    if len(train) == 0 or len(test) == 0 or not features:
        return {
            "dataset": dataset,
            "target": target,
            "model": model_name,
            "features": features,
            "train_rows": int(len(train)),
            "test_rows": int(len(test)),
            "mae_log10_target": None,
            "rmse_log10_target": None,
            "r2_log10_target": None,
            "skipped": True,
        }
    x_train = train[features]
    y_train = train[target_col].astype(float)
    x_test = test[features]
    y_test = test[target_col].astype(float)

    if model_name == "median":
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
    pipe.fit(x_train, y_train)
    pred = pipe.predict(x_test)
    rmse = mean_squared_error(y_test, pred) ** 0.5
    return {
        "dataset": dataset,
        "target": target,
        "model": model_name,
        "features": features,
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "mae_log10_target": float(mean_absolute_error(y_test, pred)),
        "rmse_log10_target": float(rmse),
        "r2_log10_target": float(r2_score(y_test, pred)),
        "skipped": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("work/unified_manifest/unified_manifest.csv.gz"))
    parser.add_argument("--out-dir", type=Path, default=Path("work/ground_motion_baseline"))
    parser.add_argument("--datasets", nargs="+", default=["instancegm", "knet"])
    parser.add_argument("--train-size", type=int, default=5000)
    parser.add_argument("--test-size", type=int, default=1000)
    parser.add_argument("--early-seconds", type=float, default=3.0)
    parser.add_argument("--max-samples", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=19)
    parser.add_argument("--targets", nargs="+", default=["pga", "pgv", "sa03", "sa10", "sa30"])
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    targets = {name: TARGET_COLUMNS[name] for name in args.targets if name in TARGET_COLUMNS}
    target_columns = list(targets.values())

    all_reports = []
    data_paths = {}
    for dataset in args.datasets:
        print(f"selecting {dataset}", flush=True)
        train_rows = select_rows(args.manifest, dataset, "train", args.train_size, args.seed, args.max_samples, target_columns)
        test_rows = select_rows(args.manifest, dataset, "test", args.test_size, args.seed + 1, args.max_samples, target_columns)
        print(f"building features {dataset}: train={len(train_rows)} test={len(test_rows)}", flush=True)
        train_df = build_frame(train_rows, args.early_seconds, targets)
        test_df = build_frame(test_rows, args.early_seconds, targets)
        train_path = args.out_dir / f"{dataset}_train_features.csv"
        test_path = args.out_dir / f"{dataset}_test_features.csv"
        train_df.to_csv(train_path, index=False)
        test_df.to_csv(test_path, index=False)
        data_paths[dataset] = {"train_features": str(train_path), "test_features": str(test_path)}

        metadata_cols = [col for col in METADATA_FEATURES if col in train_df.columns]
        waveform_cols = [
            col
            for col in train_df.columns
            if col.endswith("_early_absmax")
            or col.endswith("_early_rms")
            or col.endswith("_early_std")
            or col.endswith("_early_p95_abs")
        ]
        feature_sets = {
            "median": metadata_cols[:1],
            "metadata_only": metadata_cols,
            "early_waveform_only": waveform_cols,
            "metadata_plus_early_waveform": metadata_cols + waveform_cols,
        }
        for target in targets:
            for model_name, features in feature_sets.items():
                actual_model = "median" if model_name == "median" else "hgb"
                result = train_eval(train_df, test_df, features, actual_model, dataset, target)
                result["feature_set"] = model_name
                result["early_seconds"] = args.early_seconds
                all_reports.append(result)
                print(
                    dataset,
                    target,
                    model_name,
                    result["mae_log10_target"],
                    result["r2_log10_target"],
                    flush=True,
                )

    report = {
        "manifest": str(args.manifest),
        "datasets": args.datasets,
        "train_size_requested": args.train_size,
        "test_size_requested": args.test_size,
        "early_seconds": args.early_seconds,
        "max_samples": args.max_samples,
        "targets": list(targets),
        "data_paths": data_paths,
        "results": all_reports,
        "note": "Ground-motion baseline uses early post-P waveform features to avoid full-waveform peak leakage.",
    }
    report_path = args.out_dir / "ground_motion_baseline_summary.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    with (args.out_dir / "ground_motion_baseline_results.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(all_reports[0].keys()))
        writer.writeheader()
        writer.writerows(all_reports)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
