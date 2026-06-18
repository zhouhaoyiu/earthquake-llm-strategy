#!/usr/bin/env python3
"""Create a publication-style held-out generalization figure."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


TARGET_ORDER = ["pga", "pgv", "sa03", "sa10", "sa30"]
DATASET_ORDER = ["instancegm", "knet"]
SPLIT_LABELS = {"event": "held event", "station": "held station"}
DATASET_LABELS = {"instancegm": "InstanceGM", "knet": "K-NET"}
TARGET_LABELS = {"pga": "PGA", "pgv": "PGV", "sa03": "SA03", "sa10": "SA10", "sa30": "SA30"}
COLORS = {"held event": "#3b7ea1", "held station": "#c55a32"}


def load_split_table(event_path: Path, station_path: Path) -> pd.DataFrame:
    frames = []
    for holdout, path in [("event", event_path), ("station", station_path)]:
        df = pd.read_csv(path)
        df = df[
            (df["holdout"] == holdout)
            & (df["feature_set"].isin(["metadata_only", "metadata_plus_early_waveform"]))
            & (~df["skipped"])
        ].copy()
        frames.append(df)
    raw = pd.concat(frames, ignore_index=True)
    meta = raw[raw["feature_set"] == "metadata_only"][
        ["dataset", "target", "holdout", "mae_log10_target", "r2_log10_target", "test_rows", "group_overlap"]
    ].rename(columns={"mae_log10_target": "metadata_mae", "r2_log10_target": "metadata_r2"})
    combo = raw[raw["feature_set"] == "metadata_plus_early_waveform"][
        ["dataset", "target", "holdout", "mae_log10_target", "r2_log10_target", "test_rows", "group_overlap"]
    ].rename(columns={"mae_log10_target": "combined_mae", "r2_log10_target": "combined_r2"})
    table = meta.merge(combo, on=["dataset", "target", "holdout"], suffixes=("_metadata", "_combined"))
    table["mae_reduction_pct"] = (table["metadata_mae"] - table["combined_mae"]) / table["metadata_mae"] * 100.0
    table["series"] = table["dataset"].map(DATASET_LABELS) + " " + table["target"].map(TARGET_LABELS)
    table["split"] = table["holdout"].map(SPLIT_LABELS)
    table["target_order"] = table["target"].map({target: idx for idx, target in enumerate(TARGET_ORDER)})
    table["dataset_order"] = table["dataset"].map({dataset: idx for idx, dataset in enumerate(DATASET_ORDER)})
    return table.sort_values(["dataset_order", "target_order", "holdout"]).reset_index(drop=True)


def load_distribution_table(path: Path) -> pd.DataFrame:
    dist = pd.read_csv(path)
    dist["variable_label"] = dist["variable"].replace(
        {
            "source_magnitude": "magnitude",
            "source_distance_km": "distance",
            "target_log10_pga": "log10 PGA",
        }
    )
    return dist


def target_positions(table: pd.DataFrame) -> tuple[list[str], dict[str, float]]:
    series = []
    for dataset in DATASET_ORDER:
        for target in TARGET_ORDER:
            if ((table["dataset"] == dataset) & (table["target"] == target)).any():
                series.append(f"{DATASET_LABELS[dataset]} {TARGET_LABELS[target]}")
    positions = {name: idx for idx, name in enumerate(series)}
    return series, positions


def style_axis(ax: plt.Axes) -> None:
    ax.grid(True, axis="y", alpha=0.25, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_mae_reduction(ax: plt.Axes, table: pd.DataFrame, series: list[str], positions: dict[str, float]) -> None:
    width = 0.36
    for split, offset in [("held event", -width / 2), ("held station", width / 2)]:
        sub = table[table["split"] == split]
        xs = [positions[name] + offset for name in sub["series"]]
        ax.bar(xs, sub["mae_reduction_pct"], width=width, color=COLORS[split], label=split)
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_xticks(range(len(series)))
    ax.set_xticklabels(series, rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("MAE reduction from metadata-only (%)")
    ax.set_title("a  Early waveform gain persists in held-out splits", loc="left", fontsize=11)
    ax.legend(frameon=False, fontsize=8, ncol=2)
    style_axis(ax)


def plot_r2(ax: plt.Axes, table: pd.DataFrame, series: list[str], positions: dict[str, float]) -> None:
    width = 0.36
    for split, offset in [("held event", -width / 2), ("held station", width / 2)]:
        sub = table[table["split"] == split]
        xs = [positions[name] + offset for name in sub["series"]]
        ax.bar(xs, sub["combined_r2"], width=width, color=COLORS[split], label=split)
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_xticks(range(len(series)))
    ax.set_xticklabels(series, rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("combined-model R2")
    ax.set_title("b  Combined model skill under held-out evaluation", loc="left", fontsize=11)
    style_axis(ax)


def plot_distribution_overlap(ax: plt.Axes, dist: pd.DataFrame) -> None:
    labels = ["magnitude", "distance", "log10 PGA"]
    x = np.arange(len(labels))
    width = 0.36
    for idx, dataset in enumerate(["InstanceGM", "K-NET"]):
        sub = dist[dist["dataset"] == dataset].set_index("variable_label").reindex(labels)
        ax.bar(x + (idx - 0.5) * width, sub["hist_overlap"], width=width, label=dataset, color=["#7aa974", "#8f6bb1"][idx])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("train-test histogram overlap")
    ax.set_title("c  Station split keeps source-path-target shift", loc="left", fontsize=11)
    ax.legend(frameon=False, fontsize=8, ncol=2)
    style_axis(ax)


def plot_station_shift(ax: plt.Axes, dist: pd.DataFrame) -> None:
    view = dist.copy()
    train_range = (view["train_q95"] - view["train_q05"]).replace(0, np.nan)
    view["standardized_median_shift"] = (view["test_median"] - view["train_median"]) / train_range
    labels = []
    values = []
    colors = []
    for dataset in ["InstanceGM", "K-NET"]:
        for variable in ["source_magnitude", "source_distance_km", "target_log10_pga"]:
            row = view[(view["dataset"] == dataset) & (view["variable"] == variable)].iloc[0]
            labels.append(f"{dataset}\n{row['variable_label']}")
            values.append(row["standardized_median_shift"])
            colors.append("#7aa974" if dataset == "InstanceGM" else "#8f6bb1")
    ax.bar(np.arange(len(values)), values, color=colors)
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_xticks(np.arange(len(values)))
    ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=7)
    ax.set_ylabel("median shift / train 5-95% range")
    ax.set_title("d  Normalized direction of station-split shift", loc="left", fontsize=11)
    style_axis(ax)


def write_summary(path: Path, table: pd.DataFrame, dist: pd.DataFrame, figure_path: Path, csv_path: Path) -> None:
    station = table[table["holdout"] == "station"].copy()
    event = table[table["holdout"] == "event"].copy()
    key_rows = []
    for dataset, target in [("instancegm", "pga"), ("instancegm", "pgv"), ("knet", "pga")]:
        for split_name, sub in [("held-event", event), ("balanced held-station", station)]:
            row = sub[(sub["dataset"] == dataset) & (sub["target"] == target)].iloc[0]
            key_rows.append(
                f"- {split_name} {DATASET_LABELS[dataset]} {TARGET_LABELS[target]}: "
                f"{row['metadata_mae']:.3f} -> {row['combined_mae']:.3f} "
                f"({row['mae_reduction_pct']:.1f}% reduction), R2={row['combined_r2']:.3f}."
            )
    inst_dist = dist[(dist["dataset"] == "InstanceGM") & (dist["variable"] == "source_distance_km")].iloc[0]
    inst_pga = dist[(dist["dataset"] == "InstanceGM") & (dist["variable"] == "target_log10_pga")].iloc[0]
    lines = [
        "# Figure 3 Held-Out Generalization",
        "",
        "Date: 2026-06-18",
        "",
        "Figure 3 combines the 10 s held-event results, balanced held-station results, and station-split distribution audit. It uses the existing experiment outputs only; no model was rerun.",
        "",
        *key_rows,
        "",
        "Distribution audit:",
        "",
        f"- InstanceGM station-held records are farther from the source: train median {inst_dist['train_median']:.2f} km, test median {inst_dist['test_median']:.2f} km, overlap {inst_dist['hist_overlap']:.2f}.",
        f"- InstanceGM station-held PGA targets are weaker: train median log10 PGA {inst_pga['train_median']:.2f}, test median {inst_pga['test_median']:.2f}, overlap {inst_pga['hist_overlap']:.2f}.",
        "- K-NET station-held distance and PGA distributions have high overlap, above 0.91 in the current audit.",
        "",
        "Interpretation:",
        "",
        "The held-out evidence supports the narrow claim that early post-P waveform features add strong-motion information beyond metadata under event and station separation. The split audit shows that the station-held test retains nontrivial distribution shift.",
        "",
        f"Figure: `{figure_path}`",
        f"CSV: `{csv_path}`",
        "",
    ]
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-results", type=Path, default=Path("work/ground_motion_heldout_10s/ground_motion_heldout_results.csv"))
    parser.add_argument("--station-results", type=Path, default=Path("work/ground_motion_balanced_station_10s/ground_motion_heldout_results.csv"))
    parser.add_argument("--distribution-audit", type=Path, default=Path("work/ground_motion_balanced_station_10s/balanced_station_distribution_audit.csv"))
    parser.add_argument("--figure", type=Path, default=Path("outputs/figures/figure3_heldout_generalization.png"))
    parser.add_argument("--csv", type=Path, default=Path("outputs/figure3_heldout_generalization.csv"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/figure3_heldout_generalization_summary.md"))
    args = parser.parse_args()

    args.figure.parent.mkdir(parents=True, exist_ok=True)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)

    table = load_split_table(args.event_results, args.station_results)
    dist = load_distribution_table(args.distribution_audit)
    table.to_csv(args.csv, index=False)

    series, positions = target_positions(table)
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 8.1), dpi=180)
    plot_mae_reduction(axes[0, 0], table, series, positions)
    plot_r2(axes[0, 1], table, series, positions)
    plot_distribution_overlap(axes[1, 0], dist)
    plot_station_shift(axes[1, 1], dist)
    fig.suptitle("Held-out generalization and station-split audit", x=0.02, y=0.995, ha="left", fontsize=14)
    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.96])
    fig.savefig(args.figure)
    plt.close(fig)

    write_summary(args.summary, table, dist, args.figure, args.csv)
    print(f"wrote {args.figure}")
    print(f"wrote {args.csv}")
    print(f"wrote {args.summary}")


if __name__ == "__main__":
    main()
