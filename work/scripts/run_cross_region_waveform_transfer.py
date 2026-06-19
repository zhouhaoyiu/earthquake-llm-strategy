#!/usr/bin/env python3
"""Cross-region early-waveform transfer checks from compact feature tables."""

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
import matplotlib
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline


matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


WAVEFORM_COLS = [
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

TARGETS = ["pga", "pgv"]


def finite_target(df: pd.DataFrame, target: str) -> pd.DataFrame:
    col = f"target_log10_{target}"
    if col not in df.columns:
        return df.iloc[:0].copy()
    out = df[pd.to_numeric(df[col], errors="coerce").notna()].copy()
    out[col] = out[col].astype(float)
    return out


def add_log_waveform_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in WAVEFORM_COLS:
        if col in out.columns:
            values = pd.to_numeric(out[col], errors="coerce").astype(float)
            out[f"log10_{col}"] = np.log10(np.maximum(np.abs(values), 0.0) + 1e-12)
    return out


def load_table(path: Path, dataset: str, early_seconds: float) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    if "early_seconds" in df.columns:
        df = df[df["early_seconds"].astype(float).eq(float(early_seconds))].copy()
    df["dataset"] = dataset
    return add_log_waveform_features(df)


def split_aq_by_event(df: pd.DataFrame, train_size: int, test_size: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    work = df.copy()
    work["_group"] = work["source_id"].fillna("").astype(str)
    work = work[work["_group"].ne("")].copy()
    group_sizes = work["_group"].value_counts()
    groups = np.array(group_sizes.index.tolist(), dtype=object)
    rng = np.random.default_rng(seed)
    rng.shuffle(groups)

    test_groups: list[str] = []
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
        raise RuntimeError(f"AQ held-event split overlap: {sorted(overlap)[:3]}")
    info = {
        "dataset": "aq2009gm",
        "split": "held_event",
        "eligible_rows": int(len(work)),
        "eligible_groups": int(work["_group"].nunique()),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_groups": int(train["_group"].nunique()),
        "test_groups": int(test["_group"].nunique()),
        "group_overlap": int(len(overlap)),
    }
    return train.drop(columns=["_group"]), test.drop(columns=["_group"]), info


def load_aq(feature_dir: Path, early_seconds: float, train_size: int, test_size: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    files = sorted(feature_dir.glob("aq2009gm_chunk*_features.csv.gz"))
    if not files:
        raise FileNotFoundError(f"no AQ feature tables under {feature_dir}")
    keep = {
        "row_id",
        "source_id",
        "station_group",
        "early_seconds",
        "target_log10_pga",
        "target_log10_pgv",
        *WAVEFORM_COLS,
    }
    frames = []
    for path in files:
        chunk = pd.read_csv(path, usecols=lambda col: col in keep, low_memory=False)
        chunk = chunk[chunk["early_seconds"].astype(float).eq(float(early_seconds))]
        if not chunk.empty:
            chunk["dataset"] = "aq2009gm"
            frames.append(chunk)
    if not frames:
        raise RuntimeError("AQ feature tables do not contain the requested early window")
    aq = add_log_waveform_features(pd.concat(frames, ignore_index=True).drop_duplicates("row_id"))
    return split_aq_by_event(aq, train_size=train_size, test_size=test_size, seed=seed)


def split_esm_by_station(
    df: pd.DataFrame,
    train_size: int,
    test_size: int,
    station_test_groups: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    work = df.copy()
    work["_group"] = work["station_group"].fillna("").astype(str)
    work = work[work["_group"].ne("")].copy()
    group_sizes = work["_group"].value_counts()
    groups = np.array(group_sizes.index.tolist(), dtype=object)
    rng = np.random.default_rng(seed)
    rng.shuffle(groups)
    test_groups = [str(group) for group in groups[: min(station_test_groups, len(groups))]]
    test_set = set(test_groups)
    train = work[~work["_group"].isin(test_set)].copy()
    test = work[work["_group"].isin(test_set)].copy()
    if len(train) > train_size:
        train = train.sample(train_size, random_state=seed + 11)
    if len(test) > test_size:
        test = test.sample(test_size, random_state=seed + 17)
    overlap = set(train["_group"]).intersection(set(test["_group"]))
    if overlap:
        raise RuntimeError(f"ESM held-station split overlap: {sorted(overlap)[:3]}")
    info = {
        "dataset": "esm",
        "split": "held_station",
        "eligible_rows": int(len(work)),
        "eligible_groups": int(work["_group"].nunique()),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_groups": int(train["_group"].nunique()),
        "test_groups": int(test["_group"].nunique()),
        "group_overlap": int(len(overlap)),
    }
    return train.drop(columns=["_group"]), test.drop(columns=["_group"]), info


def load_esm(
    path: Path,
    early_seconds: float,
    train_size: int,
    test_size: int,
    station_test_groups: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    df = pd.read_csv(path, low_memory=False)
    df = df[df["early_seconds"].astype(float).eq(float(early_seconds))].copy()
    if df.empty:
        raise RuntimeError("ESM feature table does not contain the requested early window")
    df["dataset"] = "esm"
    df = add_log_waveform_features(df)
    return split_esm_by_station(
        df,
        train_size=train_size,
        test_size=test_size,
        station_test_groups=station_test_groups,
        seed=seed,
    )


def fit_model(train: pd.DataFrame, features: list[str], target_col: str) -> Any:
    model = HistGradientBoostingRegressor(
        max_iter=200,
        learning_rate=0.05,
        max_leaf_nodes=31,
        random_state=17,
        l2_regularization=0.01,
    )
    pipe = make_pipeline(SimpleImputer(strategy="median"), model)
    pipe.fit(train[features], train[target_col].astype(float))
    return pipe


def score(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    err = y - pred
    return {
        "mae_log10_target": float(mean_absolute_error(y, pred)),
        "rmse_log10_target": float(mean_squared_error(y, pred) ** 0.5),
        "r2_log10_target": float(r2_score(y, pred)),
        "mean_error": float(np.mean(err)),
        "median_error": float(np.median(err)),
        "q90_abs_error": float(np.nanquantile(np.abs(err), 0.9)),
        "q95_abs_error": float(np.nanquantile(np.abs(err), 0.95)),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def station_group(df: pd.DataFrame) -> pd.Series:
    if {"station_network_code", "station_code"}.issubset(df.columns):
        return df["station_network_code"].fillna("").astype(str) + "." + df["station_code"].fillna("").astype(str)
    if "station_group" in df.columns:
        return df["station_group"].fillna("").astype(str)
    return df.get("station_code", pd.Series([""] * len(df), index=df.index)).fillna("").astype(str)


def summarize(
    rows: list[dict[str, Any]],
    split_info: list[dict[str, Any]],
    path: Path,
    figure_path: Path,
    boundary_path: Path,
) -> None:
    df = pd.DataFrame([row for row in rows if not row.get("skipped")])
    lines = [
        "# Cross-region early-waveform transfer",
        "",
        "This check uses compact public-dataset feature tables only. Models use early waveform features, not source distance, site terms, event id, or station id.",
        "",
        "Splits:",
        "",
        "| Dataset | Split | Train rows | Test rows | Train groups | Test groups | Group overlap |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in split_info:
        lines.append(
            f"| {row['dataset']} | {row['split']} | {row['train_rows']} | {row['test_rows']} | "
            f"{row['train_groups']} | {row['test_groups']} | {row['group_overlap']} |"
        )

    if not df.empty:
        within = df[df["source_dataset"].eq(df["test_dataset"])].copy()
        keys = ["target", "test_dataset", "feature_set", "calibration"]
        within = within.set_index(keys)["mae_log10_target"].to_dict()
        df["mae_ratio_vs_within_target"] = [
            row.mae_log10_target / within.get((row.target, row.test_dataset, row.feature_set, row.calibration), math.nan)
            for row in df.itertuples(index=False)
        ]

        transfer = df[df["source_dataset"].ne(df["test_dataset"])].copy()
        boundary_path.parent.mkdir(parents=True, exist_ok=True)
        transfer.to_csv(boundary_path, index=False)

        lines.extend(
            [
                "",
                "Best cross-region rows by target/test domain:",
                "",
                "| Target | Test domain | Calibration | Feature set | Source domain | MAE | R2 | MAE ratio vs within target |",
                "|---|---|---|---|---|---:|---:|---:|",
            ]
        )
        best = (
            transfer.sort_values("mae_log10_target")
            .groupby(["target", "test_dataset", "calibration"], as_index=False)
            .head(1)
            .sort_values(["target", "test_dataset", "calibration"])
        )
        for row in best.itertuples(index=False):
            lines.append(
                f"| {row.target.upper()} | {row.test_dataset} | {row.calibration} | {row.feature_set} | "
                f"{row.source_dataset} | {row.mae_log10_target:.3f} | {row.r2_log10_target:.3f} | "
                f"{row.mae_ratio_vs_within_target:.2f} |"
            )

        lines.extend(
            [
                "",
                "Boundary interpretation:",
            ]
        )
        direct = transfer[transfer["calibration"].eq("source_only")]
        calibrated = transfer[transfer["calibration"].eq("target_offset_calibrated")]
        if not direct.empty:
            lines.append(
                f"- Zero-shot transfer median MAE ratio vs target-domain training: {direct['mae_ratio_vs_within_target'].median():.2f}."
            )
        if not calibrated.empty:
            lines.append(
                f"- Target-train offset calibration median MAE ratio vs target-domain training: {calibrated['mae_ratio_vs_within_target'].median():.2f}."
            )
        lines.append(
            "- Treat large cross-domain penalties as evidence for a predictability boundary and unit/measurement harmonization need, not as a failed main result."
        )
        lines.extend(
            [
                "",
                "Files:",
                f"- `{boundary_path.parent / 'cross_region_waveform_transfer_metrics.csv'}`",
                f"- `{boundary_path}`",
                f"- `{figure_path}`",
            ]
        )

    path.write_text("\n".join(lines) + "\n")


def plot_boundary(rows: list[dict[str, Any]], path: Path) -> None:
    df = pd.DataFrame([row for row in rows if not row.get("skipped")])
    if df.empty:
        return
    within = df[df["source_dataset"].eq(df["test_dataset"])].copy()
    keys = ["target", "test_dataset", "feature_set", "calibration"]
    within_mae = within.set_index(keys)["mae_log10_target"].to_dict()
    df["mae_ratio_vs_within_target"] = [
        row.mae_log10_target / within_mae.get((row.target, row.test_dataset, row.feature_set, row.calibration), math.nan)
        for row in df.itertuples(index=False)
    ]
    transfer = df[df["source_dataset"].ne(df["test_dataset"])].copy()
    if transfer.empty:
        return
    best = (
        transfer.sort_values("mae_log10_target")
        .groupby(["target", "test_dataset", "calibration"], as_index=False)
        .head(1)
        .sort_values(["target", "test_dataset", "calibration"])
    )
    labels = []
    for target, test_dataset in best[["target", "test_dataset"]].drop_duplicates().itertuples(index=False):
        labels.append((target, test_dataset))

    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    x = np.arange(len(labels))
    width = 0.36
    colors = {"source_only": "#b65f2a", "target_offset_calibrated": "#31688e"}
    names = {"source_only": "zero-shot", "target_offset_calibrated": "offset calibrated"}
    for offset_idx, cal in enumerate(["source_only", "target_offset_calibrated"]):
        vals = []
        sources = []
        for target, test_dataset in labels:
            sub = best[
                best["target"].eq(target) & best["test_dataset"].eq(test_dataset) & best["calibration"].eq(cal)
            ]
            if sub.empty:
                vals.append(np.nan)
                sources.append("")
            else:
                row = sub.iloc[0]
                vals.append(float(row["mae_ratio_vs_within_target"]))
                sources.append(str(row["source_dataset"]))
        pos = x + (offset_idx - 0.5) * width
        bars = ax.bar(pos, vals, width=width, color=colors[cal], label=names[cal])
        for bar, source in zip(bars, sources):
            if not source:
                continue
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.08,
                source.replace("aq2009gm", "AQ"),
                ha="center",
                va="bottom",
                fontsize=8,
                rotation=90,
            )
    ax.axhline(1.0, color="#222222", linewidth=1.0, linestyle="--")
    ax.text(-0.55, 1.05, "target-domain training", fontsize=9, va="bottom")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{target.upper()} -> {test.upper()}" for target, test in labels], rotation=25, ha="right")
    ax.set_ylabel("MAE ratio vs target-domain model")
    ax.set_title("Cross-region early-waveform transfer boundary", loc="left", fontsize=12)
    ax.set_ylim(0, max(5.6, float(np.nanmax(best["mae_ratio_vs_within_target"])) + 0.9))
    ax.legend(frameon=False, ncol=2, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8, alpha=0.8)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--balanced-dir", type=Path, default=Path("work/ground_motion_balanced_station_10s"))
    parser.add_argument("--aq-feature-dir", type=Path, default=Path("work/aq2009gm_full_stream_validation/features"))
    parser.add_argument("--esm-features", type=Path, default=Path("work/esm_compact_features_full/esm_compact_features.csv.gz"))
    parser.add_argument("--out-dir", type=Path, default=Path("work/cross_region_waveform_transfer"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/cross_region_waveform_transfer_summary.md"))
    parser.add_argument("--figure", type=Path, default=Path("outputs/figures/ground_motion_audit/cross_region_waveform_transfer_boundary.png"))
    parser.add_argument("--early-seconds", type=float, default=10.0)
    parser.add_argument("--aq-train-size", type=int, default=30000)
    parser.add_argument("--aq-test-size", type=int, default=10000)
    parser.add_argument("--esm-train-size", type=int, default=20000)
    parser.add_argument("--esm-test-size", type=int, default=6000)
    parser.add_argument("--esm-station-test-groups", type=int, default=200)
    parser.add_argument("--seed", type=int, default=59)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)

    datasets: dict[str, dict[str, pd.DataFrame]] = {
        "instancegm": {
            "train": load_table(args.balanced_dir / "instancegm_held_station_train_features.csv", "instancegm", args.early_seconds),
            "test": load_table(args.balanced_dir / "instancegm_held_station_test_features.csv", "instancegm", args.early_seconds),
        },
        "knet": {
            "train": load_table(args.balanced_dir / "knet_held_station_train_features.csv", "knet", args.early_seconds),
            "test": load_table(args.balanced_dir / "knet_held_station_test_features.csv", "knet", args.early_seconds),
        },
    }
    aq_info: dict[str, Any] | None = None
    try:
        aq_train, aq_test, aq_info = load_aq(args.aq_feature_dir, args.early_seconds, args.aq_train_size, args.aq_test_size, args.seed)
        datasets["aq2009gm"] = {"train": aq_train, "test": aq_test}
    except RuntimeError as exc:
        if "requested early window" not in str(exc):
            raise
    esm_info: dict[str, Any] | None = None
    if args.esm_features.exists():
        esm_train, esm_test, esm_info = load_esm(
            args.esm_features,
            args.early_seconds,
            train_size=args.esm_train_size,
            test_size=args.esm_test_size,
            station_test_groups=args.esm_station_test_groups,
            seed=args.seed + 503,
        )
        datasets["esm"] = {"train": esm_train, "test": esm_test}

    split_info = [
        {
            "dataset": "instancegm",
            "split": "balanced_held_station",
            "train_rows": int(len(datasets["instancegm"]["train"])),
            "test_rows": int(len(datasets["instancegm"]["test"])),
            "train_groups": int(station_group(datasets["instancegm"]["train"]).nunique()),
            "test_groups": int(station_group(datasets["instancegm"]["test"]).nunique()),
            "group_overlap": int(
                len(
                    set(station_group(datasets["instancegm"]["train"]))
                    & set(station_group(datasets["instancegm"]["test"]))
                )
            ),
        },
        {
            "dataset": "knet",
            "split": "balanced_held_station",
            "train_rows": int(len(datasets["knet"]["train"])),
            "test_rows": int(len(datasets["knet"]["test"])),
            "train_groups": int(station_group(datasets["knet"]["train"]).nunique()),
            "test_groups": int(station_group(datasets["knet"]["test"]).nunique()),
            "group_overlap": int(
                len(
                    set(station_group(datasets["knet"]["train"]))
                    & set(station_group(datasets["knet"]["test"]))
                )
            ),
        },
    ]
    if aq_info is not None:
        split_info.append(aq_info)
    if esm_info is not None:
        split_info.append(esm_info)

    feature_sets = {
        "raw_waveform": [col for col in WAVEFORM_COLS if all(col in part for data in datasets.values() for part in data.values())],
        "log_waveform": [
            f"log10_{col}" for col in WAVEFORM_COLS if all(f"log10_{col}" in part for data in datasets.values() for part in data.values())
        ],
    }

    rows: list[dict[str, Any]] = []
    for target in TARGETS:
        target_col = f"target_log10_{target}"
        for source_name, source in datasets.items():
            source_train = finite_target(source["train"], target)
            if source_train.empty:
                continue
            for feature_set, cols in feature_sets.items():
                if not cols:
                    continue
                print(f"[fit] source={source_name} target={target} features={feature_set}", flush=True)
                model = fit_model(source_train, cols, target_col)
                for test_name, test_data in datasets.items():
                    target_train = finite_target(test_data["train"], target)
                    target_test = finite_target(test_data["test"], target)
                    if target_train.empty or target_test.empty:
                        rows.append(
                            {
                                "source_dataset": source_name,
                                "test_dataset": test_name,
                                "target": target,
                                "feature_set": feature_set,
                                "calibration": "skipped",
                                "train_rows": int(len(source_train)),
                                "calibration_rows": int(len(target_train)),
                                "test_rows": int(len(target_test)),
                                "skipped": True,
                            }
                        )
                        continue

                    y_test = target_test[target_col].astype(float).to_numpy()
                    raw_pred = model.predict(target_test[cols])
                    cal_pred_train = model.predict(target_train[cols])
                    offset = float(np.median(target_train[target_col].astype(float).to_numpy() - cal_pred_train))
                    common = {
                        "source_dataset": source_name,
                        "test_dataset": test_name,
                        "target": target,
                        "feature_set": feature_set,
                        "train_rows": int(len(source_train)),
                        "calibration_rows": int(len(target_train)),
                        "test_rows": int(len(target_test)),
                        "source_train_target_median": float(source_train[target_col].median()),
                        "target_calibration_median": float(target_train[target_col].median()),
                        "target_test_median": float(target_test[target_col].median()),
                        "target_offset_log10": offset,
                        "early_seconds": float(args.early_seconds),
                        "skipped": False,
                    }
                    rows.append({**common, "calibration": "source_only", **score(y_test, raw_pred)})
                    rows.append({**common, "calibration": "target_offset_calibrated", **score(y_test, raw_pred + offset)})

    metrics_path = args.out_dir / "cross_region_waveform_transfer_metrics.csv"
    boundary_path = args.out_dir / "cross_region_waveform_transfer_boundary.csv"
    split_path = args.out_dir / "cross_region_waveform_transfer_split_info.csv"
    write_csv(metrics_path, rows)
    write_csv(split_path, split_info)
    plot_boundary(rows, args.figure)
    summarize(rows, split_info, args.summary, args.figure, boundary_path)

    report = {
        "metrics": str(metrics_path),
        "split_info": str(split_path),
        "summary": str(args.summary),
        "figure": str(args.figure),
        "rows": len(rows),
    }
    (args.out_dir / "cross_region_waveform_transfer_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
