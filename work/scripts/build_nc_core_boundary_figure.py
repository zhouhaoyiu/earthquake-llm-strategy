#!/usr/bin/env python3
"""Build the compact NC predictability-boundary synthesis figure."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


WINDOWS = [1, 2, 3, 5, 10]
TRANSFER_RUNS = {
    1: Path("work/cross_region_waveform_transfer_esm_1s/cross_region_waveform_transfer_boundary.csv"),
    2: Path("work/cross_region_waveform_transfer_aq_esm_2s/cross_region_waveform_transfer_boundary.csv"),
    3: Path("work/cross_region_waveform_transfer_esm_3s/cross_region_waveform_transfer_boundary.csv"),
    5: Path("work/cross_region_waveform_transfer_aq_esm_5s/cross_region_waveform_transfer_boundary.csv"),
    10: Path("work/cross_region_waveform_transfer_esm_10s/cross_region_waveform_transfer_boundary.csv"),
}
OUT_CSV = Path("outputs/nc_core_predictability_boundary_table.csv")
OUT_MD = Path("outputs/nc_core_predictability_boundary_summary.md")
OUT_FIG = Path("outputs/figures/nc_core_predictability_boundary.png")


def main() -> None:
    table = pd.DataFrame({"window_s": WINDOWS})
    table = table.merge(within_gain(), on="window_s", how="left")
    table = table.merge(transfer_penalty(), on="window_s", how="left")
    table = table.merge(conformal_boundary(), on="window_s", how="left")
    table = table.merge(tail_boundary(), on="window_s", how="left")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT_CSV, index=False)
    write_summary(table)
    draw_figure(table)

    assert set(table["window_s"]) == set(WINDOWS)
    assert table["main_held_station_gain_pct"].dropna().gt(0).all()
    assert table["aq_station_gain_pct"].dropna().gt(0).all()
    assert table["zero_shot_transfer_ratio"].is_monotonic_increasing
    assert table["offset_transfer_ratio"].is_monotonic_increasing
    assert table.loc[table["window_s"].eq(5), "zero_shot_conformal_coverage"].iloc[0] < 0.4
    assert table.loc[table["window_s"].eq(2), "zero_shot_coverage_gap_to_90"].iloc[0] > 0.4
    assert table.loc[table["window_s"].eq(5), "zero_shot_coverage_gap_to_90"].iloc[0] > 0.5
    assert table.loc[table["window_s"].eq(5), "target_offset_interval_width"].iloc[0] > table.loc[
        table["window_s"].eq(5), "zero_shot_interval_width"
    ].iloc[0]
    assert (
        table.loc[table["window_s"].eq(5), "target_domain_top5_under_factor2_rate"].iloc[0]
        < table.loc[table["window_s"].eq(2), "target_domain_top5_under_factor2_rate"].iloc[0]
    )
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_FIG}")


def within_gain() -> pd.DataFrame:
    main = (
        pd.read_csv("work/held_station_window_scan.csv")
        .groupby("window_s", as_index=False)["mae_reduction_pct"]
        .median()
        .rename(columns={"mae_reduction_pct": "main_held_station_gain_pct"})
    )

    aq = pd.concat(
        [
            pd.read_csv("work/aq2009gm_full_stream_validation/aq2009gm_full_stream_comparison.csv"),
            pd.read_csv("work/aq2009gm_full_stream_validation_2s5s/aq2009gm_full_stream_comparison.csv"),
        ],
        ignore_index=True,
    )
    aq = (
        aq[aq["holdout"].eq("station")]
        .groupby("early_seconds", as_index=False)["mae_reduction_pct"]
        .median()
        .rename(columns={"early_seconds": "window_s", "mae_reduction_pct": "aq_station_gain_pct"})
    )
    aq["window_s"] = aq["window_s"].astype(int)

    esm = pd.read_csv("work/esm_heldout_baseline/esm_heldout_metrics.csv")
    station = esm[esm["holdout"].eq("station")]
    median = station[station["feature_set"].eq("median")].set_index(["target", "early_seconds"])["mae_log10_target"]
    site = station[station["feature_set"].eq("p_waveform_distance_site")].set_index(["target", "early_seconds"])[
        "mae_log10_target"
    ]
    esm_gain = ((median - site) / median * 100.0).rename("gain").reset_index()
    esm_gain = esm_gain.groupby("early_seconds", as_index=False)["gain"].median().rename(
        columns={"early_seconds": "window_s", "gain": "esm_station_gain_vs_median_pct"}
    )
    esm_gain["window_s"] = esm_gain["window_s"].astype(int)

    return main.merge(aq, on="window_s", how="outer").merge(esm_gain, on="window_s", how="outer")


def transfer_penalty() -> pd.DataFrame:
    rows = []
    for window, path in TRANSFER_RUNS.items():
        df = pd.read_csv(path)
        df = df[df["feature_set"].eq("log_waveform")]
        for calibration, name in [
            ("source_only", "zero_shot_transfer_ratio"),
            ("target_offset_calibrated", "offset_transfer_ratio"),
        ]:
            rows.append(
                {
                    "window_s": window,
                    name: df[df["calibration"].eq(calibration)]["mae_ratio_vs_within_target"].median(),
                }
            )
    return pd.DataFrame(rows).groupby("window_s", as_index=False).first()


def conformal_boundary() -> pd.DataFrame:
    df = pd.read_csv("work/nc_boundary_sensitivity/conformal_boundary.csv")
    grouped = df.groupby(["early_seconds", "mode"])
    cov = grouped["coverage90"].median().unstack()
    cov = cov.rename(
        columns={
            "target_domain": "target_domain_conformal_coverage",
            "zero_shot_source_conformal": "zero_shot_conformal_coverage",
            "target_offset_conformal": "target_offset_conformal_coverage",
        }
    )
    width = grouped["interval_width_log10"].median().unstack()
    width = width.rename(
        columns={
            "target_domain": "target_domain_interval_width",
            "zero_shot_source_conformal": "zero_shot_interval_width",
            "target_offset_conformal": "target_offset_interval_width",
        }
    )
    out = cov.join(width)
    for prefix in ["target_domain", "zero_shot", "target_offset"]:
        out[f"{prefix}_coverage_gap_to_90"] = 0.9 - out[f"{prefix}_conformal_coverage"]
    out.index = out.index.astype(int)
    return out.reset_index(names="window_s")


def tail_boundary() -> pd.DataFrame:
    df = pd.read_csv("work/nc_boundary_sensitivity/tail_underprediction.csv")
    df = df[df["tail_quantile"].eq(0.95)]
    tail = df.groupby(["early_seconds", "mode"])["under_factor2_rate"].median().unstack()
    tail = tail.rename(
        columns={
            "target_domain": "target_domain_top5_under_factor2_rate",
            "zero_shot_source_conformal": "zero_shot_top5_under_factor2_rate",
            "target_offset_conformal": "target_offset_top5_under_factor2_rate",
        }
    )
    tail.index = tail.index.astype(int)
    return tail.reset_index(names="window_s")


def write_summary(table: pd.DataFrame) -> None:
    lines = [
        "# NC Core Predictability-Boundary Synthesis",
        "",
        "This file is generated from existing validated outputs. It does not add a new model run.",
        "",
        "| Window | Main held-station gain % | AQ station gain % | ESM station gain vs median % | Zero-shot transfer ratio | Offset transfer ratio | Source coverage gap | Target-offset gap | Target-offset width | Target-domain top5 under-rate |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in table.itertuples(index=False):
        lines.append(
            f"| {row.window_s}s | {fmt(row.main_held_station_gain_pct, 1)} | "
            f"{fmt(row.aq_station_gain_pct, 1)} | {fmt(row.esm_station_gain_vs_median_pct, 1)} | "
            f"{fmt(row.zero_shot_transfer_ratio, 2)} | {fmt(row.offset_transfer_ratio, 2)} | "
            f"{fmt(row.zero_shot_coverage_gap_to_90, 3)} | {fmt(row.target_offset_coverage_gap_to_90, 3)} | "
            f"{fmt(row.target_offset_interval_width, 3)} | {fmt(row.target_domain_top5_under_factor2_rate, 3)} |"
        )
    lines.extend(
        [
            "",
            "Plain-language read:",
            "- Early-window information gain is consistently positive under held-station or held-station-like checks.",
            "- Cross-region transfer penalties grow from 1 s to 10 s, and offset calibration does not remove them.",
            "- Source-domain conformal intervals have large positive coverage gaps at 2 s and 5 s.",
            "- Target-offset calibration restores near-zero coverage gaps but changes interval width.",
            "- The strongest-shaking tail improves from 2 s to 5 s, but the top-tail underprediction boundary remains visible.",
            "",
            "Files:",
            f"- `{OUT_CSV}`",
            f"- `{OUT_FIG}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")


def draw_figure(table: pd.DataFrame) -> None:
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 8.1))
    ax1, ax2, ax3, ax4 = axes.ravel()

    ax1.plot(table["window_s"], table["main_held_station_gain_pct"], marker="o", label="InstanceGM/K-NET")
    ax1.plot(table["window_s"], table["aq_station_gain_pct"], marker="s", label="AQ2009GM")
    ax1.plot(table["window_s"], table["esm_station_gain_vs_median_pct"], marker="^", label="ESM")
    style_axis(ax1, "A. Within-domain information gain", "P-window length (s)", "MAE reduction (%)")
    ax1.set_xlabel("")
    ax1.legend(frameon=False, fontsize=8)

    ax2.plot(table["window_s"], table["zero_shot_transfer_ratio"], marker="o", color="#b65f2a", label="zero-shot")
    ax2.plot(table["window_s"], table["offset_transfer_ratio"], marker="s", color="#31688e", label="offset calibrated")
    ax2.axhline(1.0, color="#333333", linestyle="--", linewidth=1)
    style_axis(ax2, "B. Cross-region transfer boundary", "P-window length (s)", "MAE ratio vs target-domain")
    ax2.set_xlabel("")
    ax2.legend(frameon=False, fontsize=8)

    sub = table[table["window_s"].isin([2, 5])]
    x = sub["window_s"].astype(float)
    ax3.axhline(0.0, color="#333333", linestyle="--", linewidth=1, alpha=0.55, zorder=0)
    ax3.plot(x - 0.04, sub["zero_shot_coverage_gap_to_90"], marker="s", color="#b65f2a", label="source gap", zorder=3)
    ax3.plot(x + 0.04, sub["target_offset_coverage_gap_to_90"], marker="^", color="#2f7d4f", label="target-offset gap", zorder=3)
    ax3.set_ylim(-0.08, 0.68)
    ax3.set_xlim(1.75, 5.55)
    style_axis(ax3, "C. Uncertainty transfer boundary", "P-window length (s)", "0.90 - observed coverage")
    ax3b = ax3.twinx()
    ax3b.plot(x, sub["zero_shot_interval_width"], marker="s", color="#b65f2a", linestyle=":", label="source width")
    ax3b.plot(x, sub["target_offset_interval_width"], marker="^", color="#2f7d4f", linestyle=":", label="target-offset width")
    ax3b.set_ylabel("interval width (log10)")
    ax3b.set_ylim(0.5, 2.6)
    ax3b.spines["top"].set_visible(False)
    end = sub[sub["window_s"].eq(5)].iloc[0]
    ax3.text(5.08, end["zero_shot_coverage_gap_to_90"], "source gap", color="#b65f2a", va="center", fontsize=7)
    ax3.text(5.08, end["target_offset_coverage_gap_to_90"], "offset gap", color="#2f7d4f", va="center", fontsize=7)
    ax3b.text(5.08, end["zero_shot_interval_width"], "source width", color="#b65f2a", va="center", fontsize=7)
    ax3b.text(5.08, end["target_offset_interval_width"], "offset width", color="#2f7d4f", va="center", fontsize=7)

    ax4.plot(sub["window_s"], sub["target_domain_top5_under_factor2_rate"], marker="o", label="target-domain")
    ax4.plot(sub["window_s"], sub["zero_shot_top5_under_factor2_rate"], marker="s", label="zero-shot")
    ax4.set_ylim(0.0, 0.75)
    style_axis(ax4, "D. Strong-motion tail boundary", "P-window length (s)", "Top 5% factor-2 under-rate")
    ax4.legend(frameon=False, fontsize=8)

    for ax in axes.ravel():
        ax.set_xticks(WINDOWS if ax in [ax1, ax2] else [2, 5])
    fig.tight_layout(h_pad=2.8, w_pad=2.0)
    fig.savefig(OUT_FIG, dpi=240)
    plt.close(fig)


def style_axis(ax: plt.Axes, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(title, loc="left", fontsize=11)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8, alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def fmt(value: float, digits: int) -> str:
    if pd.isna(value):
        return "NA"
    return f"{value:.{digits}f}"


if __name__ == "__main__":
    main()
