#!/usr/bin/env python3
"""Summarize 1/3/10 s cross-region transfer boundaries."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


RUNS = {
    1: Path("work/cross_region_waveform_transfer_1s/cross_region_waveform_transfer_boundary.csv"),
    3: Path("work/cross_region_waveform_transfer_3s/cross_region_waveform_transfer_boundary.csv"),
    10: Path("work/cross_region_waveform_transfer/cross_region_waveform_transfer_boundary.csv"),
}
OUT_CSV = Path("work/cross_region_waveform_transfer_window_scan.csv")
OUT_FIG = Path("outputs/figures/ground_motion_audit/cross_region_waveform_transfer_window_scan.png")
OUT_MD = Path("outputs/cross_region_waveform_transfer_window_scan_summary.md")


def main() -> None:
    frames = []
    for window, path in RUNS.items():
        df = pd.read_csv(path)
        df["window_s"] = window
        frames.append(df)
    all_rows = pd.concat(frames, ignore_index=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    all_rows.to_csv(OUT_CSV, index=False)

    agg = (
        all_rows.groupby(["window_s", "calibration"], as_index=False)["mae_ratio_vs_within_target"]
        .median()
        .sort_values(["calibration", "window_s"])
    )

    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    colors = {"source_only": "#b65f2a", "target_offset_calibrated": "#31688e"}
    names = {"source_only": "zero-shot", "target_offset_calibrated": "offset calibrated"}
    for cal in ["source_only", "target_offset_calibrated"]:
        sub = agg[agg["calibration"].eq(cal)]
        ax.plot(
            sub["window_s"],
            sub["mae_ratio_vs_within_target"],
            marker="o",
            linewidth=2.2,
            color=colors[cal],
            label=names[cal],
        )
    ax.axhline(1.0, color="#222222", linewidth=1.0, linestyle="--")
    ax.set_xticks([1, 3, 10])
    ax.set_xlabel("P-window length after pick (s)")
    ax.set_ylabel("Median MAE ratio vs target-domain model")
    ax.set_title("Cross-region transfer penalty grows with longer windows", loc="left", fontsize=12)
    ax.legend(frameon=False)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8, alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT_FIG, dpi=220)
    plt.close(fig)

    direct = agg[agg["calibration"].eq("source_only")]
    cal = agg[agg["calibration"].eq("target_offset_calibrated")]
    lines = [
        "# Cross-region Transfer Window Scan",
        "",
        "This summary combines the 1, 3, and 10 s cross-region early-waveform transfer checks.",
        "",
        "| Window | Zero-shot median ratio | Offset-calibrated median ratio |",
        "|---:|---:|---:|",
    ]
    for window in [1, 3, 10]:
        d = direct[direct["window_s"].eq(window)]["mae_ratio_vs_within_target"].iloc[0]
        c = cal[cal["window_s"].eq(window)]["mae_ratio_vs_within_target"].iloc[0]
        lines.append(f"| {window}s | {d:.2f} | {c:.2f} |")
    lines.extend(
        [
            "",
            "Interpretation:",
            "- All cross-domain rows remain worse than target-domain training.",
            "- The median transfer penalty increases from 1 s to 10 s, indicating that longer-window amplitude structure is more region- and measurement-system dependent.",
            "- Offset calibration helps at every window but does not remove the transfer boundary.",
            "",
            "Files:",
            f"- `{OUT_CSV}`",
            f"- `{OUT_FIG}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
