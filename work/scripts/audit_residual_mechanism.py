#!/usr/bin/env python3
"""Summarize covariate shifts in the largest 10 s residuals."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


PRED = Path("work/ground_motion_residuals_10s/ground_motion_residual_predictions.csv")
OUT_CSV = Path("outputs/residual_mechanism_audit.csv")
OUT_CLASS_CSV = Path("outputs/residual_mechanism_classes.csv")
OUT_MD = Path("outputs/residual_mechanism_audit.md")
OUT_FIG = Path("outputs/figures/ground_motion_audit/residual_mechanism_audit.png")

FEATURES = [
    ("source_distance_km", "distance"),
    ("source_magnitude", "magnitude"),
    ("source_depth_km", "depth"),
    ("station_vs30_mps", "Vs30"),
    ("log10_vec_early_absmax", "early amp"),
    ("actual_log10_target", "target"),
]


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["log10_vec_early_absmax"] = np.log10(out["vec_early_absmax"].abs() + 1e-12)
    return out


def robust_shift(top: pd.Series, all_values: pd.Series) -> tuple[float, float, float, float]:
    all_values = pd.to_numeric(all_values, errors="coerce").dropna()
    top = pd.to_numeric(top, errors="coerce").dropna()
    if len(all_values) == 0 or len(top) == 0:
        return np.nan, np.nan, np.nan, np.nan
    q25, q75 = all_values.quantile([0.25, 0.75])
    iqr = float(q75 - q25)
    all_med = float(all_values.median())
    top_med = float(top.median())
    shift = top_med - all_med
    scaled = shift / iqr if iqr > 0 else np.nan
    return all_med, top_med, shift, scaled


def collect(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    combo = df[df["feature_set"].eq("metadata_plus_early_waveform")].copy()
    for (dataset, target), sub in combo.groupby(["dataset", "target"], sort=True):
        cutoff = sub["abs_residual_log10_target"].quantile(0.95)
        top = sub[sub["abs_residual_log10_target"].ge(cutoff)].copy()
        for col, label in FEATURES:
            all_med, top_med, shift, scaled = robust_shift(top[col], sub[col])
            rows.append(
                {
                    "dataset": dataset,
                    "target": target,
                    "series": f"{dataset} {target}",
                    "feature": label,
                    "top5_rows": int(len(top)),
                    "all_rows": int(len(sub)),
                    "all_median": all_med,
                    "top5_median": top_med,
                    "median_shift": shift,
                    "iqr_scaled_shift": scaled,
                    "top5_underprediction_fraction": float((top["residual_log10_target"] < 0).mean()),
                    "top5_median_abs_residual": float(top["abs_residual_log10_target"].median()),
                }
            )
    return pd.DataFrame(rows)


def mechanism_class(feature: str) -> tuple[str, str]:
    if feature == "distance":
        return (
            "path_attenuation_boundary",
            "Largest errors occur in a path-distance corner, consistent with attenuation and regional path effects not fully captured by early-window features.",
        )
    if feature == "target":
        return (
            "strong_motion_tail_boundary",
            "Largest errors occur in the upper target-amplitude tail, consistent with rare strong-motion outcomes that remain hard to infer from the early P window.",
        )
    if feature == "early amp":
        return (
            "early_amplitude_boundary",
            "Largest errors occur where early P amplitude itself is shifted, indicating that the early window carries information but still leaves ambiguous growth paths.",
        )
    if feature == "Vs30":
        return (
            "site_boundary",
            "Largest errors align with site-condition shifts, consistent with local amplification not fully resolved by the current site metadata.",
        )
    return (
        "source_geometry_boundary",
        "Largest errors align with source-side shifts, consistent with source metadata or rupture geometry remaining underspecified.",
    )


def build_class_table(table: pd.DataFrame) -> pd.DataFrame:
    top = (
        table.dropna(subset=["iqr_scaled_shift"])
        .assign(abs_shift=lambda x: x["iqr_scaled_shift"].abs())
        .sort_values(["series", "abs_shift"], ascending=[True, False])
        .groupby("series", as_index=False)
        .first()
    )
    rows = []
    for row in top.to_dict("records"):
        cls, interpretation = mechanism_class(str(row["feature"]))
        rows.append(
            {
                "series": row["series"],
                "dominant_feature": row["feature"],
                "mechanism_class": cls,
                "iqr_scaled_shift": row["iqr_scaled_shift"],
                "top5_underprediction_fraction": row["top5_underprediction_fraction"],
                "top5_median_abs_residual": row["top5_median_abs_residual"],
                "interpretation": interpretation,
                "claim_boundary": "structured residual association; not causal attribution",
            }
        )
    return pd.DataFrame(rows)


def write_summary(table: pd.DataFrame) -> None:
    top = build_class_table(table)
    lines = [
        "# Residual mechanism audit",
        "",
        "This audit compares the largest 5% of 10 s absolute residuals with all 10 s held-station residuals for the metadata-plus-early-waveform model.",
        "",
        "| series | dominant boundary | top shifted covariate | scaled median shift | top-5% underprediction fraction | top-5% median abs residual |",
        "|---|---|---|---:|---:|---:|",
    ]
    for row in top.to_dict("records"):
        lines.append(
            f"| {row['series']} | {row['mechanism_class']} | {row['dominant_feature']} | {row['iqr_scaled_shift']:.2f} | "
            f"{row['top5_underprediction_fraction']:.2f} | {row['top5_median_abs_residual']:.3f} |"
        )
    lines += [
        "",
        "Interpretation: large residuals separate into path-attenuation, strong-motion-tail and early-amplitude boundaries. This supports a structured residual claim: some held-station errors are tied to identifiable covariate regimes after the early-window model has used distance and site metadata. The audit reports associations, not causal attribution.",
        "",
        f"CSV: `{OUT_CSV}`",
        f"Class CSV: `{OUT_CLASS_CSV}`",
        f"Figure: `{OUT_FIG}`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines))


def plot(table: pd.DataFrame) -> None:
    top = (
        table.dropna(subset=["iqr_scaled_shift"])
        .assign(abs_shift=lambda x: x["iqr_scaled_shift"].abs())
        .sort_values(["series", "abs_shift"], ascending=[True, False])
        .groupby("series", as_index=False)
        .first()
    )
    labels = [s.replace("instancegm", "IGM").replace("knet", "K-NET").upper() for s in top["series"]]
    x = np.arange(len(top))
    colors = {
        "distance": "#4c78a8",
        "magnitude": "#72b7b2",
        "depth": "#54a24b",
        "Vs30": "#b279a2",
        "early amp": "#f58518",
        "target": "#e45756",
    }
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 6.0), dpi=180)
    axes[0].bar(x, top["iqr_scaled_shift"], color=[colors.get(f, "#777777") for f in top["feature"]])
    axes[0].axhline(0, color="#333333", linewidth=0.8)
    ymin = min(0.0, float(top["iqr_scaled_shift"].min()))
    ymax = max(0.0, float(top["iqr_scaled_shift"].max()))
    yspan = max(ymax - ymin, 1.0)
    label_offset = 0.05 * yspan
    axes[0].set_ylim(ymin - 0.12 * yspan, ymax + 0.28 * yspan)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=30, ha="right")
    axes[0].set_ylabel("dominant median shift / IQR")
    axes[0].set_title("A. Largest residual covariate shift", loc="left", pad=10)
    for i, row in enumerate(top.itertuples()):
        y = row.iqr_scaled_shift
        va = "bottom" if y >= 0 else "top"
        axes[0].text(
            i,
            y + (label_offset if y >= 0 else -label_offset),
            f"{row.feature}\n{y:.2f}",
            ha="center",
            va=va,
            fontsize=8,
        )

    axes[1].bar(x, top["top5_underprediction_fraction"], color="#6f6f6f")
    axes[1].axhline(0.5, color="#333333", linestyle="--", linewidth=0.8)
    axes[1].set_ylim(0, max(0.75, float(top["top5_underprediction_fraction"].max()) + 0.10))
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=30, ha="right")
    axes[1].set_ylabel("fraction")
    axes[1].set_title("B. Top-5% residuals that are underpredictions", loc="left", pad=10)
    for i, val in enumerate(top["top5_underprediction_fraction"]):
        axes[1].text(i, val + 0.015, f"{val:.2f}", ha="center", va="bottom", fontsize=8)
    for ax in axes:
        ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG)
    plt.close(fig)


def main() -> None:
    df = add_features(pd.read_csv(PRED))
    table = collect(df)
    classes = build_class_table(table)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT_CSV, index=False)
    classes.to_csv(OUT_CLASS_CSV, index=False)
    write_summary(table)
    plot(table)
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_CLASS_CSV}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_FIG}")


if __name__ == "__main__":
    main()
