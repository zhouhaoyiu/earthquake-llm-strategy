#!/usr/bin/env python3
"""Build source data for Figure 5 residual diagnostics."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path("work/ground_motion_residuals_10s")
OUT = Path("outputs/figure5_residual_diagnostic_source_data.csv")


def metric_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    df = pd.read_csv(ROOT / "ground_motion_residual_metric_deltas.csv")
    metrics = [
        "metadata_mae",
        "combined_mae",
        "mae_reduction_pct",
        "metadata_q95_abs",
        "combined_q95_abs",
        "q95_reduction_pct",
        "combined_r2",
        "combined_median_signed",
        "combined_overpredict_fraction",
    ]
    for row in df.to_dict("records"):
        for metric in metrics:
            rows.append(
                {
                    "panel": "A_error_reduction",
                    "source_table": "ground_motion_residual_metric_deltas.csv",
                    "dataset": row["dataset"],
                    "target": row["target"],
                    "feature_set": "metadata_plus_early_waveform",
                    "variable": "",
                    "bin": "",
                    "n": "",
                    "x_min": "",
                    "x_max": "",
                    "x_center": "",
                    "metric": metric,
                    "value": row[metric],
                    "notes": "Panel A metric or supporting metric.",
                }
            )
    return rows


def bin_rows() -> list[dict[str, object]]:
    df = pd.read_csv(ROOT / "ground_motion_residual_bins.csv")
    filters = [
        ("B_knet_distance", (df["dataset"] == "knet") & (df["target"] == "pga") & (df["feature_set"] == "metadata_plus_early_waveform") & (df["variable"] == "source_distance_km")),
        ("C_instancegm_depth", (df["dataset"] == "instancegm") & (df["feature_set"] == "metadata_plus_early_waveform") & (df["variable"] == "source_depth_km")),
        ("D_instancegm_early_amp", (df["dataset"] == "instancegm") & (df["feature_set"] == "metadata_plus_early_waveform") & (df["variable"] == "vec_early_absmax")),
    ]
    rows: list[dict[str, object]] = []
    for panel, mask in filters:
        sub = df[mask].copy()
        sub["x_center"] = (sub["x_min"] + sub["x_max"]) / 2.0
        for row in sub.to_dict("records"):
            for metric in ["median_signed_residual", "mean_signed_residual", "mae_residual", "q90_abs_residual", "overpredict_fraction"]:
                rows.append(
                    {
                        "panel": panel,
                        "source_table": "ground_motion_residual_bins.csv",
                        "dataset": row["dataset"],
                        "target": row["target"],
                        "feature_set": row["feature_set"],
                        "variable": row["variable"],
                        "bin": row["bin"],
                        "n": row["n"],
                        "x_min": row["x_min"],
                        "x_max": row["x_max"],
                        "x_center": row["x_center"],
                        "metric": metric,
                        "value": row[metric],
                        "notes": "Panel B-D binned residual diagnostic value.",
                    }
                )
    return rows


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out = pd.DataFrame(metric_rows() + bin_rows())
    expected_panels = {"A_error_reduction", "B_knet_distance", "C_instancegm_depth", "D_instancegm_early_amp"}
    assert set(out["panel"]) == expected_panels, sorted(set(out["panel"]))
    assert len(out) == 329, len(out)
    out.to_csv(OUT, index=False)
    print(f"Wrote {OUT} ({len(out)} rows)")


if __name__ == "__main__":
    main()
