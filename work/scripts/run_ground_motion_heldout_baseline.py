#!/usr/bin/env python3
"""Ground-motion baseline with held-event or held-station splits."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from run_ground_motion_baseline import (
    METADATA_FEATURES,
    TARGET_COLUMNS,
    build_frame,
    train_eval,
)


ID_COLUMNS = [
    "global_id",
    "record_id",
    "event_id",
    "station_network_code",
    "station_code",
    "split",
    "original_split",
]


def has_any_target(df: pd.DataFrame, target_columns: list[str]) -> pd.Series:
    mask = pd.Series(False, index=df.index)
    for col in target_columns:
        if col in df.columns:
            mask |= pd.to_numeric(df[col], errors="coerce").fillna(0).gt(0)
    return mask


def eligible_rows(
    manifest: Path,
    dataset: str,
    max_samples: int,
    target_columns: list[str],
) -> pd.DataFrame:
    frames = []
    for chunk in pd.read_csv(manifest, chunksize=200_000, dtype=str):
        sub = chunk[(chunk["dataset"] == dataset) & (chunk["has_ground_motion_task"] == "1")].copy()
        if sub.empty:
            continue
        sub = sub[has_any_target(sub, target_columns)]
        if max_samples:
            n_samples = pd.to_numeric(sub["n_samples"], errors="coerce")
            sub = sub[n_samples.le(max_samples)]
        if not sub.empty:
            frames.append(sub)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def group_key(df: pd.DataFrame, holdout: str) -> pd.Series:
    if holdout == "event":
        return df["event_id"].fillna("").astype(str)
    if holdout == "station":
        network = df["station_network_code"].fillna("").astype(str)
        station = df["station_code"].fillna("").astype(str)
        return network + "." + station
    raise ValueError(f"unsupported holdout type: {holdout}")


def split_by_group(
    df: pd.DataFrame,
    holdout: str,
    train_size: int,
    test_size: int,
    seed: int,
    min_test_groups: int = 0,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    work = df.copy()
    work["_group"] = group_key(work, holdout)
    work = work[work["_group"].ne("") & work["_group"].ne(".")].copy()
    rng = np.random.default_rng(seed)
    group_sizes = work["_group"].value_counts()
    groups = np.array(group_sizes.index.tolist(), dtype=object)
    rng.shuffle(groups)

    if min_test_groups > 0:
        # ponytail: hold out many stations first; stratified station sampling can replace this if coverage matters.
        test_groups = list(groups[: min(min_test_groups, len(groups))])
    else:
        test_groups = []
        test_rows = 0
        for group in groups:
            test_groups.append(group)
            test_rows += int(group_sizes.loc[group])
            if test_rows >= test_size:
                break

    test_group_set = set(test_groups)
    train = work[~work["_group"].isin(test_group_set)].copy()
    test = work[work["_group"].isin(test_group_set)].copy()

    if len(train) > train_size:
        train = train.sample(train_size, random_state=seed + 11)
    if len(test) > test_size:
        if min_test_groups > 0 and test["_group"].nunique() <= test_size:
            keep = test.groupby("_group", group_keys=False).sample(1, random_state=seed + 17)
            rest = test.drop(index=keep.index)
            extra = rest.sample(test_size - len(keep), random_state=seed + 19) if len(keep) < test_size else rest.iloc[:0]
            test = pd.concat([keep, extra], ignore_index=False).sample(frac=1, random_state=seed + 23)
        else:
            test = test.sample(test_size, random_state=seed + 17)

    overlap = set(train["_group"]).intersection(set(test["_group"]))
    assert not overlap, "held-out group overlap detected"
    info = {
        "holdout": holdout,
        "group_column": "event_id" if holdout == "event" else "station_network_code.station_code",
        "eligible_rows": int(len(work)),
        "eligible_groups": int(work["_group"].nunique()),
        "train_rows_selected": int(len(train)),
        "test_rows_selected": int(len(test)),
        "train_groups": int(train["_group"].nunique()),
        "test_groups": int(test["_group"].nunique()),
        "group_overlap": int(len(overlap)),
    }
    train = train.drop(columns=["_group"])
    test = test.drop(columns=["_group"])
    return train, test, info


def waveform_feature_cols(df: pd.DataFrame) -> list[str]:
    return [
        col
        for col in df.columns
        if col.endswith("_early_absmax")
        or col.endswith("_early_rms")
        or col.endswith("_early_std")
        or col.endswith("_early_p95_abs")
    ]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("work/unified_manifest/unified_manifest.csv.gz"))
    parser.add_argument("--out-dir", type=Path, default=Path("work/ground_motion_heldout_10s"))
    parser.add_argument("--datasets", nargs="+", default=["instancegm", "knet"])
    parser.add_argument("--holdouts", nargs="+", default=["event", "station"], choices=["event", "station"])
    parser.add_argument("--station-test-groups", type=int, default=0)
    parser.add_argument("--train-size", type=int, default=5000)
    parser.add_argument("--test-size", type=int, default=1000)
    parser.add_argument("--early-seconds", type=float, default=10.0)
    parser.add_argument("--max-samples", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=31)
    parser.add_argument("--targets", nargs="+", default=["pga", "pgv", "sa03", "sa10", "sa30"])
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    targets = {name: TARGET_COLUMNS[name] for name in args.targets if name in TARGET_COLUMNS}
    target_columns = list(targets.values())
    all_reports: list[dict[str, Any]] = []
    split_infos: list[dict[str, Any]] = []
    data_paths: dict[str, Any] = {}

    for dataset in args.datasets:
        print(f"loading eligible rows {dataset}", flush=True)
        rows = eligible_rows(args.manifest, dataset, args.max_samples, target_columns)
        if rows.empty:
            continue
        data_paths[dataset] = {}

        for holdout in args.holdouts:
            print(f"splitting {dataset} held-{holdout}", flush=True)
            train_rows, test_rows, split_info = split_by_group(
                rows,
                holdout=holdout,
                train_size=args.train_size,
                test_size=args.test_size,
                seed=args.seed + (101 if holdout == "station" else 0),
                min_test_groups=args.station_test_groups if holdout == "station" else 0,
            )
            split_info["dataset"] = dataset
            split_infos.append(split_info)
            print(
                f"building features {dataset} held-{holdout}: "
                f"train={len(train_rows)} test={len(test_rows)} groups "
                f"{split_info['train_groups']}/{split_info['test_groups']}",
                flush=True,
            )
            train_df = build_frame(train_rows.to_dict("records"), args.early_seconds, targets)
            test_df = build_frame(test_rows.to_dict("records"), args.early_seconds, targets)

            prefix = f"{dataset}_held_{holdout}"
            train_path = args.out_dir / f"{prefix}_train_features.csv"
            test_path = args.out_dir / f"{prefix}_test_features.csv"
            train_df.to_csv(train_path, index=False)
            test_df.to_csv(test_path, index=False)
            data_paths[dataset][holdout] = {
                "train_features": str(train_path),
                "test_features": str(test_path),
            }

            metadata_cols = [col for col in METADATA_FEATURES if col in train_df.columns]
            waveform_cols = waveform_feature_cols(train_df)
            feature_sets = {
                "median": metadata_cols[:1],
                "metadata_only": metadata_cols,
                "early_waveform_only": waveform_cols,
                "metadata_plus_early_waveform": metadata_cols + waveform_cols,
            }
            for target in targets:
                for feature_set, features in feature_sets.items():
                    actual_model = "median" if feature_set == "median" else "hgb"
                    result = train_eval(train_df, test_df, features, actual_model, dataset, target)
                    result["feature_set"] = feature_set
                    result["holdout"] = holdout
                    result["early_seconds"] = args.early_seconds
                    result["group_overlap"] = split_info["group_overlap"]
                    all_reports.append(result)
                    print(
                        dataset,
                        f"held-{holdout}",
                        target,
                        feature_set,
                        result["mae_log10_target"],
                        result["r2_log10_target"],
                        flush=True,
                    )

    results_path = args.out_dir / "ground_motion_heldout_results.csv"
    split_path = args.out_dir / "ground_motion_heldout_split_info.csv"
    write_csv(results_path, all_reports)
    write_csv(split_path, split_infos)

    report = {
        "manifest": str(args.manifest),
        "datasets": args.datasets,
        "holdouts": args.holdouts,
        "train_size_requested": args.train_size,
        "test_size_requested": args.test_size,
        "early_seconds": args.early_seconds,
        "max_samples": args.max_samples,
        "targets": list(targets),
        "data_paths": data_paths,
        "results_path": str(results_path),
        "split_info_path": str(split_path),
        "split_info": split_infos,
        "results": all_reports,
        "note": "Held-out baselines split rows by event_id or station code. Group overlap must be zero.",
    }
    report_path = args.out_dir / "ground_motion_heldout_summary.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
