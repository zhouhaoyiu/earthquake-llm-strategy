#!/usr/bin/env python3
"""Build feature-group ablation tables from existing held-out metrics."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


OUT_CSV = Path("outputs/feature_group_ablation_table.csv")
SUMMARY = Path("outputs/feature_group_ablation_summary.md")
FIGURE = Path("outputs/figures/ground_motion_audit/feature_group_ablation.png")


def reduction(old: float, new: float) -> float:
    return (old - new) / old * 100.0


def main_rows() -> pd.DataFrame:
    frames = []
    for root in sorted(Path("work").glob("ground_motion_balanced_station_*s")):
        path = root / "ground_motion_heldout_results.csv"
        if path.exists():
            frames.append(pd.read_csv(path))
    df = pd.concat(frames, ignore_index=True)
    df = df[~df.get("skipped", False).astype(bool)].copy()
    df = df[pd.to_numeric(df["mae_log10_target"], errors="coerce").notna()].copy()
    rows = []
    for key, sub in df.groupby(["dataset", "target", "early_seconds"]):
        pivot = sub.set_index("feature_set")["mae_log10_target"]
        if {"median", "metadata_only", "early_waveform_only", "metadata_plus_early_waveform"} <= set(pivot.index):
            rows += [
                {
                    "scope": "instancegm_knet_station",
                    "dataset": key[0],
                    "target": key[1],
                    "holdout": "station",
                    "early_seconds": key[2],
                    "comparison": "metadata_vs_median",
                    "reduction_pct": reduction(pivot["median"], pivot["metadata_only"]),
                },
                {
                    "scope": "instancegm_knet_station",
                    "dataset": key[0],
                    "target": key[1],
                    "holdout": "station",
                    "early_seconds": key[2],
                    "comparison": "p_waveform_vs_median",
                    "reduction_pct": reduction(pivot["median"], pivot["early_waveform_only"]),
                },
                {
                    "scope": "instancegm_knet_station",
                    "dataset": key[0],
                    "target": key[1],
                    "holdout": "station",
                    "early_seconds": key[2],
                    "comparison": "metadata_plus_p_vs_metadata",
                    "reduction_pct": reduction(pivot["metadata_only"], pivot["metadata_plus_early_waveform"]),
                },
            ]
    return pd.DataFrame(rows)


def esm_rows() -> pd.DataFrame:
    path = Path("work/esm_heldout_baseline/esm_heldout_metrics.csv")
    df = pd.read_csv(path)
    rows = []
    for key, sub in df.groupby(["holdout", "target", "early_seconds"]):
        pivot = sub.set_index("feature_set")["mae_log10_target"]
        if {"median", "p_waveform_only", "p_waveform_plus_distance", "p_waveform_distance_site"} <= set(pivot.index):
            base = {"scope": "esm", "dataset": "esm", "holdout": key[0], "target": key[1], "early_seconds": key[2]}
            rows += [
                {**base, "comparison": "p_waveform_vs_median", "reduction_pct": reduction(pivot["median"], pivot["p_waveform_only"])},
                {**base, "comparison": "distance_added_to_p", "reduction_pct": reduction(pivot["p_waveform_only"], pivot["p_waveform_plus_distance"])},
                {**base, "comparison": "site_added_to_p_distance", "reduction_pct": reduction(pivot["p_waveform_plus_distance"], pivot["p_waveform_distance_site"])},
                {**base, "comparison": "p_distance_site_vs_median", "reduction_pct": reduction(pivot["median"], pivot["p_waveform_distance_site"])},
            ]
    return pd.DataFrame(rows)


def aq_rows() -> pd.DataFrame:
    path = Path("work/aq2009gm_full_stream_validation_2s5s/aq2009gm_full_stream_comparison.csv")
    df = pd.read_csv(path)
    rows = []
    for row in df.itertuples(index=False):
        rows.append(
            {
                "scope": "aq2009gm",
                "dataset": row.dataset,
                "holdout": row.holdout,
                "target": row.target,
                "early_seconds": row.early_seconds,
                "comparison": "metadata_plus_p_vs_metadata",
                "reduction_pct": row.mae_reduction_pct,
            }
        )
    return pd.DataFrame(rows)


def write_summary(table: pd.DataFrame) -> None:
    main = table[table["scope"].eq("instancegm_knet_station")]
    esm = table[table["scope"].eq("esm")]
    aq = table[table["scope"].eq("aq2009gm")]
    lines = [
        "# Feature-group ablation summary",
        "",
        "This audit combines existing held-out metrics. It does not retrain models.",
        "",
        "## InstanceGM and K-NET held-station",
        "",
        "| Window | Comparison | Median reduction | Range |",
        "|---:|---|---:|---:|",
    ]
    for (window, comp), sub in main.groupby(["early_seconds", "comparison"]):
        lines.append(f"| {window:g}s | {comp} | {sub.reduction_pct.median():.1f}% | {sub.reduction_pct.min():.1f} to {sub.reduction_pct.max():.1f}% |")
    lines += ["", "## ESM information increments", "", "| Holdout | Window | Comparison | Median reduction |", "|---|---:|---|---:|"]
    for (holdout, window, comp), sub in esm.groupby(["holdout", "early_seconds", "comparison"]):
        lines.append(f"| {holdout} | {window:g}s | {comp} | {sub.reduction_pct.median():.1f}% |")
    lines += ["", "## AQ2009GM metadata plus P-window", "", "| Holdout | Window | Median reduction |", "|---|---:|---:|"]
    for (holdout, window), sub in aq.groupby(["holdout", "early_seconds"]):
        lines.append(f"| {holdout} | {window:g}s | {sub.reduction_pct.median():.1f}% |")
    lines += [
        "",
        "Interpretation: early P-window features add information beyond metadata in the main held-station benchmark and AQ2009GM. In ESM, distance gives a large additional gain over P-only features. Site metadata gives a smaller, split- and window-dependent increment, including near-zero or slightly negative station-held increments in short windows. This supports feature-group wording in the manuscript without claiming that site effects are fully solved.",
        "",
        "Files:",
        f"- `{OUT_CSV}`",
        f"- `{FIGURE}`",
    ]
    SUMMARY.write_text("\n".join(lines) + "\n")


def plot(table: pd.DataFrame) -> None:
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.1), constrained_layout=True)

    main = table[table["scope"].eq("instancegm_knet_station")]
    main_plot = (
        main[main["comparison"].isin(["p_waveform_vs_median", "metadata_plus_p_vs_metadata"])]
        .groupby(["early_seconds", "comparison"])["reduction_pct"]
        .median()
        .unstack()
    )
    axes[0].plot(main_plot.index, main_plot["p_waveform_vs_median"], marker="o", label="P only vs median")
    axes[0].plot(main_plot.index, main_plot["metadata_plus_p_vs_metadata"], marker="s", label="metadata + P vs metadata")
    axes[0].set_title("A. Main held-station")
    axes[0].set_xlabel("P-window length (s)")
    axes[0].set_ylabel("Median MAE reduction (%)")

    esm = table[(table["scope"].eq("esm")) & (table["holdout"].eq("station"))]
    esm_plot = esm.groupby(["early_seconds", "comparison"])["reduction_pct"].median().unstack()
    axes[1].plot(esm_plot.index, esm_plot["p_waveform_vs_median"], marker="o", label="P only")
    axes[1].plot(esm_plot.index, esm_plot["distance_added_to_p"], marker="s", label="+ distance")
    axes[1].plot(esm_plot.index, esm_plot["site_added_to_p_distance"], marker="^", label="+ site")
    axes[1].set_title("B. ESM station")
    axes[1].set_xlabel("P-window length (s)")

    aq = table[table["scope"].eq("aq2009gm")]
    aq_plot = aq.groupby(["early_seconds", "holdout"])["reduction_pct"].median().unstack()
    for holdout in aq_plot.columns:
        axes[2].plot(aq_plot.index, aq_plot[holdout], marker="o", label=holdout)
    axes[2].set_title("C. AQ2009GM")
    axes[2].set_xlabel("P-window length (s)")

    for ax in axes:
        ax.grid(True, axis="y", color="0.9")
        ax.axhline(0, color="0.25", linewidth=0.8)
        ax.legend(frameon=False, fontsize=8)
    fig.savefig(FIGURE, dpi=220)
    plt.close(fig)


def main() -> None:
    table = pd.concat([main_rows(), esm_rows(), aq_rows()], ignore_index=True)
    assert not table.empty
    assert table["reduction_pct"].notna().all()
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT_CSV, index=False)
    write_summary(table)
    plot(table)
    print(OUT_CSV)
    print(SUMMARY)
    print(FIGURE)


if __name__ == "__main__":
    main()
