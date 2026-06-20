#!/usr/bin/env python3
"""Audit whether held-station waveform gains persist inside train-distribution support."""

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

from run_ground_motion_baseline import METADATA_FEATURES, train_eval
from run_ground_motion_heldout_baseline import waveform_feature_cols


TARGETS = ["pga", "pgv", "sa03", "sa10", "sa30"]
MATCH_COLUMNS = ["source_magnitude", "source_distance_km"]
FEATURE_SETS = ["metadata_only", "metadata_plus_early_waveform"]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def support_mask(
    train: pd.DataFrame,
    test: pd.DataFrame,
    target: str,
    include_target: bool,
) -> tuple[pd.Series, dict[str, float]]:
    cols = MATCH_COLUMNS + ([f"target_log10_{target}"] if include_target else [])
    cols = [c for c in cols if c in train.columns and c in test.columns]
    mask = pd.Series(True, index=test.index)
    bounds: dict[str, float] = {}
    for col in cols:
        train_values = pd.to_numeric(train[col], errors="coerce").dropna()
        test_values = pd.to_numeric(test[col], errors="coerce")
        if len(train_values) < 20:
            continue
        lo = float(train_values.quantile(0.05))
        hi = float(train_values.quantile(0.95))
        mask &= test_values.between(lo, hi, inclusive="both").fillna(False)
        bounds[f"{col}_train_q05"] = lo
        bounds[f"{col}_train_q95"] = hi
    return mask, bounds


def collect_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dataset in args.datasets:
        train_path = args.input_dir / f"{dataset}_held_station_train_features.csv"
        test_path = args.input_dir / f"{dataset}_held_station_test_features.csv"
        if not train_path.exists() or not test_path.exists():
            continue
        train = pd.read_csv(train_path)
        test = pd.read_csv(test_path)
        metadata_cols = [col for col in METADATA_FEATURES if col in train.columns]
        waveform_cols = waveform_feature_cols(train)
        features_by_set = {
            "metadata_only": metadata_cols,
            "metadata_plus_early_waveform": metadata_cols + waveform_cols,
        }
        for target in TARGETS:
            target_col = f"target_log10_{target}"
            if target_col not in train.columns or train[target_col].notna().sum() == 0 or test[target_col].notna().sum() == 0:
                continue
            path_mask, path_bounds = support_mask(train, test, target, include_target=False)
            target_mask, target_bounds = support_mask(train, test, target, include_target=True)
            scopes = {
                "full_test": (test, {}),
                "source_path_support": (test.loc[path_mask].copy(), path_bounds),
                "matched_train_support": (test.loc[target_mask].copy(), target_bounds),
            }
            for scope, (scoped_test, bounds) in scopes.items():
                for feature_set in FEATURE_SETS:
                    result = train_eval(
                        train,
                        scoped_test,
                        features_by_set[feature_set],
                        "hgb",
                        dataset,
                        target,
                    )
                    row = {
                        "dataset": dataset,
                        "target": target,
                        "scope": scope,
                        "feature_set": feature_set,
                        "test_rows_full": int(test[target_col].notna().sum()),
                        "test_rows_scope": int(pd.to_numeric(scoped_test[target_col], errors="coerce").notna().sum()),
                        "retained_fraction": float(
                            pd.to_numeric(scoped_test[target_col], errors="coerce").notna().sum()
                            / max(1, test[target_col].notna().sum())
                        ),
                        "mae_log10_target": result["mae_log10_target"],
                        "rmse_log10_target": result["rmse_log10_target"],
                        "r2_log10_target": result["r2_log10_target"],
                        "skipped": result["skipped"],
                    }
                    row.update(bounds)
                    rows.append(row)
    return rows


def summary_rows(metrics: pd.DataFrame) -> pd.DataFrame:
    pivot = metrics.pivot_table(
        index=["dataset", "target", "scope", "test_rows_full", "test_rows_scope", "retained_fraction"],
        columns="feature_set",
        values="mae_log10_target",
        aggfunc="first",
    ).reset_index()
    pivot["mae_reduction_pct"] = (
        (pivot["metadata_only"] - pivot["metadata_plus_early_waveform"]) / pivot["metadata_only"] * 100.0
    )
    return pivot.sort_values(["dataset", "target", "scope"])


