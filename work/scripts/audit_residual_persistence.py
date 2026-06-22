#!/usr/bin/env python3
"""Audit whether large residuals persist as the P window lengthens."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


WINDOWS = [1, 3, 10]
ROOT = Path("work")
OUT_DIR = Path("outputs/figures/ground_motion_audit")
OUT_CSV = Path("outputs/residual_persistence_audit.csv")
OUT_MD = Path("outputs/residual_persistence_audit.md")


def load_predictions() -> pd.DataFrame:
    frames = []
    cols = [
        "global_id",
        "dataset",
        "target",
        "feature_set",
        "source_magnitude",
        "source_depth_km",
        "source_distance_km",
        "station_vs30_mps",
        "vec_early_absmax",
        "actual_log10_target",
        "residual_log10_target",
        "abs_residual_log10_target",
    ]
    for window in WINDOWS:
        path = ROOT / f"ground_motion_residuals_{window}s" / "ground_motion_residual_predictions.csv"
        df = pd.read_csv(path, usecols=cols)
        df = df[df["feature_set"].eq("metadata_plus_early_waveform")].copy()
        df["window_s"] = window
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def wide_table(df: pd.DataFrame) -> pd.DataFrame:
    key = ["global_id", "dataset", "target"]
    metric_cols = [
        "source_magnitude",
        "source_depth_km",
        "source_distance_km",
        "station_vs30_mps",
        "actual_log10_target",
    ]
    base = df[df["window_s"].eq(10)][key + metric_cols].copy()
    for window in WINDOWS:
        sub = df[df["window_s"].eq(window)][key + ["residual_log10_target", "abs_residual_log10_target", "vec_early_absmax"]]
        sub = sub.rename(
            columns={
                "residual_log10_target": f"residual_{window}s",
                "abs_residual_log10_target": f"abs_residual_{window}s",
                "vec_early_absmax": f"early_absmax_{window}s",
            }
        )
        base = base.merge(sub, on=key, how="inner")
    return base


def summarize(wide: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (dataset, target), sub in wide.groupby(["dataset", "target"], sort=True):
        q10 = sub["abs_residual_10s"].quantile(0.95)
        q1 = sub["abs_residual_1s"].quantile(0.95)
        q3 = sub["abs_residual_3s"].quantile(0.95)
        high10 = sub["abs_residual_10s"].ge(q10)
        persistent = high10 & sub["abs_residual_1s"].ge(q1) & sub["abs_residual_3s"].ge(q3)
        sign_stable = high10 & (
            np.sign(sub["residual_1s"])
            .eq(np.sign(sub["residual_3s"]))
            .to_numpy()
            & np.sign(sub["residual_3s"]).eq(np.sign(sub["residual_10s"])).to_numpy()
        )
        high1_resolved = sub["abs_residual_1s"].ge(q1) & ~high10
        tail = sub[high10]
        rows.append(
            {
                "dataset": dataset,
                "target": target,
                "n_records": len(sub),
                "n_top5_10s": int(high10.sum()),
                "persistent_top5_fraction": float(persistent.sum() / max(high10.sum(), 1)),
                "sign_stable_top5_fraction": float(sign_stable.sum() / max(high10.sum(), 1)),
                "high1_resolved_fraction": float(high1_resolved.sum() / max(sub["abs_residual_1s"].ge(q1).sum(), 1)),
                "top5_10s_underprediction_fraction": float((tail["residual_10s"] < 0).mean()),
                "top5_10s_median_distance_km": float(tail["source_distance_km"].median()),
                "all_median_distance_km": float(sub["source_distance_km"].median()),
                "top5_10s_median_abs_residual": float(tail["abs_residual_10s"].median()),
                "all_median_abs_residual_10s": float(sub["abs_residual_10s"].median()),
            }
        )
    return pd.DataFrame(rows)


def plot(summary: pd.DataFrame, wide: pd.DataFrame) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    labels = [
        f"{dataset} {target.upper()}".replace("instancegm", "IGM").replace("knet", "K-NET")
        for dataset, target in zip(summary["dataset"], summary["target"])
    ]
    x = np.arange(len(labels))
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.4), dpi=180)

    axes[0, 0].bar(x, summary["persistent_top5_fraction"], color="#356f9f")
    axes[0, 0].set_ylabel("fraction of 10 s top-5%")
    axes[0, 0].set_title("A. High residuals persisting from 1 s to 10 s", loc="left")

    axes[0, 1].bar(x, summary["high1_resolved_fraction"], color="#5f8f5a")
    axes[0, 1].set_ylabel("fraction of 1 s top-5%")
    axes[0, 1].set_title("B. High 1 s residuals resolved by 10 s", loc="left")

    dist_shift = summary["top5_10s_median_distance_km"] - summary["all_median_distance_km"]
    axes[1, 0].bar(x, dist_shift, color="#c45a32")
    axes[1, 0].axhline(0, color="#333333", lw=0.8)
    axes[1, 0].set_ylabel("median distance shift (km)")
    axes[1, 0].set_title("C. Distance shift of remaining 10 s tail", loc="left")

    sub = wide[(wide["dataset"].eq("knet")) & (wide["target"].eq("pga"))].copy()
    q10 = sub["abs_residual_10s"].quantile(0.95)
    tail = sub[sub["abs_residual_10s"].ge(q10)]
    axes[1, 1].scatter(sub["source_distance_km"], sub["abs_residual_10s"], s=8, alpha=0.22, color="#777777", label="all")
    axes[1, 1].scatter(tail["source_distance_km"], tail["abs_residual_10s"], s=14, alpha=0.7, color="#c45a32", label="10 s top-5%")
    axes[1, 1].set_xlabel("source distance (km)")
    axes[1, 1].set_ylabel("|residual| at 10 s")
    axes[1, 1].set_title("D. K-NET PGA remaining tail", loc="left")
    axes[1, 1].legend(frameon=False)

    for ax in axes.ravel()[:3]:
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=35, ha="right")
    for ax in axes.ravel():
        ax.grid(True, axis="y", alpha=0.25)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "residual_persistence_audit.png")
    plt.close(fig)


def write_summary(summary: pd.DataFrame) -> None:
    view = summary.copy()
    for col in view.select_dtypes("number").columns:
        if col.startswith("n_"):
            continue
        view[col] = view[col].map(lambda x: f"{x:.3f}")
    lines = [
        "# Residual persistence audit",
        "",
        "This audit uses existing 1 s, 3 s and 10 s metadata-plus-early-waveform residual tables. It does not retrain models.",
        "",
        "| " + " | ".join(view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in view.columns) + " |")
    k = summary[(summary["dataset"].eq("knet")) & (summary["target"].eq("pga"))].iloc[0]
    lines += [
        "",
        "Interpretation:",
        "",
        f"- K-NET PGA keeps {k.persistent_top5_fraction:.1%} of its 10 s top-tail residuals in the top 5% at both 1 s and 3 s.",
        f"- {k.high1_resolved_fraction:.1%} of K-NET PGA 1 s top-tail residuals leave the top 5% by 10 s.",
        f"- The remaining K-NET PGA 10 s tail is farther than the full set by {k.top5_10s_median_distance_km - k.all_median_distance_km:.1f} km in median distance.",
        "",
        "Files:",
        "- `outputs/residual_persistence_audit.csv`",
        "- `outputs/figures/ground_motion_audit/residual_persistence_audit.png`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines))


def main() -> None:
    df = load_predictions()
    wide = wide_table(df)
    summary = summarize(wide)
    OUT_CSV.write_text(summary.to_csv(index=False))
    plot(summary, wide)
    write_summary(summary)
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_DIR / 'residual_persistence_audit.png'}")


if __name__ == "__main__":
    main()
