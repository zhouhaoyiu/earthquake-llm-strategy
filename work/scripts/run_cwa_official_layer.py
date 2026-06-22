#!/usr/bin/env python3
"""Download one CWA year, run an official PGA/PGV early-window check, then clean raw files."""

from __future__ import annotations

import argparse
import json
import math
import os
import tarfile
from pathlib import Path
from typing import Any

import h5py
import matplotlib
import numpy as np
import pandas as pd

from run_aq2009gm_chunk_baseline import (
    compare_results,
    split_by_group,
    to_float,
    train_eval,
    waveform_feature_cols,
    waveform_features,
    write_csv,
)

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


TARGETS = {"pga": "trace_pga_cmps2", "pgv": "trace_pgv_cmps"}
METADATA_FEATURES = [
    "source_magnitude",
    "source_depth_km",
    "path_ep_distance_km",
    "path_hyp_distance_km",
    "station_elevation_m",
    "trace_sampling_rate_hz",
    "trace_npts",
]
TAR_BY_YEAR = {
    **{year: "merge2011_2014.tar.gz" for year in range(2011, 2015)},
    **{year: "merge2015_2018.tar.gz" for year in range(2015, 2019)},
    **{year: "merge2019_2021.tar.gz" for year in range(2019, 2022)},
}


def download_tar(raw_dir: Path, year: int) -> Path:
    from huggingface_hub import hf_hub_download

    raw_dir.mkdir(parents=True, exist_ok=True)
    filename = TAR_BY_YEAR[year]
    existing = raw_dir / filename
    if existing.exists() and existing.stat().st_size > 0:
        return existing
    return Path(
        hf_hub_download(
            "NLPLabNTUST/Merged-CWA",
            filename,
            repo_type="dataset",
            local_dir=raw_dir,
        )
    )


def extract_year(tar_path: Path, cache_dir: Path, year: int) -> list[Path]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    wanted = {f"metadata_{year}.csv", f"waveforms_{year}.hdf5"}
    existing = [cache_dir / name for name in sorted(wanted)]
    if all(path.exists() and path.stat().st_size > 0 for path in existing):
        return existing
    extracted: list[Path] = []
    with tarfile.open(tar_path, "r:gz") as tar:
        members = [m for m in tar.getmembers() if Path(m.name).name in wanted]
        found = {Path(m.name).name for m in members}
        if found != wanted:
            raise FileNotFoundError(f"{tar_path} missing {sorted(wanted - found)}")
        for member in members:
            member.name = Path(member.name).name
            tar.extract(member, cache_dir)
            extracted.append(cache_dir / member.name)
    metadata_path = cache_dir / f"metadata_{year}.csv"
    metadata = pd.read_csv(metadata_path)
    if "split" not in metadata.columns:
        metadata["split"] = "train" if year <= 2018 else "dev" if year == 2019 else "test"
        metadata.to_csv(metadata_path, index=False)
    return extracted


def cleanup(cache_dir: Path, raw_dir: Path, year: int, remove_tar: bool) -> None:
    for path in [
        cache_dir / f"metadata_{year}.csv",
        cache_dir / f"metadata_{year}.csv.partial",
        cache_dir / f"waveforms_{year}.hdf5",
        cache_dir / f"waveforms_{year}.hdf5.partial",
        cache_dir / "waveforms_2021.hdf5.partial",
    ]:
        path.unlink(missing_ok=True)
    if remove_tar:
        for tar_name in set(TAR_BY_YEAR.values()):
            (raw_dir / tar_name).unlink(missing_ok=True)


def as_cw(waveform: np.ndarray) -> np.ndarray:
    arr = np.asarray(waveform, dtype=np.float32)
    if arr.ndim != 2:
        raise ValueError(f"expected 2-D waveform, got {arr.shape}")
    if arr.shape[0] <= 4:
        return arr
    if arr.shape[1] <= 4:
        return arr.T
    raise ValueError(f"can not infer component axis for {arr.shape}")


def read_data_format(h5: h5py.File) -> dict[str, str]:
    out: dict[str, str] = {}
    for key in ["component_order", "dimension_order", "measurement", "unit"]:
        value = h5[f"data_format/{key}"][()]
        out[key] = value.decode() if isinstance(value, bytes) else str(value)
    return out


def valid_metadata(cache_dir: Path, year: int) -> pd.DataFrame:
    df = pd.read_csv(cache_dir / f"metadata_{year}.csv", low_memory=False)
    df["row_id"] = np.arange(len(df))
    df["trace_chunk"] = f"_{year}"
    df["source_id"] = df["source_event_id"].fillna("").astype(str)
    df["station_group"] = (
        df["station_network_code"].fillna("").astype(str) + "." + df["station_code"].fillna("").astype(str)
    )
    depth = pd.to_numeric(df["source_depth_km"], errors="coerce")
    ep = pd.to_numeric(df["path_ep_distance_km"], errors="coerce")
    df["path_hyp_distance_km"] = np.sqrt(depth * depth + ep * ep)
    mask = df["trace_category"].eq("earthquake")
    mask &= df["trace_name"].notna()
    mask &= pd.to_numeric(df["trace_p_arrival_sample"], errors="coerce").notna()
    mask &= pd.to_numeric(df["trace_npts"], errors="coerce").gt(0)
    for col in TARGETS.values():
        mask &= pd.to_numeric(df[col], errors="coerce").gt(0)
    return df[mask].copy()


