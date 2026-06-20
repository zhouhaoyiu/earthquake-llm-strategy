#!/usr/bin/env python3
"""Audit whether early windows already contain target-scale PGA amplitudes."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


OUT_CSV = Path("outputs/early_window_peak_capture_audit.csv")
OUT_MD = Path("outputs/early_window_peak_capture_audit.md")


def row(dataset: str, window: int) -> dict:
    df = pd.read_csv(f"work/ground_motion_baseline_multi_{window}s/{dataset}_test_features.csv")
    sub = df.dropna(subset=["target_pga", "target_log10_pga", "h_early_absmax"]).copy()
    sub = sub[(sub["target_pga"] > 0) & (sub["h_early_absmax"] >= 0)]
    ratio = sub["h_early_absmax"] / sub["target_pga"]
    return {
        "dataset": dataset,
        "window_s": window,
        "n": int(len(sub)),
        "ratio_median": float(ratio.median()),
        "ratio_q75": float(ratio.quantile(0.75)),
        "ratio_q90": float(ratio.quantile(0.90)),
        "frac_ratio_ge_0p5": float((ratio >= 0.5).mean()),
        "frac_ratio_ge_0p8": float((ratio >= 0.8).mean()),
        "frac_ratio_ge_1p0": float((ratio >= 1.0).mean()),
        "spearman_h_absmax_log10_pga": float(sub["h_early_absmax"].corr(sub["target_log10_pga"], method="spearman")),
    }


def main() -> None:
    rows = [row(dataset, window) for dataset in ["instancegm", "knet"] for window in [1, 3, 10]]
    out = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)

    knet10 = out[(out.dataset == "knet") & (out.window_s == 10)].iloc[0]
    knet1 = out[(out.dataset == "knet") & (out.window_s == 1)].iloc[0]
    inst10 = out[(out.dataset == "instancegm") & (out.window_s == 10)].iloc[0]
    lines = [
        "# Early-Window Peak-Capture Audit",
        "",
        "Date: 2026-06-18",
        "",
        "This audit compares early-window horizontal peak amplitude (`h_early_absmax`) with the full-record PGA target in the existing random-split test feature tables.",
        "",
        "## Key Results",
        "",
        f"- K-NET 1 s: median early/target ratio {knet1['ratio_median']:.2f}; fraction >= 0.8 is {knet1['frac_ratio_ge_0p8']:.3f}.",
        f"- K-NET 10 s: median early/target ratio {knet10['ratio_median']:.2f}; fraction >= 0.8 is {knet10['frac_ratio_ge_0p8']:.3f}.",
        f"- InstanceGM 10 s direct amplitude ratio median is {inst10['ratio_median']:.6f}, indicating that waveform amplitudes and PGA targets are not on a directly comparable scale in the local feature table.",
        "",
        "## Interpretation",
        "",
        "K-NET PGA results should be framed as early-window strong-motion information, with a clear note that 10 s windows often contain target-scale horizontal amplitudes. The 1 s and 3 s windows remain important for lead-time-sensitive interpretation. InstanceGM should not use direct early/target amplitude ratios without unit reconciliation; its evidence should rely on held-out prediction, residual, and calibration metrics.",
        "",
        f"CSV: `{OUT_CSV}`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines))
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
