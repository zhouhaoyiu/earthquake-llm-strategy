#!/usr/bin/env python3
"""Plot OpenQuake reference and split-conformal uncertainty."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ORDER = ["InstanceGM PGA", "InstanceGM PGV", "InstanceGM SA03", "InstanceGM SA10", "InstanceGM SA30", "K-NET PGA"]


def labels(df: pd.DataFrame) -> pd.Series:
    dataset = df["dataset"].replace({"instancegm": "InstanceGM", "knet": "K-NET"})
    return dataset + " " + df["target"].str.upper()


def style(ax: plt.Axes) -> None:
    ax.grid(True, axis="y", alpha=0.25, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def load_tables(openquake_path: Path, conformal_path: Path) -> pd.DataFrame:
    oq = pd.read_csv(openquake_path)
    cf = pd.read_csv(conformal_path)
    oq["label"] = labels(oq)
    cf["label"] = labels(cf)
    out = oq.merge(cf[["label", "coverage", "interval_width", "q90_abs_residual", "mae"]], on="label", how="inner")
    out["label"] = pd.Categorical(out["label"], ORDER, ordered=True)
    out = out.sort_values("label").reset_index(drop=True)
    assert len(out) == 6, len(out)
    assert out["label"].notna().all()
    return out


def plot_mae(ax: plt.Axes, df: pd.DataFrame) -> None:
    x = np.arange(len(df))
    width = 0.25
    ax.bar(x - width, df["boore2014_mae"], width, label="Boore2014", color="#8c6d31")
    ax.bar(x, df["metadata_hgb_mae"], width, label="metadata HGB", color="#4c78a8")
    ax.bar(x + width, df["combined_mae"], width, label="metadata + early waveform", color="#c55a32")
    ax.set_xticks(x)
    ax.set_xticklabels(df["label"], rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("MAE (log10 target)")
    ax.set_title("a  Classical reference versus early waveform model", loc="left", fontsize=11)
    ax.legend(frameon=False, fontsize=8)
    style(ax)


def plot_reduction(ax: plt.Axes, df: pd.DataFrame) -> None:
    ax.bar(np.arange(len(df)), df["combined_vs_boore_reduction_pct"], color="#6b9ac4")
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_xticks(np.arange(len(df)))
    ax.set_xticklabels(df["label"], rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("MAE reduction vs Boore2014 (%)")
    ax.set_title("b  Bias-corrected OpenQuake comparison", loc="left", fontsize=11)
    style(ax)


def plot_coverage(ax: plt.Axes, df: pd.DataFrame) -> None:
    colors = np.where(df["coverage"] >= 0.9, "#5b8a5a", "#c55a32")
    ax.bar(np.arange(len(df)), df["coverage"], color=colors)
    ax.axhline(0.9, color="#333333", linestyle="--", linewidth=1.0, label="nominal 90%")
    ax.set_ylim(0.75, 0.96)
    ax.set_xticks(np.arange(len(df)))
    ax.set_xticklabels(df["label"], rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("held-station coverage")
    ax.set_title("c  Split-conformal coverage is target dependent", loc="left", fontsize=11)
    ax.legend(frameon=False, fontsize=8)
    style(ax)


def plot_width(ax: plt.Axes, df: pd.DataFrame) -> None:
    x = np.arange(len(df))
    width = 0.35
    ax.bar(x - width / 2, df["interval_width"], width, label="90% interval width", color="#9b7ab8")
    ax.bar(x + width / 2, df["mae"], width, label="conformal model MAE", color="#7aa974")
    ax.set_xticks(x)
    ax.set_xticklabels(df["label"], rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("log10 target units")
    ax.set_title("d  Interval width tracks residual scale", loc="left", fontsize=11)
    ax.legend(frameon=False, fontsize=8)
    style(ax)


def write_summary(path: Path, df: pd.DataFrame, fig_path: Path, csv_path: Path) -> None:
    best = df.loc[df["combined_vs_boore_reduction_pct"].idxmax()]
    low = df.loc[df["coverage"].idxmin()]
    lines = [
        "# Figure 4 Classical Reference And Uncertainty",
        "",
        "Date: 2026-06-18",
        "",
        "Figure 4 combines the bias-corrected OpenQuake BooreEtAl2014 comparison with split-conformal intervals on the balanced held-station split.",
        "",
        f"- Largest MAE reduction versus BooreEtAl2014: {best['label']}, {best['combined_vs_boore_reduction_pct']:.1f}%.",
        f"- Lowest nominal 90% conformal coverage: {low['label']}, coverage {low['coverage']:.3f}.",
        "- The OpenQuake comparison uses source distance as an Rjb proxy, rake 0, Vs30 760 m/s where missing, and train-set median bias correction.",
        "- The conformal result should be reported as target-dependent calibration under station shift.",
        "",
        f"Figure: `{fig_path}`",
        f"CSV: `{csv_path}`",
        "",
    ]
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--openquake", type=Path, default=Path("work/ground_motion_balanced_station_10s/openquake_comparison.csv"))
    parser.add_argument("--conformal", type=Path, default=Path("work/ground_motion_balanced_station_10s/conformal_intervals.csv"))
    parser.add_argument("--figure", type=Path, default=Path("outputs/figures/figure4_classical_uncertainty.png"))
    parser.add_argument("--csv", type=Path, default=Path("outputs/figure4_classical_uncertainty.csv"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/figure4_classical_uncertainty_summary.md"))
    args = parser.parse_args()

    args.figure.parent.mkdir(parents=True, exist_ok=True)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)

    df = load_tables(args.openquake, args.conformal)
    df.to_csv(args.csv, index=False)

    fig, axes = plt.subplots(2, 2, figsize=(13.0, 8.2), dpi=180)
    plot_mae(axes[0, 0], df)
    plot_reduction(axes[0, 1], df)
    plot_coverage(axes[1, 0], df)
    plot_width(axes[1, 1], df)
    fig.suptitle("Classical reference and calibrated uncertainty", x=0.02, y=0.995, ha="left", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(args.figure)
    plt.close(fig)

    write_summary(args.summary, df, args.figure, args.csv)
    print(f"wrote {args.figure}")
    print(f"wrote {args.csv}")
    print(f"wrote {args.summary}")


if __name__ == "__main__":
    main()