def build_features(cache_dir: Path, year: int, metadata: pd.DataFrame, windows: list[float], max_rows: int) -> tuple[pd.DataFrame, dict[str, str], list[dict[str, Any]]]:
    if max_rows and len(metadata) > max_rows:
        metadata = metadata.sample(max_rows, random_state=17).sort_values("row_id")
    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    with h5py.File(cache_dir / f"waveforms_{year}.hdf5", "r") as h5:
        data_format = read_data_format(h5)
        data = h5["data"]
        for _, row in metadata.iterrows():
            try:
                arr = as_cw(data[str(row["trace_name"])][()])
            except Exception as exc:
                errors.append({"row_id": int(row["row_id"]), "trace_name": row.get("trace_name", ""), "error": repr(exc)})
                continue

            base = {
                "row_id": int(row["row_id"]),
                "source_id": row.get("source_id", ""),
                "station_group": row.get("station_group", ""),
                "source_origin_time": row.get("source_origin_time", ""),
                "trace_start_time": row.get("trace_start_time", ""),
                "source_magnitude": to_float(row.get("source_magnitude")),
                "source_depth_km": to_float(row.get("source_depth_km")),
                "path_ep_distance_km": to_float(row.get("path_ep_distance_km")),
                "path_hyp_distance_km": to_float(row.get("path_hyp_distance_km")),
                "station_elevation_m": to_float(row.get("station_elevation_m")),
                "trace_sampling_rate_hz": to_float(row.get("trace_sampling_rate_hz")),
                "trace_npts": to_float(row.get("trace_npts")),
            }
            for target, col in TARGETS.items():
                value = to_float(row.get(col))
                base[f"target_{target}"] = value
                base[f"target_log10_{target}"] = math.log10(value) if value and value > 0 else np.nan
            for seconds in windows:
                rec = dict(base)
                rec.update(waveform_features(arr, row, seconds))
                records.append(rec)
    return pd.DataFrame(records), data_format, errors


