#!/usr/bin/env python3
"""Minimal NC boundary checks: conformal transfer, strong-tail misses, seed robustness."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import run_cross_region_waveform_transfer as xfer  # noqa: E402


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    keys: list[str] = []
    for row in rows:
        keys += [key for key in row if key not in keys]
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def split_model_cal(df: pd.DataFrame, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    cal = df.sample(frac=0.25, random_state=seed)
    train = df.drop(index=cal.index)
    return train, cal


def load_datasets(args: argparse.Namespace, window: float, seed: int) -> dict[str, dict[str, pd.DataFrame]]:
    datasets: dict[str, dict[str, pd.DataFrame]] = {
        "instancegm": {
            "train": xfer.load_table(args.balanced_root / f"ground_motion_balanced_station_{int(window)}s/instancegm_held_station_train_features.csv", "instancegm", window),
            "test": xfer.load_table(args.balanced_root / f"ground_motion_balanced_station_{int(window)}s/instancegm_held_station_test_features.csv", "instancegm", window),
        },
        "knet": {
            "train": xfer.load_table(args.balanced_root / f"ground_motion_balanced_station_{int(window)}s/knet_held_station_train_features.csv", "knet", window),
            "test": xfer.load_table(args.balanced_root / f"ground_motion_balanced_station_{int(window)}s/knet_held_station_test_features.csv", "knet", window),
        },
    }
    aq_train, aq_test, _ = xfer.load_aq(args.aq_feature_dir, window, args.aq_train_size, args.aq_test_size, seed)
    datasets["aq2009gm"] = {"train": aq_train, "test": aq_test}
    esm_train, esm_test, _ = xfer.load_esm(
        args.esm_features,
        window,
        train_size=args.esm_train_size,
        test_size=args.esm_test_size,
        station_test_groups=args.esm_station_test_groups,
        seed=seed + 503,
    )
    datasets["esm"] = {"train": esm_train, "test": esm_test}
    return datasets


def metric_rows(args: argparse.Namespace, window: float, seed: int) -> list[dict[str, Any]]:
    datasets = load_datasets(args, window, seed)
    features = [
        f"log10_{col}"
        for col in xfer.WAVEFORM_COLS
        if all(f"log10_{col}" in part for data in datasets.values() for part in data.values())
    ]
    rows: list[dict[str, Any]] = []
    for target in xfer.TARGETS:
        target_col = f"target_log10_{target}"
        for source_name, source_data in datasets.items():
            source_train = xfer.finite_target(source_data["train"], target)
            if source_train.empty:
                continue
            model_train, source_cal = split_model_cal(source_train, seed + 19)
            model = xfer.fit_model(model_train, features, target_col)
            source_cal_y = source_cal[target_col].astype(float).to_numpy()
            source_cal_pred = model.predict(source_cal[features])
            source_q90 = float(np.quantile(np.abs(source_cal_y - source_cal_pred), 0.9))
            for test_name, test_data in datasets.items():
                target_train = xfer.finite_target(test_data["train"], target)
                target_test = xfer.finite_target(test_data["test"], target)
                if target_train.empty or target_test.empty:
                    continue
                y = target_test[target_col].astype(float).to_numpy()
                raw_pred = model.predict(target_test[features])
                target_train_y = target_train[target_col].astype(float).to_numpy()
                target_train_pred = model.predict(target_train[features])
                offset = float(np.median(target_train_y - target_train_pred))
                target_q90 = float(np.quantile(np.abs(target_train_y - (target_train_pred + offset)), 0.9))
                modes = []
                if source_name == test_name:
                    modes.append(("target_domain", raw_pred, source_q90))
                else:
                    modes.append(("zero_shot_source_conformal", raw_pred, source_q90))
                    modes.append(("target_offset_conformal", raw_pred + offset, target_q90))
                for mode, pred, q90 in modes:
                    abs_err = np.abs(y - pred)
                    top_rows: list[dict[str, Any]] = []
                    for tail_q in [0.90, 0.95]:
                        cutoff = float(np.quantile(y, tail_q))
                        mask = y >= cutoff
                        miss = y[mask] - pred[mask]
                        top_rows.append(
                            {
                                "tail_quantile": tail_q,
                                "tail_rows": int(mask.sum()),
                                "tail_cutoff_log10": cutoff,
                                "under_factor2_rate": float(np.mean(miss > 0.3)),
                                "mean_underprediction_log10": float(np.mean(np.maximum(miss, 0.0))),
                                "q95_underprediction_log10": float(np.quantile(np.maximum(miss, 0.0), 0.95)),
                            }
                        )
                    rows.append(
                        {
                            "seed": seed,
                            "early_seconds": window,
                            "source_dataset": source_name,
                            "test_dataset": test_name,
                            "target": target,
                            "mode": mode,
                            "train_rows": int(len(model_train)),
                            "calibration_rows": int(len(source_cal if mode != "target_offset_conformal" else target_train)),
                            "test_rows": int(len(target_test)),
                            "mae_log10_target": float(np.mean(abs_err)),
                            "q90_bound_log10": q90,
                            "interval_width_log10": 2 * q90,
                            "coverage90": float(np.mean(abs_err <= q90)),
                            "q95_abs_error_log10": float(np.quantile(abs_err, 0.95)),
                            "tail": top_rows,
                        }
                    )
    return rows


def flatten_tail(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        base = {k: v for k, v in row.items() if k != "tail"}
        for tail in row["tail"]:
            out.append({**base, **tail})
    return out


def summarize(out_dir: Path, summary: Path) -> None:
    conformal = pd.read_csv(out_dir / "conformal_boundary.csv")
    tail = pd.read_csv(out_dir / "tail_underprediction.csv")
    robust = pd.read_csv(out_dir / "seed_robustness.csv")
    lines = [
        "# NC boundary sensitivity checks",
        "",
        "Feature set: early log-waveform features only. Models exclude distance, site terms, event id, and station id.",
        "",
        "## Conformal transfer boundary",
        "",
        "| Window | Mode | Median coverage90 | Median width |",
        "|---:|---|---:|---:|",
    ]
    for (window, mode), sub in conformal.groupby(["early_seconds", "mode"]):
        lines.append(f"| {window:g}s | {mode} | {sub.coverage90.median():.3f} | {sub.interval_width_log10.median():.3f} |")
    lines += [
        "",
        "## Strong-motion tail underprediction",
        "",
        "| Window | Mode | Tail | Median factor-2 underprediction rate | Median q95 underprediction |",
        "|---:|---|---:|---:|---:|",
    ]
    for (window, mode, tail_q), sub in tail.groupby(["early_seconds", "mode", "tail_quantile"]):
        lines.append(
            f"| {window:g}s | {mode} | top {100*(1-tail_q):.0f}% | "
            f"{sub.under_factor2_rate.median():.3f} | {sub.q95_underprediction_log10.median():.3f} |"
        )
    lines += [
        "",
        "## Three-seed transfer robustness",
        "",
        "| Window | Target | Mode | Median ratio range |",
        "|---:|---|---|---:|",
    ]
    for row in robust.itertuples(index=False):
        lines.append(
            f"| {row.early_seconds:g}s | {row.target.upper()} | {row.mode} | "
            f"{row.ratio_min:.2f}-{row.ratio_max:.2f} |"
        )
    lines += [
        "",
        "Files:",
        f"- `{out_dir / 'conformal_boundary.csv'}`",
        f"- `{out_dir / 'tail_underprediction.csv'}`",
        f"- `{out_dir / 'seed_robustness.csv'}`",
    ]
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--balanced-root", type=Path, default=Path("work"))
    parser.add_argument("--aq-feature-dir", type=Path, default=Path("work/aq2009gm_full_stream_validation_2s5s/features"))
    parser.add_argument("--esm-features", type=Path, default=Path("work/esm_compact_features_full/esm_compact_features.csv.gz"))
    parser.add_argument("--out-dir", type=Path, default=Path("work/nc_boundary_sensitivity"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/nc_boundary_sensitivity_summary.md"))
    parser.add_argument("--windows", nargs="+", type=float, default=[2.0, 5.0])
    parser.add_argument("--seeds", nargs="+", type=int, default=[17, 59, 101])
    parser.add_argument("--aq-train-size", type=int, default=30000)
    parser.add_argument("--aq-test-size", type=int, default=10000)
    parser.add_argument("--esm-train-size", type=int, default=20000)
    parser.add_argument("--esm-test-size", type=int, default=6000)
    parser.add_argument("--esm-station-test-groups", type=int, default=200)
    args = parser.parse_args()

    all_rows: list[dict[str, Any]] = []
    for window in args.windows:
        for seed in args.seeds:
            print(f"[run] window={window:g}s seed={seed}", flush=True)
            all_rows.extend(metric_rows(args, window, seed))

    flat = [{k: v for k, v in row.items() if k != "tail"} for row in all_rows]
    conformal_path = args.out_dir / "conformal_boundary.csv"
    tail_path = args.out_dir / "tail_underprediction.csv"
    write_csv(conformal_path, flat)
    write_csv(tail_path, flatten_tail(all_rows))

    conformal = pd.DataFrame(flat)
    within = conformal[conformal["mode"].eq("target_domain")].set_index(["seed", "early_seconds", "test_dataset", "target"])["mae_log10_target"].to_dict()
    cross = conformal[conformal["source_dataset"].ne(conformal["test_dataset"])].copy()
    cross["ratio_vs_target_domain"] = [
        row.mae_log10_target / within[(row.seed, row.early_seconds, row.test_dataset, row.target)]
        for row in cross.itertuples(index=False)
    ]
    robust_rows = []
    for (window, target, mode, seed), sub in cross.groupby(["early_seconds", "target", "mode", "seed"]):
        robust_rows.append(
            {
                "early_seconds": window,
                "target": target,
                "mode": mode,
                "seed": seed,
                "median_ratio_vs_target_domain": float(sub["ratio_vs_target_domain"].median()),
            }
        )
    robust = pd.DataFrame(robust_rows)
    robust_summary = (
        robust.groupby(["early_seconds", "target", "mode"])["median_ratio_vs_target_domain"]
        .agg(ratio_min="min", ratio_median="median", ratio_max="max")
        .reset_index()
    )
    robust_summary.to_csv(args.out_dir / "seed_robustness.csv", index=False)
    summarize(args.out_dir, args.summary)
    print(args.summary)


if __name__ == "__main__":
    main()
