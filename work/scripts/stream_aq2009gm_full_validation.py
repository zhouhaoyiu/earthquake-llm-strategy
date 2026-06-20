#!/usr/bin/env python3
"""Stream AQ2009GM chunks into compact features, then evaluate."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
print("[startup] stream_aq2009gm_full_validation.py", flush=True)

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import make_pipeline

from run_aq2009gm_chunk_baseline import (
    METADATA_FEATURES,
    TARGETS,
    build_features,
    compare_results,
    load_metadata,
    plot_comparison,
    split_by_group,
    train_eval,
    waveform_feature_cols,
    write_csv,
)


def read_chunks(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def cleanup_raw(cache_dir: Path, chunk: str) -> None:
    for suffix in [".csv", ".csv.partial"]:
        (cache_dir / f"metadata{chunk}{suffix}").unlink(missing_ok=True)
    for suffix in [".hdf5", ".hdf5.partial"]:
        (cache_dir / f"waveforms{chunk}{suffix}").unlink(missing_ok=True)


def download_chunk(cache_dir: Path, chunk: str, retries: int, retry_sleep_sec: float) -> None:
    if (cache_dir / f"metadata{chunk}.csv").exists() and (cache_dir / f"waveforms{chunk}.hdf5").exists():
        return
    import requests
    import seisbench.data as sbd

    if not getattr(requests.get, "_aq_timeout_wrapped", False):
        original_get = requests.get

        def get_with_timeout(*args: Any, **kwargs: Any) -> Any:
            kwargs.setdefault("timeout", (30, 120))
            return original_get(*args, **kwargs)

        get_with_timeout._aq_timeout_wrapped = True  # type: ignore[attr-defined]
        requests.get = get_with_timeout

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        cleanup_raw(cache_dir, chunk)
        try:
            sbd.AQ2009GM(chunks=[chunk])
            return
        except Exception as exc:
            last_error = exc
            print(f"[download_retry] chunk={chunk} attempt={attempt}/{retries} error={exc!r}", flush=True)
            if attempt < retries:
                time.sleep(retry_sleep_sec)
    raise RuntimeError(f"failed to download chunk {chunk} after {retries} attempts") from last_error


def extract_chunk(cache_dir: Path, chunk: str, windows: list[float], feature_dir: Path) -> dict[str, Any]:
    feature_path = feature_dir / f"aq2009gm_chunk{chunk}_features.csv.gz"
    error_path = feature_dir / f"aq2009gm_chunk{chunk}_errors.csv"
    metadata_path = cache_dir / f"metadata{chunk}.csv"

    all_rows = len(pd.read_csv(metadata_path, usecols=["trace_name"], low_memory=False))
    metadata = load_metadata(metadata_path, chunk, row_offset=int(chunk) * 10_000_000)
    features, data_format, errors = build_features(metadata, cache_dir, windows)
    features.to_csv(feature_path, index=False)
    write_csv(error_path, errors)
    return {
        "chunk": chunk,
        "metadata_all_rows": int(all_rows),
        "valid_rows": int(metadata["row_id"].nunique()),
        "feature_rows": int(len(features)),
        "valid_events": int(metadata["source_id"].nunique()),
        "valid_stations": int(metadata["station_group"].nunique()),
        "errors": int(len(errors)),
        "data_format": data_format,
        "feature_path": str(feature_path),
        "error_path": str(error_path),
    }


def load_stream_features(feature_dir: Path) -> pd.DataFrame:
    files = sorted(feature_dir.glob("aq2009gm_chunk*_features.csv.gz"))
    if not files:
        raise FileNotFoundError(f"no chunk features under {feature_dir}")
    return pd.concat((pd.read_csv(path, low_memory=False) for path in files), ignore_index=True)


def split_by_time(
    df: pd.DataFrame,
    dataset: str,
    train_size: int,
    test_size: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    work = df.copy()
    work["_group"] = work["source_id"].fillna("").astype(str)
    work["_time"] = pd.to_datetime(work["source_origin_time"], errors="coerce", utc=True)
    work = work[work["_group"].ne("") & work["_time"].notna()].copy()

    group_times = work.groupby("_group")["_time"].min().sort_values()
    group_sizes = work["_group"].value_counts()
    test_groups: list[str] = []
    test_rows = 0
    for group in reversed(group_times.index.tolist()):
        test_groups.append(str(group))
        test_rows += int(group_sizes.loc[group])
        if test_rows >= test_size:
            break

    test_group_set = set(test_groups)
    train = work[~work["_group"].isin(test_group_set)]
    test = work[work["_group"].isin(test_group_set)]
    if len(train) > train_size:
        train = train.sample(train_size, random_state=seed + 31)
    if len(test) > test_size:
        test = test.sample(test_size, random_state=seed + 37)

    overlap = set(train["_group"]).intersection(set(test["_group"]))
    if overlap:
        raise RuntimeError(f"held-time overlap: {sorted(overlap)[:3]}")
    info = {
        "dataset": dataset,
        "holdout": "time",
        "group_column": "source_id",
        "eligible_rows": int(len(work)),
        "eligible_groups": int(work["_group"].nunique()),
        "train_rows_selected": int(len(train)),
        "test_rows_selected": int(len(test)),
        "train_groups": int(train["_group"].nunique()),
        "test_groups": int(test["_group"].nunique()),
        "group_overlap": int(len(overlap)),
        "station_test_groups_requested": 0,
    }
    return train["row_id"].to_numpy(), test["row_id"].to_numpy(), info


def fit_hgb(train: pd.DataFrame, test: pd.DataFrame, cols: list[str], target_col: str) -> tuple[np.ndarray, np.ndarray]:
    model = HistGradientBoostingRegressor(
        max_iter=200,
        learning_rate=0.05,
        max_leaf_nodes=31,
        random_state=17,
        l2_regularization=0.01,
    )
    pipe = make_pipeline(SimpleImputer(strategy="median"), model)
    pipe.fit(train[cols], train[target_col].astype(float))
    return pipe.predict(train[cols]), pipe.predict(test[cols])


def qcut_labels(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.nunique(dropna=True) < 3:
        return pd.Series(["all"] * len(values), index=values.index)
    labels = pd.qcut(numeric, q=3, labels=["low", "mid", "high"], duplicates="drop")
    return labels.astype(str).fillna("missing")


def subgroup_rows(
    dataset: str,
    holdout: str,
    target: str,
    seconds: float,
    test: pd.DataFrame,
    y: np.ndarray,
    pred_meta: np.ndarray,
    pred_combined: np.ndarray,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    families = {
        "magnitude": test.get("source_magnitude"),
        "hyp_distance": test.get("path_hyp_distance_km"),
        "target_level": pd.Series(y, index=test.index),
    }
    for family, values in families.items():
        if values is None:
            continue
        bins = qcut_labels(pd.Series(values, index=test.index))
        for label in sorted(set(bins)):
            mask = bins.eq(label).to_numpy()
            if not mask.any():
                continue
            meta_mae = float(mean_absolute_error(y[mask], pred_meta[mask]))
            comb_mae = float(mean_absolute_error(y[mask], pred_combined[mask]))
            rows.append(
                {
                    "dataset": dataset,
                    "holdout": holdout,
                    "target": target,
                    "early_seconds": seconds,
                    "bin_family": family,
                    "bin": label,
                    "test_rows": int(mask.sum()),
                    "metadata_mae_log10_target": meta_mae,
                    "combined_mae_log10_target": comb_mae,
                    "mae_reduction_pct": 100.0 * (meta_mae - comb_mae) / meta_mae if meta_mae else math.nan,
                }
            )
    return rows


def evaluate(features: pd.DataFrame, args: argparse.Namespace, chunks: list[str], chunk_reports: list[dict[str, Any]]) -> dict[str, Any]:
    dataset = "aq2009gm_full_stream" if len(chunks) == len(read_chunks(args.chunks_file)) else "aq2009gm_stream_subset"
    first_window = float(args.windows[0])
    metadata = features[features["early_seconds"].eq(first_window)].drop_duplicates("row_id").copy()

    splits: dict[str, tuple[np.ndarray, np.ndarray, dict[str, Any]]] = {}
    for holdout in ["event", "station"]:
        splits[holdout] = split_by_group(
            metadata,
            dataset,
            holdout,
            args.train_size,
            args.test_size,
            args.station_test_groups,
            args.seed + (101 if holdout == "station" else 0),
        )
    splits["time"] = split_by_time(metadata, dataset, args.train_size, args.test_size, args.seed + 203)

    metrics: list[dict[str, Any]] = []
    subgroup: list[dict[str, Any]] = []
    uncertainty: list[dict[str, Any]] = []
    for holdout, (train_ids, test_ids, info) in splits.items():
        for seconds in args.windows:
            sub = features[features["early_seconds"].eq(float(seconds))]
            train = sub[sub["row_id"].isin(train_ids)].dropna(subset=["row_id"]).copy()
            test = sub[sub["row_id"].isin(test_ids)].dropna(subset=["row_id"]).copy()
            metadata_cols = [col for col in METADATA_FEATURES if col in sub.columns]
            wave_cols = waveform_feature_cols(sub)
            feature_sets = {
                "median": metadata_cols[:1],
                "metadata_only": metadata_cols,
                "early_velocity_only": wave_cols,
                "metadata_plus_early_velocity": metadata_cols + wave_cols,
            }
            for target in TARGETS:
                target_col = f"target_log10_{target}"
                for name, cols in feature_sets.items():
                    metrics.append(train_eval(train, test, cols, name, holdout, target, seconds, info, dataset))

                ready_train = train.dropna(subset=[target_col])
                ready_test = test.dropna(subset=[target_col])
                if len(ready_train) == 0 or len(ready_test) == 0:
                    continue
                y_train = ready_train[target_col].astype(float).to_numpy()
                y_test = ready_test[target_col].astype(float).to_numpy()
                pred_meta_train, pred_meta_test = fit_hgb(ready_train, ready_test, metadata_cols, target_col)
                pred_comb_train, pred_comb_test = fit_hgb(ready_train, ready_test, metadata_cols + wave_cols, target_col)
                subgroup.extend(subgroup_rows(dataset, holdout, target, seconds, ready_test, y_test, pred_meta_test, pred_comb_test))
                abs_train = np.abs(y_train - pred_comb_train)
                abs_test = np.abs(y_test - pred_comb_test)
                for q in [0.5, 0.9, 0.95]:
                    bound = float(np.nanquantile(abs_train, q))
                    uncertainty.append(
                        {
                            "dataset": dataset,
                            "holdout": holdout,
                            "target": target,
                            "early_seconds": seconds,
                            "quantile": q,
                            "train_abs_error_bound": bound,
                            "test_coverage": float(np.mean(abs_test <= bound)),
                            "test_mean_abs_error": float(np.mean(abs_test)),
                            "test_q95_abs_error": float(np.nanquantile(abs_test, 0.95)),
                        }
                    )

    comparisons = compare_results(metrics)
    prefix = dataset
    write_csv(args.out_dir / f"{prefix}_metrics.csv", metrics)
    write_csv(args.out_dir / f"{prefix}_comparison.csv", comparisons)
    write_csv(args.out_dir / f"{prefix}_split_info.csv", [info for _, _, info in splits.values()])
    write_csv(args.out_dir / f"{prefix}_subgroup.csv", subgroup)
    write_csv(args.out_dir / f"{prefix}_uncertainty.csv", uncertainty)
    plot_comparison(comparisons, args.figure, f"{dataset} early velocity information")

    summary = {
        "dataset": dataset,
        "chunks_requested": chunks,
        "chunk_count": len(chunks),
        "metadata_all_rows": int(sum(row.get("metadata_all_rows", 0) for row in chunk_reports)),
        "valid_rows": int(metadata["row_id"].nunique()),
        "valid_events": int(metadata["source_id"].nunique()),
        "valid_stations": int(metadata["station_group"].nunique()),
        "windows": args.windows,
        "targets": TARGETS,
        "split_info": [info for _, _, info in splits.values()],
        "chunk_inventory": str(args.out_dir / "chunk_inventory.csv"),
        "metrics_path": str(args.out_dir / f"{prefix}_metrics.csv"),
        "comparison_path": str(args.out_dir / f"{prefix}_comparison.csv"),
        "subgroup_path": str(args.out_dir / f"{prefix}_subgroup.csv"),
        "uncertainty_path": str(args.out_dir / f"{prefix}_uncertainty.csv"),
        "feature_dir": str(args.feature_dir),
        "figure_path": str(args.figure),
    }
    (args.out_dir / f"{prefix}_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    write_stream_summary(args.summary, summary, comparisons)
    return summary


def write_stream_summary(path: Path, summary: dict[str, Any], comparisons: list[dict[str, Any]]) -> None:
    comp = pd.DataFrame(comparisons).sort_values(["holdout", "target", "early_seconds"])
    lines = [
        f"# {summary['dataset']} AQ2009GM full-manifest chunk-streaming validation",
        "",
        "This validation streams every chunk listed in the local SeisBench AQ2009GM chunk manifest. Raw HDF5 and metadata files may be deleted after feature extraction when `--delete-raw` is used; the retained evidence is the compact feature table and generated metrics.",
        "",
        f"- chunks: {summary['chunk_count']}",
        f"- metadata rows: {summary['metadata_all_rows']}",
        f"- valid records: {summary['valid_rows']}",
        f"- events: {summary['valid_events']}",
        f"- stations: {summary['valid_stations']}",
        "",
        "## Splits",
        "",
        "| Holdout | Eligible rows | Eligible groups | Train rows | Test rows | Train groups | Test groups | Overlap |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for info in summary["split_info"]:
        lines.append(
            f"| {info['holdout']} | {info['eligible_rows']} | {info['eligible_groups']} | "
            f"{info['train_rows_selected']} | {info['test_rows_selected']} | "
            f"{info['train_groups']} | {info['test_groups']} | {info['group_overlap']} |"
        )
    lines.extend(
        [
            "",
            "## Metadata + early velocity",
            "",
            "| Holdout | Target | Window | Metadata MAE | Combined MAE | MAE reduction | Metadata R2 | Combined R2 |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in comp.iterrows():
        lines.append(
            f"| {row['holdout']} | {row['target'].upper()} | {row['early_seconds']:.0f}s | "
            f"{row['metadata_mae_log10_target']:.3f} | {row['combined_mae_log10_target']:.3f} | "
            f"{row['mae_reduction_pct']:.1f}% | {row['metadata_r2']:.3f} | {row['combined_r2']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Extra analysis files",
            "",
            f"- subgroup: `{summary['subgroup_path']}`",
            f"- uncertainty: `{summary['uncertainty_path']}`",
            f"- chunk inventory: `{summary['chunk_inventory']}`",
            f"- figure: `{summary['figure_path']}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n")


def write_inventory(path: Path, rows: list[dict[str, Any]]) -> None:
    slim = [{k: v for k, v in row.items() if k != "data_format"} for row in rows]
    if not slim:
        path.write_text("")
        return
    fieldnames = sorted({key for row in slim for key in row})
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(slim)


def summarize_cached_feature(path: Path, chunk: str) -> dict[str, Any]:
    df = pd.read_csv(path, usecols=["row_id", "source_id", "station_group", "early_seconds"], low_memory=False)
    first_window = df["early_seconds"].min()
    one = df[df["early_seconds"].eq(first_window)]
    return {
        "chunk": chunk,
        "status": "cached",
        "metadata_all_rows": 0,
        "valid_rows": int(one["row_id"].nunique()),
        "feature_rows": int(len(df)),
        "valid_events": int(one["source_id"].nunique()),
        "valid_stations": int(one["station_group"].nunique()),
        "errors": 0,
        "feature_path": str(path),
    }


def read_inventory(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    number_cols = {"metadata_all_rows", "valid_rows", "feature_rows", "valid_events", "valid_stations", "errors"}
    out: dict[str, dict[str, Any]] = {}
    with path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            chunk = row.get("chunk")
            if not chunk:
                continue
            for col in number_cols:
                if row.get(col) not in (None, ""):
                    row[col] = int(row[col])
            out[chunk] = row
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", type=Path, default=Path.home() / ".seisbench/datasets/aq2009gm")
    parser.add_argument("--chunks-file", type=Path, default=Path.home() / ".seisbench/datasets/aq2009gm/chunks")
    parser.add_argument("--chunks", nargs="+")
    parser.add_argument("--max-chunks", type=int)
    parser.add_argument("--out-dir", type=Path, default=Path("work/aq2009gm_full_stream_validation"))
    parser.add_argument("--feature-dir", type=Path, default=Path("work/aq2009gm_full_stream_validation/features"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/aq2009gm_full_stream_validation_summary.md"))
    parser.add_argument("--figure", type=Path, default=Path("outputs/figures/ground_motion_audit/aq2009gm_full_stream_panel.png"))
    parser.add_argument("--windows", nargs="+", type=float, default=[1.0, 3.0, 10.0])
    parser.add_argument("--train-size", type=int, default=30000)
    parser.add_argument("--test-size", type=int, default=10000)
    parser.add_argument("--station-test-groups", type=int, default=20)
    parser.add_argument("--seed", type=int, default=43)
    parser.add_argument("--download-retries", type=int, default=5)
    parser.add_argument("--retry-sleep-sec", type=float, default=30.0)
    parser.add_argument("--delete-raw", action="store_true")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.feature_dir.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.figure.parent.mkdir(parents=True, exist_ok=True)

    chunks = args.chunks or read_chunks(args.chunks_file)
    if args.max_chunks:
        chunks = chunks[: args.max_chunks]

    reports: list[dict[str, Any]] = []
    inventory_path = args.out_dir / "chunk_inventory.csv"
    previous_reports = read_inventory(inventory_path)
    for i, chunk in enumerate(chunks, start=1):
        feature_path = args.feature_dir / f"aq2009gm_chunk{chunk}_features.csv.gz"
        if feature_path.exists():
            report = previous_reports.get(chunk) or summarize_cached_feature(feature_path, chunk)
            report["status"] = "cached"
            if args.delete_raw:
                cleanup_raw(args.cache_dir, chunk)
        else:
            print(f"[{i}/{len(chunks)}] download {chunk}", flush=True)
            download_chunk(args.cache_dir, chunk, args.download_retries, args.retry_sleep_sec)
            print(f"[{i}/{len(chunks)}] extract {chunk}", flush=True)
            report = extract_chunk(args.cache_dir, chunk, args.windows, args.feature_dir)
            report["status"] = "extracted"
            if args.delete_raw:
                cleanup_raw(args.cache_dir, chunk)
        reports.append(report)
        write_inventory(inventory_path, reports)
        print(json.dumps({k: report.get(k) for k in ["chunk", "status", "valid_rows", "errors"]}, ensure_ascii=False), flush=True)

    features = load_stream_features(args.feature_dir)
    summary = evaluate(features, args, chunks, reports)
    if args.delete_raw:
        for chunk in read_chunks(args.chunks_file):
            cleanup_raw(args.cache_dir, chunk)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