def write_summary(
    path: Path,
    args: argparse.Namespace,
    metadata: pd.DataFrame,
    features: pd.DataFrame,
    data_format: dict[str, str],
    comparisons: list[dict[str, Any]],
    errors: list[dict[str, Any]],
) -> None:
    comp = pd.DataFrame(comparisons).sort_values(["holdout", "target", "early_seconds"])
    lines = [
        "# CWA official PGA/PGV independent layer",
        "",
        "## Scope",
        "",
        f"- Source: SeisBench CWA benchmark, year {args.year}.",
        f"- Eligible official PGA/PGV records: {len(metadata):,}.",
        f"- Feature rows: {len(features):,}.",
        f"- Events: {metadata['source_id'].nunique():,}.",
        f"- Stations: {metadata['station_group'].nunique():,}.",
        "- Targets: `trace_pga_cmps2` and `trace_pgv_cmps` from CWA metadata.",
        f"- HDF5 format: measurement={data_format.get('measurement')}, unit={data_format.get('unit')}, component_order={data_format.get('component_order')}.",
        "- Raw CWA metadata/HDF5 and downloaded tar are deleted after the run when `--cleanup-raw` is used.",
        "",
        "## Metadata + early waveform vs metadata-only",
        "",
        "| Holdout | Target | Window | Metadata MAE | Combined MAE | MAE reduction | Metadata R2 | Combined R2 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in comp.iterrows():
        lines.append(
            f"| {row['holdout']} | {row['target'].upper()} | {row['early_seconds']:.0f}s | "
            f"{row['metadata_mae_log10_target']:.3f} | {row['combined_mae_log10_target']:.3f} | "
            f"{row['mae_reduction_pct']:.1f}% | {row['metadata_r2']:.3f} | {row['combined_r2']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Evidence boundary",
            "",
            "This is an official CWA PGA/PGV metadata-target layer from real waveforms. It supports an independent Taiwan check for early-window information.",
            "It is a one-year CWA layer, not a full 2011-2021 CWA benchmark.",
            f"Waveform read errors: {len(errors):,}.",
            "",
            "## Files",
            "",
            f"- Comparison: `{args.out_dir / 'cwa_official_comparison.csv'}`",
            f"- Metrics: `{args.out_dir / 'cwa_official_metrics.csv'}`",
            f"- Features: `{args.out_dir / 'cwa_official_features.csv.gz'}`",
            f"- Figure: `{args.figure}`",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def plot_cwa_comparison(comparisons: list[dict[str, Any]], out: Path, title: str) -> None:
    df = pd.DataFrame(comparisons)
    windows = sorted(df["early_seconds"].dropna().unique())
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    colors = {"event": "#2f6f9f", "station": "#b25d2a"}
    markers = {"event": "o", "station": "s"}
    for ax, target in zip(axes, ["pga", "pgv"], strict=True):
        for holdout in ["event", "station"]:
            sub = df[(df["target"].eq(target)) & (df["holdout"].eq(holdout))].sort_values("early_seconds")
            ax.plot(
                sub["early_seconds"],
                sub["mae_reduction_pct"],
                marker=markers[holdout],
                linewidth=2.2,
                color=colors[holdout],
                label=f"held-{holdout}",
            )
        ax.axhline(0, color="#666666", linewidth=0.8)
        ax.set_title(target.upper())
        ax.set_xlabel("Post-P window (s)")
        ax.set_xticks(windows)
        ax.grid(True, axis="y", alpha=0.25)
    axes[0].set_ylabel("MAE reduction vs metadata-only (%)")
    axes[1].legend(frameon=False, loc="upper left")
    fig.suptitle(title, y=1.02)
    fig.tight_layout()
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2011)
    parser.add_argument("--raw-dir", type=Path, default=Path("work/cwa_raw"))
    parser.add_argument("--cache-dir", type=Path, default=Path.home() / ".seisbench/datasets/cwa")
    parser.add_argument("--out-dir", type=Path, default=Path("work/cwa_official_layer"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/cwa_official_pga_pgv_summary.md"))
    parser.add_argument("--figure", type=Path, default=Path("outputs/figures/ground_motion_audit/cwa_official_pga_pgv_panel.png"))
    parser.add_argument("--windows", nargs="+", type=float, default=[2.0, 5.0])
    parser.add_argument("--max-rows", type=int, default=30000)
    parser.add_argument("--train-size", type=int, default=12000)
    parser.add_argument("--test-size", type=int, default=3000)
    parser.add_argument("--station-test-groups", type=int, default=20)
    parser.add_argument("--cleanup-raw", action="store_true")
    args = parser.parse_args()

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.figure.parent.mkdir(parents=True, exist_ok=True)

    tar_path = download_tar(args.raw_dir, args.year)
    extract_year(tar_path, args.cache_dir, args.year)
    metadata = valid_metadata(args.cache_dir, args.year)
    features, data_format, errors = build_features(args.cache_dir, args.year, metadata, args.windows, args.max_rows)
    features.to_csv(args.out_dir / "cwa_official_features.csv.gz", index=False)

    split_meta = features[features["early_seconds"].eq(float(args.windows[0]))].drop_duplicates("row_id")
    split_masks = {}
    split_infos = []
    for holdout in ["event", "station"]:
        train_ids, test_ids, info = split_by_group(
            split_meta,
            dataset=f"cwa_{args.year}",
            holdout=holdout,
            train_size=args.train_size,
            test_size=args.test_size,
            station_test_groups=args.station_test_groups,
            seed=17 + (101 if holdout == "station" else 0),
        )
        split_masks[holdout] = (train_ids, test_ids, info)
        split_infos.append(info)

    results: list[dict[str, Any]] = []
    for holdout, (train_ids, test_ids, info) in split_masks.items():
        for seconds in args.windows:
            sub = features[features["early_seconds"].eq(float(seconds))]
            train = sub[sub["row_id"].isin(train_ids)]
            test = sub[sub["row_id"].isin(test_ids)]
            meta_cols = [col for col in METADATA_FEATURES if col in sub.columns]
            wave_cols = waveform_feature_cols(sub)
            for target in TARGETS:
                for feature_set, cols in {
                    "metadata_only": meta_cols,
                    "metadata_plus_early_velocity": meta_cols + wave_cols,
                }.items():
                    results.append(train_eval(train, test, cols, feature_set, holdout, target, seconds, info, f"cwa_{args.year}"))

    comparisons = compare_results(results)
    write_csv(args.out_dir / "cwa_official_metrics.csv", results)
    write_csv(args.out_dir / "cwa_official_comparison.csv", comparisons)
    write_csv(args.out_dir / "cwa_official_split_info.csv", split_infos)
    write_csv(args.out_dir / "cwa_official_waveform_errors.csv", errors)
    plot_cwa_comparison(comparisons, args.figure, f"CWA {args.year} official PGA/PGV early waveform information")
    (args.out_dir / "cwa_official_summary.json").write_text(
        json.dumps(
            {
                "year": args.year,
                "eligible_records": int(len(metadata)),
                "feature_rows": int(len(features)),
                "events": int(metadata["source_id"].nunique()),
                "stations": int(metadata["station_group"].nunique()),
                "data_format": data_format,
                "windows": args.windows,
                "cleanup_raw": bool(args.cleanup_raw),
                "summary": str(args.summary),
                "figure": str(args.figure),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    write_summary(args.summary, args, metadata, features, data_format, comparisons, errors)
    if args.cleanup_raw:
        cleanup(args.cache_dir, args.raw_dir, args.year, remove_tar=True)
    print(args.summary)


if __name__ == "__main__":
    main()
