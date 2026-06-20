#!/usr/bin/env python3
"""Plot residual evolution across early waveform windows."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


WINDOW_DIRS = {
    1: Path("work/ground_motion_residuals_1s"),
    3: Path("work/ground_motion_residuals_3s"),
    10: Path("work/ground_motion_residuals_10s"),
}


def load_metrics(window_dirs: dict[int, Path]) -> pd.DataFrame:
    frames = []
    for window_s, directory in window_dirs.items():
        path = directory / "ground_motion_residual_metrics.csv"
        df = pd.read_csv(path)
        df["window_s"] = window_s
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def load_bins(window_dirs: dict[int, Path]) -> pd.DataFrame:
    frames = []
    for window_s, directory in window_dirs.items():
        path = directory / "ground_motion_residual_bins.csv"
        df = pd.read_csv(path)
        df["window_s"] = window_s
        df["x_center"] = (df["x_min"] + df["x_max"]) / 2.0
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def comparison_table(metrics: pd.DataFrame) -> pd.DataFrame:
    idx_cols = ["window_s", "dataset", "target"]
    meta = metrics.loc[metrics["feature_set"] == "metadata_only", idx_cols + [
        "mae_log10_target",
        "q95_abs_residual",
        "r2_log10_target",
    ]]
    combo = metrics.loc[metrics["feature_set"] == "metadata_plus_early_waveform", idx_cols + [
        "mae_log10_target",
        "q95_abs_residual",
        "r2_log10_target",
        "median_signed_residual",
        "mean_signed_residual",
    ]]
    merged = meta.merge(combo, on=idx_cols, suffixes=("_metadata", "_combined"))
    merged["mae_reduction_pct"] = (
        (merged["mae_log10_target_metadata"] - merged["mae_log10_target_combined"])
        / merged["mae_log10_target_metadata"]
        * 100.0
    )
    merged["q95_reduction_pct"] = (
        (merged["q95_abs_residual_metadata"] - merged["q95_abs_residual_combined"])
        / merged["q95_abs_residual_metadata"]
        * 100.0
    )
    merged["r2_gain"] = merged["r2_log10_target_combined"] - merged["r2_log10_target_metadata"]
    merged["series"] = merged["dataset"].str.upper() + " " + merged["target"].str.upper()
    return merged.sort_values(["dataset", "target", "window_s"]).reset_index(drop=True)


def style_axis(ax: plt.Axes) -> None:
    ax.grid(True, axis="y", alpha=0.25, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xticks([1, 3, 10])


def plot_metric_lines(ax: plt.Axes, table: pd.DataFrame, y_col: str, ylabel: str, title: str) -> None:
    for series, group in table.groupby("series", sort=False):
        group = group.sort_values("window_s")
        lw = 2.2 if series == "KNET PGA" else 1.6
        alpha = 1.0 if series == "KNET PGA" else 0.84
        marker = "s" if series == "KNET PGA" else "o"
        ax.plot(group["window_s"], group[y_col], marker=marker, linewidth=lw, alpha=alpha, label=series)
    ax.set_xlabel("post-P window (s)")
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontsize=11)
    style_axis(ax)


def plot_distance_bins(ax: plt.Axes, bins: pd.DataFrame) -> None:
    sub = bins[
        (bins["dataset"] == "knet")
        & (bins["target"] == "pga")
        & (bins["feature_set"] == "metadata_plus_early_waveform")
        & (bins["variable"] == "source_distance_km")
    ].copy()
    for window_s, group in sub.groupby("window_s"):
        group = group.sort_values("x_center")
        ax.plot(group["x_center"], group["mae_residual"], marker="o", linewidth=1.8, label=f"{window_s} s")
    ax.set_xlabel("source distance bin center (km)")
    ax.set_ylabel("MAE residual")
    ax.set_title("K-NET PGA residual tail by distance", loc="left", fontsize=11)
    ax.grid(True, axis="both", alpha=0.25, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def write_summary(path: Path, table: pd.DataFrame) -> None:
    view = table[[
        "window_s",
        "dataset",
        "target",
        "mae_log10_target_metadata",
        "mae_log10_target_combined",
        "mae_reduction_pct",
        "q95_abs_residual_metadata",
        "q95_abs_residual_combined",
        "q95_reduction_pct",
        "r2_log10_target_combined",
    ]].copy()
    float_cols = [col for col in view.columns if col != "window_s" and view[col].dtype.kind in "fc"]
    for col in float_cols:
        view[col] = view[col].map(lambda value: f"{value:.3f}")
    headers = list(view.columns)
    table_lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in view.iterrows():
        table_lines.append("| " + " | ".join(str(row[col]) for col in headers) + " |")
    lines = [
        "# Early-Window Residual Evolution Summary",
        "",
        "Date: 2026-06-14",
        "",
        "Residual definition: predicted log10 target minus observed log10 target.",
        "",
        "The table compares metadata-only HGB against metadata plus early waveform features across 1 s, 3 s, and 10 s post-P windows.",
        "",
        "\n".join(table_lines),
        "",
        "Interpretation:",
        "",
        "1. Early waveform information improves mean and tail residuals at every tested window.",
        "2. Longer windows generally provide larger gains, especially for K-NET PGA and InstanceGM PGV.",
        "3. The 1 s window already adds signal, which supports a lead-time-dependent interpretation rather than a full-record leakage explanation.",
        "4. K-NET PGA retains a distance-dependent residual tail after waveform features, making it a strong residual-audit target.",
        "",
    ]
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("outputs/figures/ground_motion_audit"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/early_window_residual_evolution_summary.md"))
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)

    metrics = load_metrics(WINDOW_DIRS)
    bins = load_bins(WINDOW_DIRS)
    table = comparison_table(metrics)
    comparison_path = args.out_dir / "early_window_residual_evolution_metrics.csv"
    table.to_csv(comparison_path, index=False)

    fig, axes = plt.subplots(2, 2, figsize=(13.0, 8.2), dpi=180)
    plot_metric_lines(
        axes[0, 0],
        table,
        "mae_reduction_pct",
        "MAE reduction (%)",
        "Mean residual reduction from early waveform features",
    )
    plot_metric_lines(
        axes[0, 1],
        table,
        "q95_reduction_pct",
        "q95 abs residual reduction (%)",
        "Tail residual reduction from early waveform features",
    )
    plot_metric_lines(
        axes[1, 0],
        table,
        "mae_log10_target_combined",
        "combined MAE (log10 target)",
        "Combined model error across early windows",
    )
    plot_distance_bins(axes[1, 1], bins)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=6, frameon=False, fontsize=8)
    fig.suptitle("Early-window ground-motion residual evolution", x=0.02, y=0.995, ha="left", fontsize=14)
    fig.tight_layout(rect=[0.0, 0.06, 1.0, 0.96])
    out_path = args.out_dir / "early_window_residual_evolution_panel.png"
    fig.savefig(out_path)
    plt.close(fig)

    write_summary(args.summary, table)
    print(f"wrote {out_path}")
    print(f"wrote {comparison_path}")
    print(f"wrote {args.summary}")


if __name__ == "__main__":
    main()
