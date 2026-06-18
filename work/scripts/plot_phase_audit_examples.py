#!/usr/bin/env python3
"""Plot waveform examples for large phase-picking residuals."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def to_float(value: Any) -> float | None:
    try:
        if value is None or pd.isna(value) or str(value) == "":
            return None
        value_f = float(value)
        return value_f if np.isfinite(value_f) else None
    except Exception:
        return None


def to_int(value: Any, default: int = 0) -> int:
    value_f = to_float(value)
    return default if value_f is None else int(round(value_f))


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")


def load_manifest_rows(manifest: Path, global_ids: set[str]) -> dict[str, dict[str, Any]]:
    rows = {}
    for chunk in pd.read_csv(manifest, chunksize=200_000, dtype=str):
        sub = chunk[chunk["global_id"].isin(global_ids)]
        for _, row in sub.iterrows():
            rows[row["global_id"]] = row.to_dict()
        if len(rows) == len(global_ids):
            break
    return rows


def load_waveform(row: dict[str, Any]) -> np.ndarray:
    start = to_int(row.get("sample_start"), 0)
    stop = to_int(row.get("sample_stop"), to_int(row.get("n_samples"), 0))
    with h5py.File(row["waveform_store"], "r") as h5:
        if row["dataset"] == "knet":
            arr = h5[row["hdf5_key"]][:, start:stop]
        else:
            arr = h5[row["hdf5_key"]][to_int(row["hdf5_index"]), :, start:stop]
    return np.asarray(arr, dtype=np.float32)


def normalized(arr: np.ndarray) -> np.ndarray:
    out = arr.copy().astype(float)
    for i in range(out.shape[0]):
        x = out[i]
        x = x - np.nanmedian(x)
        scale = np.nanpercentile(np.abs(x), 99)
        if not np.isfinite(scale) or scale <= 0:
            scale = np.nanmax(np.abs(x)) or 1.0
        out[i] = x / scale
    return out


def plot_record(row: dict[str, Any], preds: pd.DataFrame, out_dir: Path) -> Path:
    arr = normalized(load_waveform(row))
    sr = to_float(row.get("sampling_rate_hz")) or 100.0
    t = np.arange(arr.shape[1], dtype=float) / sr

    fig, axes = plt.subplots(3, 1, figsize=(12, 7), sharex=True)
    components = list(row.get("component_order") or "ZNE")
    if len(components) != 3:
        components = ["Z", "N", "E"]

    true_p = to_float(preds["p_true_sec"].dropna().iloc[0]) if preds["p_true_sec"].notna().any() else None
    true_s = to_float(preds["s_true_sec"].dropna().iloc[0]) if preds["s_true_sec"].notna().any() else None

    for idx, ax in enumerate(axes):
        ax.plot(t, arr[idx], color="0.15", linewidth=0.7)
        ax.set_ylabel(components[idx])
        ax.axhline(0, color="0.8", linewidth=0.5)
        if true_p is not None:
            ax.axvline(true_p, color="#1f77b4", linewidth=1.6, label="label P" if idx == 0 else None)
        if true_s is not None:
            ax.axvline(true_s, color="#d62728", linewidth=1.6, label="label S" if idx == 0 else None)

        for _, pred in preds.iterrows():
            p_sec = to_float(pred.get("p_pred_sec"))
            s_sec = to_float(pred.get("s_pred_sec"))
            if p_sec is not None:
                ax.axvline(p_sec, color="#1f77b4", alpha=0.35, linestyle="--", linewidth=1.0)
            if s_sec is not None:
                ax.axvline(s_sec, color="#d62728", alpha=0.35, linestyle="--", linewidth=1.0)

    title = f"{row['global_id']} | n={row['n_samples']} | M={row.get('source_magnitude', '')}"
    axes[0].set_title(title)
    axes[-1].set_xlabel("Time from window start (s)")
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        axes[0].legend(loc="upper right")

    text_lines = []
    for _, pred in preds.iterrows():
        text_lines.append(
            f"{pred['model']}: "
            f"P {pred.get('p_pred_sec', '')} ({pred.get('p_abs_error_sec', '')}), "
            f"S {pred.get('s_pred_sec', '')} ({pred.get('s_abs_error_sec', '')})"
        )
    fig.text(0.01, 0.01, "\n".join(text_lines), fontsize=8, family="monospace")
    fig.tight_layout(rect=(0, 0.12, 1, 1))

    out_path = out_dir / f"{slug(row['global_id'])}.png"
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("work/unified_manifest/unified_manifest.csv.gz"))
    parser.add_argument(
        "--predictions",
        type=Path,
        default=Path("work/baseline_pilot_four_models/phase_baseline_pilot_predictions.csv"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("outputs/baseline_worst_plots"))
    parser.add_argument("--top", type=int, default=6)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    preds = pd.read_csv(args.predictions, dtype=str)
    scored = []
    for _, row in preds.iterrows():
        p_err = to_float(row.get("p_abs_error_sec")) or -1
        s_err = to_float(row.get("s_abs_error_sec")) or -1
        scored.append((max(p_err, s_err), row["global_id"]))
    global_ids = []
    for _, gid in sorted(scored, reverse=True):
        if gid not in global_ids:
            global_ids.append(gid)
        if len(global_ids) >= args.top:
            break

    manifest_rows = load_manifest_rows(args.manifest, set(global_ids))
    outputs = []
    for gid in global_ids:
        row = manifest_rows[gid]
        record_preds = preds[preds["global_id"] == gid].copy()
        outputs.append(plot_record(row, record_preds, args.out_dir))

    index_path = args.out_dir / "index.md"
    lines = ["# Phase Audit Example Plots", "", "These plots show catalog labels as solid lines and model picks as dashed lines.", ""]
    for path in outputs:
        lines.append(f"- `{path.name}`")
    index_path.write_text("\n".join(lines) + "\n")
    print("created")
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
