#!/usr/bin/env python3
"""Redraw NC main figures from verified tables and existing audit panels."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


OUT = Path("outputs/figures")
BLUE = "#356f9f"
ORANGE = "#c45a32"
GREEN = "#5f8f5a"
PURPLE = "#7b63a6"
GRAY = "#777777"


def setup() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.dpi": 180,
            "savefig.dpi": 240,
            "axes.linewidth": 0.8,
        }
    )
    OUT.mkdir(parents=True, exist_ok=True)


def style(ax: plt.Axes, title: str, ylabel: str | None = None) -> None:
    ax.set_title(title, loc="left")
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.grid(axis="y", color="#dddddd", linewidth=0.7, alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def save(fig: plt.Figure, path: str) -> None:
    fig.tight_layout()
    fig.savefig(OUT / path)
    plt.close(fig)


def figure1() -> None:
    df = pd.read_csv("outputs/figure1_dataset_task_matrix.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.1))
    ax = axes[0]
    y = np.arange(len(df))
    colors = [GRAY if s else BLUE for s in df["supplement"]]
    ax.barh(y, df["records"] / 1000, color=colors)
    ax.set_yticks(y)
    ax.set_yticklabels(df["dataset"])
    ax.invert_yaxis()
    ax.set_xlabel("records (thousand)")
    style(ax, "A. Public waveform records")

    ax = axes[1]
    tasks = ["phase", "detect", "gm", "pga", "pgv", "sa"]
    mat = df[tasks].astype(int).to_numpy()
    ax.imshow(mat, cmap=matplotlib.colors.ListedColormap(["#f3f3f3", BLUE]), vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(len(tasks)))
    ax.set_xticklabels(["phase", "detect", "GM", "PGA", "PGV", "SA"], rotation=30, ha="right")
    ax.set_yticks(np.arange(len(df)))
    ax.set_yticklabels(df["dataset"])
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, "yes" if mat[i, j] else "", ha="center", va="center", color="white" if mat[i, j] else "#888888", fontsize=7)
    style(ax, "B. Task and target availability")
    save(fig, "figure1_dataset_task_matrix.png")


def figure2() -> None:
    df = pd.read_csv("outputs/figure2_early_window_performance.csv")
    series = df["series"].drop_duplicates().tolist()
    colors = [BLUE, ORANGE, GREEN]
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.4))
    for ax, metric, title, ylabel in [
        (axes[0, 0], "mae_reduction_pct", "A. Early-window MAE reduction", "MAE reduction (%)"),
        (axes[0, 1], "q95_reduction_pct", "B. Tail residual reduction", "q95 reduction (%)"),
        (axes[1, 0], "mae_log10_target_combined", "C. Combined-model error", "MAE (log10 target)"),
        (axes[1, 1], "r2_log10_target_combined", "D. Combined-model R2", "R2"),
    ]:
        for color, window in zip(colors, [1, 3, 10]):
            sub = df[df["window_s"].eq(window)].set_index("series").reindex(series)
            x = np.arange(len(series)) + {1: -0.24, 3: 0, 10: 0.24}[window]
            ax.bar(x, sub[metric], width=0.22, color=color, label=f"{window}s")
        ax.set_xticks(np.arange(len(series)))
        ax.set_xticklabels(series, rotation=35, ha="right")
        style(ax, title, ylabel)
    axes[0, 0].legend(frameon=False, ncol=3)
    save(fig, "figure2_early_window_performance.png")


def figure3() -> None:
    df = pd.read_csv("outputs/figure3_heldout_generalization.csv")
    dist = pd.read_csv("work/ground_motion_balanced_station_10s/balanced_station_distribution_audit.csv")
    labels = df["series"].drop_duplicates().tolist()
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.4))
    for ax, metric, title, ylabel in [
        (axes[0, 0], "mae_reduction_pct", "A. Held-out early-waveform gain", "MAE reduction (%)"),
        (axes[0, 1], "combined_r2", "B. Combined-model held-out skill", "R2"),
    ]:
        for color, split, off in [(BLUE, "held event", -0.18), (ORANGE, "held station", 0.18)]:
            sub = df[df["split"].eq(split)].set_index("series").reindex(labels)
            axes_flat_x = np.arange(len(labels)) + off
            ax.bar(axes_flat_x, sub[metric], width=0.34, color=color, label=split)
        ax.set_xticks(np.arange(len(labels)))
        ax.set_xticklabels(labels, rotation=35, ha="right")
        style(ax, title, ylabel)
    axes[0, 0].legend(frameon=False, ncol=2)

    variables = ["source_magnitude", "source_distance_km", "target_log10_pga"]
    names = ["magnitude", "distance", "log10 PGA"]
    x = np.arange(len(variables))
    for color, dataset, off in [(GREEN, "InstanceGM", -0.18), (PURPLE, "K-NET", 0.18)]:
        sub = dist[dist["dataset"].eq(dataset)].set_index("variable").reindex(variables)
        axes[1, 0].bar(x + off, sub["hist_overlap"], width=0.34, color=color, label=dataset)
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(names)
    axes[1, 0].set_ylim(0, 1.05)
    style(axes[1, 0], "C. Held-station distribution overlap", "histogram overlap")
    axes[1, 0].legend(frameon=False, ncol=2)

    view = dist.copy()
    view["shift"] = (view["test_median"] - view["train_median"]) / (view["train_q95"] - view["train_q05"]).replace(0, np.nan)
    rows = view[view["variable"].isin(variables)].copy()
    labels2 = rows["dataset"] + "\n" + rows["variable"].replace(dict(zip(variables, names)))
    axes[1, 1].bar(np.arange(len(rows)), rows["shift"], color=[GREEN if d == "InstanceGM" else PURPLE for d in rows["dataset"]])
    axes[1, 1].axhline(0, color="#333333", linewidth=0.8)
    axes[1, 1].set_xticks(np.arange(len(rows)))
    axes[1, 1].set_xticklabels(labels2, rotation=35, ha="right")
    style(axes[1, 1], "D. Normalized median shift", "shift / train 5-95%")
    save(fig, "figure3_heldout_generalization.png")


def figure4() -> None:
    df = pd.read_csv("outputs/figure4_classical_uncertainty.csv")
    labels = df["label"].tolist()
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.4))
    x = np.arange(len(df))
    w = 0.25
    axes[0, 0].bar(x - w, df["boore2014_mae"], w, label="Boore2014", color=GRAY)
    axes[0, 0].bar(x, df["metadata_hgb_mae"], w, label="metadata HGB", color=BLUE)
    axes[0, 0].bar(x + w, df["combined_mae"], w, label="metadata + waveform", color=ORANGE)
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=35, ha="right")
    style(axes[0, 0], "A. Classical reference comparison", "MAE")
    axes[0, 0].legend(frameon=False)

    axes[0, 1].bar(x, df["combined_vs_boore_reduction_pct"], color=BLUE)
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=35, ha="right")
    style(axes[0, 1], "B. Reduction versus Boore2014", "MAE reduction (%)")

    axes[1, 0].bar(x, df["coverage"], color=np.where(df["coverage"] >= 0.9, GREEN, ORANGE))
    axes[1, 0].axhline(0.9, color="#333333", linestyle="--", linewidth=1)
    axes[1, 0].set_ylim(0.75, 0.96)
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=35, ha="right")
    style(axes[1, 0], "C. Split-conformal coverage", "coverage")

    axes[1, 1].bar(x - 0.18, df["interval_width"], 0.34, color=PURPLE, label="interval width")
    axes[1, 1].bar(x + 0.18, df["mae"], 0.34, color=GREEN, label="MAE")
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=35, ha="right")
    style(axes[1, 1], "D. Interval width and residual scale", "log10 target")
    axes[1, 1].legend(frameon=False)
    save(fig, "figure4_classical_uncertainty.png")


def arial(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def figure5() -> None:
    main_panel = Path("outputs/figures/ground_motion_audit/ground_motion_residual_diagnostic_panel.png")
    case_panels = [
        ("A. Repeated InstanceGM high-residual records", Path("outputs/figures/ground_motion_audit/instancegm_repeated_residual_audit_panel.png")),
        ("B. K-NET PGA high-residual records", Path("outputs/figures/ground_motion_audit/knet_pga_worst_residual_audit_panel.png")),
    ]
    target_w = 2200
    pad, title_h, label_h = 36, 100, 56
    title_font, label_font = arial(54), arial(36)

    im = Image.open(main_panel).convert("RGB")
    im = im.resize((target_w, round(im.height * target_w / im.width)), Image.Resampling.LANCZOS)
    total_h = title_h + label_h + im.height + pad
    canvas = Image.new("RGB", (target_w + 2 * pad, total_h), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((pad, 22), "Residual diagnostics", fill="black", font=title_font)
    draw.text((pad, title_h + 8), "A. Error reduction, residual tails, and residual structure", fill="black", font=label_font)
    canvas.paste(im, (pad, title_h + label_h))
    canvas.save(OUT / "figure5_residual_waveform_audit.png")

    panels = []
    for label, path in case_panels:
        case = Image.open(path).convert("RGB")
        scale = target_w / case.width
        panels.append((label, case.resize((target_w, round(case.height * scale)), Image.Resampling.LANCZOS)))
    total_h = title_h + sum(panel.height + label_h + pad for _, panel in panels) + pad
    cases = Image.new("RGB", (target_w + 2 * pad, total_h), "white")
    draw = ImageDraw.Draw(cases)
    draw.text((pad, 22), "Waveform case audit", fill="black", font=title_font)
    y = title_h
    for label, panel in panels:
        draw.text((pad, y + 8), label, fill="black", font=label_font)
        cases.paste(panel, (pad, y + label_h))
        y += panel.height + label_h + pad
    cases.save(OUT / "extended_waveform_case_audit.png")

    Path("outputs/figure5_residual_waveform_audit_summary.md").write_text(
        "\n".join(
            [
                "# Figure 5 Residual Diagnostics",
                "",
                "Figure 5 now contains the residual diagnostic panel only, keeping the main text figure readable.",
                "",
                "- Main figure: `outputs/figures/figure5_residual_waveform_audit.png`",
                "- Extended waveform cases: `outputs/figures/extended_waveform_case_audit.png`",
                "",
                "The extended figure retains repeated InstanceGM high-residual records and K-NET PGA high-residual waveform cases.",
                "",
            ]
        )
    )


def figure6() -> None:
    df = pd.read_csv("outputs/figure6_phase_label_audit.csv")
    order = ["stead", "instancegm", "iquique", "knet"]
    labels = ["STEAD", "InstanceGM", "Iquique", "K-NET"]
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.2))
    specs = [
        ("P", "mae", "A. P-pick MAE", "MAE (s)"),
        ("P", "q95_abs", "B. P-pick tail error", "q95 abs error (s)"),
        ("P", "missing_rate", "C. P-pick missing rate", "missing rate"),
        ("S", "mae", "D. S-pick MAE", "MAE (s)"),
        ("S", "q95_abs", "E. S-pick tail error", "q95 abs error (s)"),
        ("S", "missing_rate", "F. S-pick missing rate", "missing rate"),
    ]
    for ax, (phase, metric, title, ylabel) in zip(axes.ravel(), specs):
        sub = df[df["phase"].eq(phase)]
        x = np.arange(len(order))
        for color, model, off in [(ORANGE, "PhaseNet", -0.18), (BLUE, "EQTransformer", 0.18)]:
            vals = sub[sub["model_label"].eq(model)].set_index("dataset").reindex(order)[metric]
            ax.bar(x + off, vals, width=0.34, color=color, label=model)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=25, ha="right")
        style(ax, title, ylabel)
    axes[0, 0].legend(frameon=False)
    save(fig, "figure6_phase_label_audit.png")


def main() -> None:
    setup()
    figure1()
    figure2()
    figure3()
    figure4()
    figure5()
    figure6()
    print("redrew Figures 1-6")


if __name__ == "__main__":
    main()
