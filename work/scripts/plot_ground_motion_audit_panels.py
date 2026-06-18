#!/usr/bin/env python3
"""Create figure-ready audit panels for ground-motion residuals."""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from run_ground_motion_baseline import early_window, to_int


TARGET_ORDER = ["pga", "pgv", "sa03", "sa10", "sa30"]
COLORS = {
    "Z": "#1f77b4",
    "N": "#2ca02c",
    "E": "#d62728",
}


def read_manifest_rows(manifest: Path, ids: set[str]) -> dict[str, dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    with gzip.open(manifest, "rt", newline="") as fh:
        header = fh.readline().rstrip("\n").split(",")
    for chunk in pd.read_csv(manifest, chunksize=200_000, dtype=str):
        sub = chunk[chunk["global_id"].isin(ids)]
        for row in sub.to_dict("records"):
            found[row["global_id"]] = row
        if len(found) == len(ids):
            break
    missing = sorted(ids - set(found))
    if missing:
        raise RuntimeError(f"Missing manifest rows: {missing}")
    return found


def load_waveform(row: dict[str, Any]) -> np.ndarray:
    start = to_int(row.get("sample_start"), 0)
    stop = to_int(row.get("sample_stop"), to_int(row.get("n_samples"), 0))
    with h5py.File(row["waveform_store"], "r") as h5:
        if row["dataset"] == "knet":
            arr = h5[row["hdf5_key"]][:, start:stop]
        else:
            arr = h5[row["hdf5_key"]][to_int(row["hdf5_index"]), :, start:stop]
    return np.asarray(arr, dtype=np.float32)


def selected_instancegm_ids(pred: pd.DataFrame, n: int) -> list[str]:
    sub = pred[(pred["dataset"] == "instancegm") & (pred["feature_set"] == "metadata_plus_early_waveform")].copy()
    worst = sub.groupby("target", group_keys=False).apply(lambda x: x.nlargest(25, "abs_residual_log10_target"))
    counts = worst["global_id"].value_counts()
    score = (
        worst.groupby("global_id")["abs_residual_log10_target"]
        .max()
        .rename("max_abs")
        .to_frame()
        .join(counts.rename("count"))
        .sort_values(["count", "max_abs"], ascending=False)
    )
    return score.head(n).index.tolist()


def selected_knet_ids(pred: pd.DataFrame, n: int) -> list[str]:
    sub = pred[
        (pred["dataset"] == "knet")
        & (pred["target"] == "pga")
        & (pred["feature_set"] == "metadata_plus_early_waveform")
    ].copy()
    return sub.nlargest(n, "abs_residual_log10_target")["global_id"].tolist()


def record_predictions(pred: pd.DataFrame, global_id: str) -> pd.DataFrame:
    return (
        pred[(pred["global_id"] == global_id) & (pred["feature_set"] == "metadata_plus_early_waveform")]
        .copy()
        .set_index("target")
        .reindex(TARGET_ORDER)
        .dropna(subset=["actual_log10_target"], how="all")
        .reset_index()
    )


def short_id(global_id: str) -> str:
    if global_id.startswith("instancegm:"):
        return global_id.replace("instancegm:", "").replace(",:3,:12000", "")
    return global_id.replace("knet:", "")


def plot_waveform_axis(ax: plt.Axes, row: dict[str, Any], seconds: float) -> float:
    arr = load_waveform(row)
    win = early_window(arr, row, seconds)
    if win.shape[1] == 0:
        ax.text(0.5, 0.5, "empty window", ha="center", va="center", transform=ax.transAxes)
        return float("nan")
    sr = float(row.get("sampling_rate_hz") or 100.0)
    t = np.arange(win.shape[1]) / sr
    max_abs = float(np.nanmax(np.abs(win)))
    scale = max_abs if max_abs > 0 else 1.0
    offsets = [2.0, 0.0, -2.0]
    labels = ["Z", "N", "E"]
    for idx, (label, offset) in enumerate(zip(labels, offsets)):
        y = win[idx] / scale + offset
        ax.plot(t, y, lw=0.8, color=COLORS[label], label=label)
    ax.set_ylim(-3.2, 3.2)
    ax.set_yticks(offsets)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, min(seconds, t[-1] if len(t) else seconds))
    ax.grid(True, axis="x", alpha=0.25)
    return max_abs


def fmt_meta(row: pd.Series) -> str:
    mag = row.get("source_magnitude", np.nan)
    dist = row.get("source_distance_km", np.nan)
    dep = row.get("source_depth_km", np.nan)
    vmax = row.get("vec_early_absmax", np.nan)
    return f"M {mag:.1f} | R {dist:.1f} km | D {dep:.1f} km | Vmax {vmax:.3g}"


