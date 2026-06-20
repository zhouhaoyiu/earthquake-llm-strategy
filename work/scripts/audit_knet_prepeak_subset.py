#!/usr/bin/env python3
"""Audit K-NET PGA performance before early windows reach target-scale peaks."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


OUT_CSV = Path("outputs/knet_prepeak_subset_audit.csv")
OUT_MD = Path("outputs/knet_prepeak_subset_audit.md")


def summarize(window: int, threshold: float) -> dict:
    pred = pd.read_csv(f"work/ground_motion_residuals_{window}s/ground_motion_residual_predictions.csv")
    sub = pred[(pred["dataset"] == "knet") & (pred["target"] == "pga")].copy()
    sub["target_pga"] = 10 ** sub["actual_log10_target"]
    sub["early_target_ratio"] = sub["h_early_absmax"] / sub["target_pga"]
    sub = sub[sub["early_target_ratio"] < threshold]
    meta = sub[sub["feature_set"] == "metadata_only"]
    combo = sub[sub["feature_set"] == "metadata_plus_early_waveform"]
    mae_meta = float(meta["abs_residual_log10_target"].mean())
    mae_combo = float(combo["abs_residual_log10_target"].mean())
    q95_meta = float(meta["abs_residual_log10_target"].quantile(0.95))
    q95_combo = float(combo["abs_residual_log10_target"].quantile(0.95))
    return {
        "dataset": "knet",
        "target": "pga",
        "window_s": window,
        "threshold": threshold,
        "records": int(sub["global_id"].nunique()),
        "metadata_mae": mae_meta,
        "combined_mae": mae_combo,
        "mae_reduction_pct": (mae_meta - mae_combo) / mae_meta * 100.0,
        "metadata_q95_abs": q95_meta,
        "combined_q95_abs": q95_combo,
        "q95_reduction_pct": (q95_meta - q95_combo) / q95_meta * 100.0,
    }


def main() -> None:
    rows = [summarize(window, threshold) for window in [1, 3, 10] for threshold in [0.5, 0.8, 1.0]]
    df = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)

    r1 = df[(df.window_s == 1) & (df.threshold == 0.8)].iloc[0]
    r3 = df[(df.window_s == 3) & (df.threshold == 0.8)].iloc[0]
    r10 = df[(df.window_s == 10) & (df.threshold == 0.8)].iloc[0]
    lines = [
        "# K-NET Pre-Peak Subset Audit",
        "",
        "Date: 2026-06-18",
        "",
        "This audit evaluates K-NET PGA records where the early-window horizontal peak is below a fraction of the observed full-record PGA target. It uses existing residual prediction tables.",
        "",
        "## Main threshold: early/target ratio < 0.8",
        "",
        f"- 1 s: {r1['records']} records; metadata MAE {r1['metadata_mae']:.3f}; combined MAE {r1['combined_mae']:.3f}; reduction {r1['mae_reduction_pct']:.1f}%.",
        f"- 3 s: {r3['records']} records; metadata MAE {r3['metadata_mae']:.3f}; combined MAE {r3['combined_mae']:.3f}; reduction {r3['mae_reduction_pct']:.1f}%.",
        f"- 10 s: {r10['records']} records; metadata MAE {r10['metadata_mae']:.3f}; combined MAE {r10['combined_mae']:.3f}; reduction {r10['mae_reduction_pct']:.1f}%.",
        "",
        "## Interpretation",
        "",
        "The 1 s and 3 s pre-peak subsets support a lead-time-sensitive K-NET signal: early waveform features still reduce error when the early horizontal peak remains below 80% of the observed PGA. The 10 s pre-peak subset is small, so it is an audit result rather than a primary performance claim.",
        "",
        f"CSV: `{OUT_CSV}`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines))
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
