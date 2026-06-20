#!/usr/bin/env python3
"""Tail audit for balanced held-station strong-motion targets."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from audit_held_station_bootstrap_ci import fit_predict
from run_ground_motion_baseline import METADATA_FEATURES
from run_ground_motion_heldout_baseline import waveform_feature_cols


TARGETS = ["pga", "pgv", "sa03", "sa10", "sa30"]
TAILS = [0.90, 0.95]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def collect_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dataset in args.datasets:
        train_path = args.input_dir / f"{dataset}_held_station_train_features.csv"
        test_path = args.input_dir / f"{dataset}_held_station_test_features.csv"
        if not train_path.exists() or not test_path.exists():
            continue
        train_all = pd.read_csv(train_path)
        test_all = pd.read_csv(test_path)
        metadata_cols = [col for col in METADATA_FEATURES if col in train_all.columns]
        combined_cols = metadata_cols + waveform_feature_cols(train_all)
        for target in TARGETS:
            target_col = f"target_log10_{target}"
            if target_col not in train_all.columns or target_col not in test_all.columns:
                continue
            train = train_all.dropna(subset=[target_col]).copy()
            test = test_all.dropna(subset=[target_col]).copy()
            if train.empty or test.empty:
                continue
            y = test[target_col].astype(float).to_numpy()
            preds = {
                "metadata_only": fit_predict(train, test, metadata_cols, target_col),
                "metadata_plus_early_waveform": fit_predict(train, test, combined_cols, target_col),
            }
            for tail_q in TAILS:
                cutoff = float(np.quantile(y, tail_q))
                mask = y >= cutoff
                for feature_set, pred in preds.items():
                    err = np.abs(y[mask] - pred[mask])
                    miss = y[mask] - pred[mask]
                    rows.append(
                        {
                            "dataset": dataset,
                            "target": target,
                            "early_seconds": 10,
                            "holdout": "station",
                            "feature_set": feature_set,
                            "tail_quantile": tail_q,
                            "tail_rows": int(mask.sum()),
                            "tail_cutoff_log10": cutoff,
                            "mae_log10_target": float(err.mean()),
                            "under_factor2_rate": float(np.mean(miss > 0.3)),
                            "mean_underprediction_log10": float(np.mean(np.maximum(miss, 0.0))),
                            "q95_underprediction_log10": float(np.quantile(np.maximum(miss, 0.0), 0.95)),
                        }
                    )
    return rows


def summarize(rows: list[dict[str, Any]], path: Path, csv_path: Path, figure_path: Path) -> None:
    df = pd.DataFrame(rows)
    pivot = df.pivot_table(
        index=["dataset", "target", "tail_quantile", "tail_rows"],
        columns="feature_set",
        values=["mae_log10_target", "under_factor2_rate"],
        aggfunc="first",
    )
    pivot.columns = [f"{metric}_{feature}" for metric, feature in pivot.columns]
    pivot = pivot.reset_index()
    pivot["mae_reduction_pct"] = (
        (
            pivot["mae_log10_target_metadata_only"]
            - pivot["mae_log10_target_metadata_plus_early_waveform"]
        )
        / pivot["mae_log10_target_metadata_only"]
        * 100.0
    )
    pivot["under_factor2_delta"] = (
        pivot["under_factor2_rate_metadata_only"]
        - pivot["under_factor2_rate_metadata_plus_early_waveform"]
    )
    lines = [
        "# Held-Station Strong-Tail Audit",
        "",
        "日期：2026-06-20",
        "",
        "## 定位",
        "",
        "这个自动审计只看 balanced held-station 测试集里目标最大的 top 10% 和 top 5% 样本，检查平均精度增益是否也出现在强震动尾部。",
        "",
        "Factor-2 漏报定义为预测 log10 目标低于观测值 0.3 以上。",
        "",
        "## 结果",
        "",
        "| 数据集 | 目标 | Tail | rows | tail MAE 降幅 | factor-2 漏报变化 |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in pivot.sort_values(["dataset", "target", "tail_quantile"]).to_dict("records"):
        lines.append(
            f"| {row['dataset']} | {row['target']} | top {100 * (1 - row['tail_quantile']):.0f}% | "
            f"{int(row['tail_rows'])} | {row['mae_reduction_pct']:.1f}% | "
            f"{row['under_factor2_delta']:.3f} |"
        )
    top5 = pivot[pivot["tail_quantile"].eq(0.95)]
    lines += [
        "",
        "## 解释",
        "",
        f"top 5% 强目标样本里，tail MAE 降幅范围为 {top5['mae_reduction_pct'].min():.1f}% 到 {top5['mae_reduction_pct'].max():.1f}%。",
        f"factor-2 漏报率变化范围为 {top5['under_factor2_delta'].min():.3f} 到 {top5['under_factor2_delta'].max():.3f}，负值表示早窗波形模型在该尾部子集里的 factor-2 漏报率更高。",
        "",
        "这个结果应写成强尾部误差边界，不写成尾部问题已解决。",
        "",
        f"CSV：`{csv_path}`",
        f"图：`{figure_path}`",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def plot(rows: list[dict[str, Any]], path: Path) -> None:
    df = pd.DataFrame(rows)
    top5 = df[df["tail_quantile"].eq(0.95)]
    pivot = top5.pivot_table(
        index=["dataset", "target"],
        columns="feature_set",
        values="under_factor2_rate",
        aggfunc="first",
    ).reset_index()
    labels = [f"{row.dataset}\n{row.target.upper()}" for row in pivot.itertuples()]
    x = np.arange(len(pivot))
    width = 0.36
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    ax.bar(x - width / 2, pivot["metadata_only"], width, label="metadata only")
    ax.bar(x + width / 2, pivot["metadata_plus_early_waveform"], width, label="metadata + P window")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Top 5% factor-2 underprediction rate")
    ax.set_title("Held-station strong-tail underprediction")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("work/ground_motion_balanced_station_10s"))
    parser.add_argument("--datasets", nargs="+", default=["instancegm", "knet"])
    parser.add_argument("--csv-out", type=Path, default=Path("work/ground_motion_balanced_station_10s/held_station_tail_audit.csv"))
    parser.add_argument("--summary-out", type=Path, default=Path("outputs/held_station_tail_audit_summary.md"))
    parser.add_argument("--figure-out", type=Path, default=Path("outputs/figures/ground_motion_audit/held_station_tail_audit.png"))
    args = parser.parse_args()

    rows = collect_rows(args)
    write_csv(args.csv_out, rows)
    summarize(rows, args.summary_out, args.csv_out, args.figure_out)
    plot(rows, args.figure_out)
    print(args.summary_out)


if __name__ == "__main__":
    main()