def plot_instancegm_panel(pred: pd.DataFrame, manifest_rows: dict[str, dict[str, str]], ids: list[str], out_path: Path, seconds: float) -> None:
    fig = plt.figure(figsize=(12.5, 2.05 * len(ids)), dpi=180)
    gs = fig.add_gridspec(len(ids), 2, width_ratios=[2.3, 1.15], hspace=0.48, wspace=0.20)
    for idx, gid in enumerate(ids):
        rows = record_predictions(pred, gid)
        meta = rows.iloc[0]
        ax_w = fig.add_subplot(gs[idx, 0])
        max_abs = plot_waveform_axis(ax_w, manifest_rows[gid], seconds)
        ax_w.set_title(f"{short_id(gid)}  |  {fmt_meta(meta)}  | waveform max {max_abs:.3g}", loc="left", fontsize=8)
        if idx == len(ids) - 1:
            ax_w.set_xlabel("seconds after P")
        else:
            ax_w.set_xticklabels([])

        ax_b = fig.add_subplot(gs[idx, 1])
        vals = rows["residual_log10_target"].to_numpy()
        targets = rows["target"].to_numpy()
        colors = np.where(vals >= 0, "#b2182b", "#2166ac")
        ax_b.bar(np.arange(len(vals)), vals, color=colors, alpha=0.86)
        ax_b.axhline(0, color="black", lw=0.8)
        ax_b.set_xticks(np.arange(len(vals)))
        ax_b.set_xticklabels([x.upper() for x in targets], rotation=0, fontsize=7)
        ax_b.set_ylabel("residual", fontsize=8)
        ax_b.grid(True, axis="y", alpha=0.25)
        bound = max(0.8, float(np.nanmax(np.abs(vals))) * 1.18)
        ax_b.set_ylim(-bound, bound)
        for x, val in enumerate(vals):
            if abs(val) < 0.12:
                continue
            ax_b.text(x, val * 0.50, f"{val:+.2f}", ha="center", va="center", fontsize=6.4, color="white")
    fig.suptitle("InstanceGM repeated high-residual audit cases, 10 s post-P window", x=0.01, ha="left", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    fig.savefig(out_path)
    plt.close(fig)


def plot_knet_panel(pred: pd.DataFrame, manifest_rows: dict[str, dict[str, str]], ids: list[str], out_path: Path, seconds: float) -> None:
    fig = plt.figure(figsize=(12.0, 2.0 * len(ids)), dpi=180)
    gs = fig.add_gridspec(len(ids), 2, width_ratios=[2.35, 1.0], hspace=0.45, wspace=0.20)
    for idx, gid in enumerate(ids):
        rows = record_predictions(pred, gid)
        row = rows[rows["target"] == "pga"].iloc[0]
        ax_w = fig.add_subplot(gs[idx, 0])
        max_abs = plot_waveform_axis(ax_w, manifest_rows[gid], seconds)
        ax_w.set_title(f"{short_id(gid)}  |  {fmt_meta(row)}  | waveform max {max_abs:.3g}", loc="left", fontsize=8)
        if idx == len(ids) - 1:
            ax_w.set_xlabel("seconds after P")
        else:
            ax_w.set_xticklabels([])

        ax_b = fig.add_subplot(gs[idx, 1])
        ax_b.bar([0, 1], [row.actual_log10_target, row.pred_log10_target], color=["#4d4d4d", "#fdae61"], alpha=0.9)
        ax_b.set_xticks([0, 1])
        ax_b.set_xticklabels(["obs", "pred"], fontsize=8)
        ax_b.set_ylabel("log10 PGA", fontsize=8)
        ax_b.grid(True, axis="y", alpha=0.25)
        ax_b.set_title(f"residual {row.residual_log10_target:+.2f}", fontsize=8)
        ymin = min(row.actual_log10_target, row.pred_log10_target) - 0.25
        ymax = max(row.actual_log10_target, row.pred_log10_target) + 0.25
        ax_b.set_ylim(ymin, ymax)
        for x, val in enumerate([row.actual_log10_target, row.pred_log10_target]):
            ax_b.text(x, val, f"{val:.2f}", ha="center", va="bottom", fontsize=7)
    fig.suptitle("K-NET PGA worst residual audit cases, 10 s post-P window", x=0.01, ha="left", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    fig.savefig(out_path)
    plt.close(fig)


def plot_residual_diagnostic(metrics_delta: pd.DataFrame, bins: pd.DataFrame, out_path: Path) -> None:
    fig = plt.figure(figsize=(12.0, 7.2), dpi=180)
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.25)

    ax = fig.add_subplot(gs[0, 0])
    labels = [f"{r.dataset}\n{r.target.upper()}" for r in metrics_delta.itertuples(index=False)]
    x = np.arange(len(labels))
    ax.bar(x - 0.18, metrics_delta["mae_reduction_pct"], width=0.36, label="MAE", color="#67a9cf")
    ax.bar(x + 0.18, metrics_delta["q95_reduction_pct"], width=0.36, label="q95 abs", color="#ef8a62")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("reduction from metadata-only (%)")
    ax.set_title("Early waveform features reduce mean and tail errors")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, axis="y", alpha=0.25)

    ax = fig.add_subplot(gs[0, 1])
    sub = bins[
        (bins["dataset"] == "knet")
        & (bins["target"] == "pga")
        & (bins["feature_set"] == "metadata_plus_early_waveform")
        & (bins["variable"] == "source_distance_km")
    ].copy()
    centers = (sub["x_min"] + sub["x_max"]) / 2
    ax.plot(centers, sub["mae_residual"], marker="o", color="#2166ac")
    ax.set_xlabel("source distance km")
    ax.set_ylabel("MAE residual")
    ax.set_title("K-NET PGA residual tail increases at far distance")
    ax.grid(True, alpha=0.25)

    ax = fig.add_subplot(gs[1, 0])
    sub = bins[
        (bins["dataset"] == "instancegm")
        & (bins["feature_set"] == "metadata_plus_early_waveform")
        & (bins["variable"] == "source_depth_km")
    ].copy()
    for target, group in sub.groupby("target"):
        centers = (group["x_min"] + group["x_max"]) / 2
        ax.plot(centers, group["mae_residual"], marker="o", lw=1.0, label=target.upper())
    ax.set_xlabel("source depth km")
    ax.set_ylabel("MAE residual")
    ax.set_title("InstanceGM residuals by source depth")
    ax.legend(frameon=False, fontsize=7, ncol=2)
    ax.grid(True, alpha=0.25)

    ax = fig.add_subplot(gs[1, 1])
    sub = bins[
        (bins["dataset"] == "instancegm")
        & (bins["feature_set"] == "metadata_plus_early_waveform")
        & (bins["variable"] == "vec_early_absmax")
    ].copy()
    for target, group in sub.groupby("target"):
        centers = (group["x_min"] + group["x_max"]) / 2
        ax.plot(centers, group["mae_residual"], marker="o", lw=1.0, label=target.upper())
    ax.set_xscale("symlog", linthresh=1e-5)
    ax.set_xlabel("10 s vector early absmax")
    ax.set_ylabel("MAE residual")
    ax.set_title("InstanceGM residuals by early-window amplitude")
    ax.legend(frameon=False, fontsize=7, ncol=2)
    ax.grid(True, alpha=0.25)

    fig.suptitle("Ground-motion residual diagnostics, 10 s HGB combined baseline", x=0.01, ha="left", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_path)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("work/unified_manifest/unified_manifest.csv.gz"))
    parser.add_argument("--predictions", type=Path, default=Path("work/ground_motion_residuals_10s/ground_motion_residual_predictions.csv"))
    parser.add_argument("--metric-deltas", type=Path, default=Path("work/ground_motion_residuals_10s/ground_motion_residual_metric_deltas.csv"))
    parser.add_argument("--bins", type=Path, default=Path("work/ground_motion_residuals_10s/ground_motion_residual_bins.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("outputs/figures/ground_motion_audit"))
    parser.add_argument("--instancegm-n", type=int, default=6)
    parser.add_argument("--knet-n", type=int, default=6)
    parser.add_argument("--seconds", type=float, default=10.0)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    pred = pd.read_csv(args.predictions)
    instance_ids = selected_instancegm_ids(pred, args.instancegm_n)
    knet_ids = selected_knet_ids(pred, args.knet_n)
    manifest_rows = read_manifest_rows(args.manifest, set(instance_ids + knet_ids))

    instance_path = args.out_dir / "instancegm_repeated_residual_audit_panel.png"
    knet_path = args.out_dir / "knet_pga_worst_residual_audit_panel.png"
    diagnostic_path = args.out_dir / "ground_motion_residual_diagnostic_panel.png"

    plot_instancegm_panel(pred, manifest_rows, instance_ids, instance_path, args.seconds)
    plot_knet_panel(pred, manifest_rows, knet_ids, knet_path, args.seconds)
    plot_residual_diagnostic(pd.read_csv(args.metric_deltas), pd.read_csv(args.bins), diagnostic_path)

    report = {
        "instancegm_ids": instance_ids,
        "knet_ids": knet_ids,
        "paths": {
            "instancegm_panel": str(instance_path),
            "knet_panel": str(knet_path),
            "diagnostic_panel": str(diagnostic_path),
        },
        "residual_definition": "predicted log10 target - observed log10 target",
    }
    report_path = args.out_dir / "ground_motion_audit_panels_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
