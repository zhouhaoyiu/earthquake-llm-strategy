#!/usr/bin/env python3
"""Build an empirical predictability-boundary table from existing NC outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


OUT_CSV = Path("outputs/predictability_boundary_table.csv")
OUT_MD = Path("outputs/predictability_boundary_summary.md")


def fmt(x: float | int | None, digits: int = 3) -> str:
    if pd.isna(x):
        return "NA"
    return f"{float(x):.{digits}f}"


def main() -> None:
    fig2 = pd.read_csv("outputs/figure2_early_window_performance.csv")
    fig3 = pd.read_csv("outputs/figure3_heldout_generalization.csv")
    fig4 = pd.read_csv("outputs/figure4_classical_uncertainty.csv")

    random10 = fig2[fig2["window_s"] == 10].copy()
    event = fig3[fig3["holdout"] == "event"].copy()
    station = fig3[fig3["holdout"] == "station"].copy()

    table = random10[
        [
            "dataset",
            "target",
            "mae_log10_target_metadata",
            "mae_log10_target_combined",
            "q95_abs_residual_combined",
            "r2_log10_target_combined",
            "mae_reduction_pct",
        ]
    ].rename(
        columns={
            "mae_log10_target_metadata": "random10_metadata_mae",
            "mae_log10_target_combined": "random10_combined_mae",
            "q95_abs_residual_combined": "random10_q95_abs_residual",
            "r2_log10_target_combined": "random10_combined_r2",
            "mae_reduction_pct": "random10_mae_reduction_pct",
        }
    )

    for split_name, split_df in [("event", event), ("station", station)]:
        cols = split_df[
            [
                "dataset",
                "target",
                "combined_mae",
                "combined_r2",
                "mae_reduction_pct",
                "test_rows_combined",
                "group_overlap_combined",
            ]
        ].rename(
            columns={
                "combined_mae": f"held_{split_name}_combined_mae",
                "combined_r2": f"held_{split_name}_combined_r2",
                "mae_reduction_pct": f"held_{split_name}_mae_reduction_pct",
                "test_rows_combined": f"held_{split_name}_test_rows",
                "group_overlap_combined": f"held_{split_name}_group_overlap",
            }
        )
        table = table.merge(cols, on=["dataset", "target"], how="left")

    uncertainty = fig4[
        [
            "dataset",
            "target",
            "boore2014_mae",
            "combined_vs_boore_reduction_pct",
            "coverage",
            "interval_width",
            "q90_abs_residual",
        ]
    ].copy()
    uncertainty["coverage_gap_to_90"] = uncertainty["coverage"] - 0.9
    table = table.merge(uncertainty, on=["dataset", "target"], how="left")

    table["station_minus_random10_mae"] = table["held_station_combined_mae"] - table["random10_combined_mae"]
    table["robust_heldout_gain_pct"] = table[
        ["held_event_mae_reduction_pct", "held_station_mae_reduction_pct"]
    ].min(axis=1)
    table["empirical_boundary_note"] = table.apply(boundary_note, axis=1)
    table = table.sort_values(["dataset", "target"]).reset_index(drop=True)
    OUT_CSV.write_text(table.to_csv(index=False))

    aq = pd.read_csv("work/aq2009gm_chunks096-100_station12_baseline/aq2009gm_chunks096-100_comparison.csv")
    aq_best = aq[aq["early_seconds"] == 10].copy()
    aq_min_gain = aq_best.groupby("target")["mae_reduction_pct"].min().to_dict()

    strongest = table.sort_values("robust_heldout_gain_pct", ascending=False).iloc[0]
    weakest = table.sort_values("robust_heldout_gain_pct", ascending=True).iloc[0]
    under = table[table["coverage_gap_to_90"] < 0].copy()

    rows = [
        "# Predictability Boundary Summary",
        "",
        "This file is generated from existing figure tables. It does not add new model runs.",
        "",
        "## Main Boundary Table",
        "",
        "| Dataset | Target | Random 10 s MAE | Held-event MAE | Held-station MAE | Robust held-out gain % | Coverage | Coverage gap to 90% | Boundary note |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in table.itertuples(index=False):
        rows.append(
            "| "
            + " | ".join(
                [
                    str(r.dataset),
                    str(r.target),
                    fmt(r.random10_combined_mae),
                    fmt(r.held_event_combined_mae),
                    fmt(r.held_station_combined_mae),
                    fmt(r.robust_heldout_gain_pct, 1),
                    fmt(r.coverage, 3),
                    fmt(r.coverage_gap_to_90, 3),
                    str(r.empirical_boundary_note),
                ]
            )
            + " |"
        )

    rows.extend(
        [
            "",
            "## Manuscript Use",
            "",
            f"- Strongest robust held-out gain: {strongest.dataset} {strongest.target}, {strongest.robust_heldout_gain_pct:.1f}%.",
            f"- Weakest robust held-out gain: {weakest.dataset} {weakest.target}, {weakest.robust_heldout_gain_pct:.1f}%.",
            f"- Under-coverage targets at nominal 90%: {', '.join((under['dataset'] + ':' + under['target']).tolist()) or 'none'}.",
            "- Use the table to state empirical predictability boundaries: early windows improve point prediction, while held-station residuals and conformal coverage define the present limit.",
            "",
            "## AQ2009GM Supplement",
            "",
            f"- AQ2009GM 096-100 10 s minimum held-out gain: PGA {aq_min_gain.get('pga', float('nan')):.1f}%, PGV {aq_min_gain.get('pgv', float('nan')):.1f}%.",
            "- This remains a five-chunk aftershock supplement, not a full external-validation claim.",
        ]
    )
    OUT_MD.write_text("\n".join(rows) + "\n")

    assert len(table) == 6
    assert table["held_event_group_overlap"].eq(0).all()
    assert table["held_station_group_overlap"].eq(0).all()
    assert table["robust_heldout_gain_pct"].gt(0).all()
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")


def boundary_note(row: pd.Series) -> str:
    gain = row["robust_heldout_gain_pct"]
    gap = row["coverage_gap_to_90"]
    if gain >= 45 and gap >= 0:
        return "strong gain with calibrated station-shift interval"
    if gain >= 30:
        return "strong point gain; uncertainty remains target-dependent"
    if gain >= 20:
        return "useful point gain; boundary set by held-station residuals"
    return "limited robust gain; keep as target-dependent boundary case"


if __name__ == "__main__":
    main()
