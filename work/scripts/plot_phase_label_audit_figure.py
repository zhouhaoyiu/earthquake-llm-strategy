#!/usr/bin/env python3
"""Plot the cross-dataset phase-label audit."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATASET_ORDER = ["stead", "instancegm", "iquique", "knet"]
DATASET_LABEL = {"stead": "STEAD", "instancegm": "InstanceGM", "iquique": "Iquique", "knet": "K-NET"}
MODEL_LABEL = {"phasenet_stead": "PhaseNet", "eqtransformer_stead": "EQTransformer"}
COLORS = {"PhaseNet": "#c55a32", "EQTransformer": "#3b7ea1"}


def load_table(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["dataset_label"] = df["dataset"].map(DATASET_LABEL)
    df["model_label"] = df["model"].map(MODEL_LABEL)
    df["dataset_order"] = df["dataset"].map({name: idx for idx, name in enumerate(DATASET_ORDER)})
    return df.sort_values(["dataset_order", "phase", "model_label"]).reset_index(drop=True)


def style(ax: plt.Axes) -> None:
    ax.grid(True, axis="y", alpha=0.25, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_metric(ax: plt.Axes, df: pd.DataFrame, phase: str, metric: str, ylabel: str, title: str) -> None:
    sub = df[df["phase"] == phase]
    labels = [DATASET_LABEL[name] for name in DATASET_ORDER]
    x = np.arange(len(labels))
    width = 0.34
    for offset, model in [(-width / 2, "PhaseNet"), (width / 2, "EQTransformer")]:
        model_sub = sub[sub["model_label"] == model].set_index("dataset").reindex(DATASET_ORDER)
        ax.bar(x + offset, model_sub[metric], width=width, label=model, color=COLORS[model])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontsize=11)
    style(ax)


def write_summary(path: Path, df: pd.DataFrame, fig_path: Path, csv_path: Path) -> None:
    pn_knet_p = df[(df["model"] == "phasenet_stead") & (df["dataset"] == "knet") & (df["phase"] == "P")].iloc[0]
    inst_s = df[(df["dataset"] == "instancegm") & (df["phase"] == "S")]
    worst_missing = inst_s.loc[inst_s["missing_rate"].idxmax()]
    lines = [
        "# Figure 6 Phase-Label Audit",
        "",
        "Date: 2026-06-18",
        "",
        "Figure 6 summarizes the 1,000-record-per-dataset phase-label audit for pretrained PhaseNet(STEAD) and EQTransformer(STEAD).",
        "",
        f"- K-NET P alignment is stable for PhaseNet: MAE {pn_knet_p['mae']:.3f} s, missing rate {pn_knet_p['missing_rate']:.3f}.",
        f"- InstanceGM S picks have the largest missing-pick risk: {worst_missing['model_label']} missing rate {worst_missing['missing_rate']:.3f}.",
        "- The phase audit supports P-aligned early-window extraction and separates label-domain risk from strong-motion performance.",
        "",
        f"Figure: `{fig_path}`",
        f"CSV: `{csv_path}`",
        "",
    ]
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("outputs/figures/phase_audit/phase_audit_1000_table.csv"))
    parser.add_argument("--figure", type=Path, default=Path("outputs/figures/figure6_phase_label_audit.png"))
    parser.add_argument("--csv", type=Path, default=Path("outputs/figure6_phase_label_audit.csv"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/figure6_phase_label_audit_summary.md"))
    args = parser.parse_args()

    args.figure.parent.mkdir(parents=True, exist_ok=True)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)

    df = load_table(args.input)
    assert len(df) == 16, len(df)
    df.to_csv(args.csv, index=False)

    fig, axes = plt.subplots(2, 3, figsize=(13.2, 7.8), dpi=180)
    plot_metric(axes[0, 0], df, "P", "mae", "MAE (s)", "a  P-pick MAE")
    plot_metric(axes[0, 1], df, "P", "q95_abs", "q95 abs error (s)", "b  P-pick tail error")
    plot_metric(axes[0, 2], df, "P", "missing_rate", "missing rate", "c  P-pick missing rate")
    plot_metric(axes[1, 0], df, "S", "mae", "MAE (s)", "d  S-pick MAE")
    plot_metric(axes[1, 1], df, "S", "q95_abs", "q95 abs error (s)", "e  S-pick tail error")
    plot_metric(axes[1, 2], df, "S", "missing_rate", "missing rate", "f  S-pick missing rate")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False, fontsize=9)
    fig.suptitle("Cross-dataset phase-label audit", x=0.02, y=0.995, ha="left", fontsize=14)
    fig.tight_layout(rect=[0, 0.06, 1, 0.96])
    fig.savefig(args.figure)
    plt.close(fig)

    write_summary(args.summary, df, args.figure, args.csv)
    print(f"wrote {args.figure}")
    print(f"wrote {args.csv}")
    print(f"wrote {args.summary}")


if __name__ == "__main__":
    main()