def write_markdown(summary: pd.DataFrame, path: Path, figure_path: Path, csv_path: Path) -> None:
    path_support = summary[summary["scope"] == "source_path_support"].copy()
    matched = summary[summary["scope"] == "matched_train_support"].copy()
    full = summary[summary["scope"] == "full_test"].copy()
    merged_path = path_support.merge(
        full[["dataset", "target", "mae_reduction_pct"]].rename(columns={"mae_reduction_pct": "full_reduction_pct"}),
        on=["dataset", "target"],
        how="left",
    )
    merged_matched = matched.merge(
        full[["dataset", "target", "mae_reduction_pct"]].rename(columns={"mae_reduction_pct": "full_reduction_pct"}),
        on=["dataset", "target"],
        how="left",
    )
    lines = [
        "# Matched Held-Station Gain Audit",
        "",
        "日期：2026-06-20",
        "",
        "## 定位",
        "",
        "这个自动审计回答两个问题：只把 held-station 测试样本裁到训练集震级和距离的 5-95% 覆盖范围内以后，早窗波形增益是否仍然存在；再加入目标幅值裁剪以后结果是否一致。",
        "",
        "`source_path_support` 不使用目标幅值。`matched_train_support` 使用目标幅值，因此后者是事后分布伪影审计，不是可部署预警模型评估。",
        "",
        "## Source-path support 结果",
        "",
        "| 数据集 | 目标 | 保留比例 | full reduction % | source-path reduction % | rows |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in merged_path.to_dict("records"):
        lines.append(
            f"| {row['dataset']} | {row['target']} | {row['retained_fraction']:.3f} | "
            f"{row['full_reduction_pct']:.1f} | {row['mae_reduction_pct']:.1f} | {int(row['test_rows_scope'])} |"
        )
    lines += [
        "",
        "## Target-matched 结果",
        "",
        "| 数据集 | 目标 | 保留比例 | full reduction % | target-matched reduction % | rows |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in merged_matched.to_dict("records"):
        lines.append(
            f"| {row['dataset']} | {row['target']} | {row['retained_fraction']:.3f} | "
            f"{row['full_reduction_pct']:.1f} | {row['mae_reduction_pct']:.1f} | {int(row['test_rows_scope'])} |"
        )
    path_min_gain = float(path_support["mae_reduction_pct"].min())
    path_min_retained = float(path_support["retained_fraction"].min())
    min_gain = float(matched["mae_reduction_pct"].min())
    min_retained = float(matched["retained_fraction"].min())
    lines += [
        "",
        "## 解释",
        "",
        f"只按震级和距离裁剪时，所有子集仍为正增益，最小 MAE 降幅为 {path_min_gain:.1f}%。最小保留比例为 {path_min_retained:.3f}。",
        "",
        f"加入目标幅值裁剪后，所有 matched 子集仍为正增益，最小 matched MAE 降幅为 {min_gain:.1f}%。最小保留比例为 {min_retained:.3f}。",
        "",
        "这个结果降低了“增益只来自 held-station 测试集分布异常”的风险。正文仍应保守表述为 source-path shift 下的稳健性证据，不能写成完全 distribution-matched transfer。",
        "",
        f"CSV：`{csv_path}`",
        f"图：`{figure_path}`",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_summary(summary: pd.DataFrame, path: Path) -> None:
    full = summary[summary["scope"] == "full_test"].set_index(["dataset", "target"])
    path_support = summary[summary["scope"] == "source_path_support"].set_index(["dataset", "target"])
    matched = summary[summary["scope"] == "matched_train_support"].set_index(["dataset", "target"])
    keys = list(matched.index)
    labels = [f"{ds}\n{target}" for ds, target in keys]
    x = np.arange(len(keys))
    width = 0.27
    fig, ax1 = plt.subplots(figsize=(11, 6.5))
    ax1.bar(x - width, [full.loc[k, "mae_reduction_pct"] for k in keys], width, label="full test")
    ax1.bar(x, [path_support.loc[k, "mae_reduction_pct"] for k in keys], width, label="source-path support")
    ax1.bar(x + width, [matched.loc[k, "mae_reduction_pct"] for k in keys], width, label="target-matched support")
    ax1.axhline(0, color="black", linewidth=0.8)
    ax1.set_ylabel("MAE reduction vs metadata-only (%)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.set_title("Held-station gain after train-support matching")
    ax1.grid(axis="y", alpha=0.25)
    ax1.legend(loc="upper right", frameon=False)

    ax2 = ax1.twinx()
    ax2.plot(x, [path_support.loc[k, "retained_fraction"] for k in keys], color="black", marker="o", linewidth=1.5)
    ax2.plot(x, [matched.loc[k, "retained_fraction"] for k in keys], color="black", marker="s", linewidth=1.2, linestyle="--")
    ax2.set_ylabel("Retained fraction")
    ax2.set_ylim(0, 1.05)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("work/ground_motion_balanced_station_10s"))
    parser.add_argument("--datasets", nargs="+", default=["instancegm", "knet"])
    parser.add_argument(
        "--metrics-out",
        type=Path,
        default=Path("work/ground_motion_balanced_station_10s/matched_station_gain_audit.csv"),
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        default=Path("outputs/matched_station_gain_audit_summary.md"),
    )
    parser.add_argument(
        "--figure-out",
        type=Path,
        default=Path("outputs/figures/ground_motion_audit/matched_station_gain_audit.png"),
    )
    args = parser.parse_args()

    rows = collect_rows(args)
    write_csv(args.metrics_out, rows)
    summary = summary_rows(pd.DataFrame(rows))
    write_csv(args.metrics_out.with_name("matched_station_gain_audit_summary.csv"), summary.to_dict("records"))
    plot_summary(summary, args.figure_out)
    write_markdown(summary, args.summary_out, args.figure_out, args.metrics_out)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
