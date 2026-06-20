#!/usr/bin/env python3
"""Summarize held-station 1/2/3/5/10 s early-window gains."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


WINDOWS = [1, 2, 3, 5, 10]
OUT_CSV = Path("work/held_station_window_scan.csv")
OUT_MD = Path("outputs/held_station_window_scan_summary.md")
OUT_FIG = Path("outputs/figures/ground_motion_audit/held_station_window_scan.png")


def main() -> None:
    rows = []
    for window in WINDOWS:
        path = Path(f"work/ground_motion_balanced_station_{window}s/ground_motion_heldout_results.csv")
        df = pd.read_csv(path)
        keep = df[(df["holdout"].eq("station")) & (~df["skipped"].fillna(False))].copy()
        pivot = keep.pivot_table(
            index=["dataset", "target"],
            columns="feature_set",
            values=["mae_log10_target", "r2_log10_target", "group_overlap"],
            aggfunc="first",
        )
        pivot.columns = ["_".join(col).strip() for col in pivot.columns.to_flat_index()]
        pivot = pivot.reset_index()
        pivot["window_s"] = window
        pivot["mae_reduction_pct"] = (
            (pivot["mae_log10_target_metadata_only"] - pivot["mae_log10_target_metadata_plus_early_waveform"])
            / pivot["mae_log10_target_metadata_only"]
            * 100.0
        )
        rows.append(pivot)
    out = pd.concat(rows, ignore_index=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)

    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    for (dataset, target), sub in out.groupby(["dataset", "target"]):
        ax.plot(sub["window_s"], sub["mae_reduction_pct"], marker="o", linewidth=1.9, label=f"{dataset} {target}")
    ax.set_xticks(WINDOWS)
    ax.set_xlabel("P-window length after pick (s)")
    ax.set_ylabel("Held-station MAE reduction vs metadata (%)")
    ax.set_title("Early P-window information gain under held-station split", loc="left", fontsize=12)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_FIG, dpi=220)
    plt.close(fig)

    lines = [
        "# Held-Station Early-Window Scan",
        "",
        "This summary combines balanced held-station runs at 1, 2, 3, 5, and 10 s after the P pick.",
        "",
        "| Dataset | Target | 1s | 2s | 3s | 5s | 10s |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for (dataset, target), sub in out.groupby(["dataset", "target"]):
        values = {int(r.window_s): r.mae_reduction_pct for r in sub.itertuples(index=False)}
        lines.append(
            f"| {dataset} | {target} | "
            + " | ".join(f"{values[w]:.1f}%" for w in WINDOWS)
            + " |"
        )
    lines.extend(
        [
            "",
            "Files:",
            f"- `{OUT_CSV}`",
            f"- `{OUT_FIG}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")

    assert set(out["window_s"]) == set(WINDOWS)
    assert out.filter(like="group_overlap").fillna(0).eq(0).all().all()
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
