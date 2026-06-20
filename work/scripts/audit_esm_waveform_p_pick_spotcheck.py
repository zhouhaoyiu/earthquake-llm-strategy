#!/usr/bin/env python3
"""Spot-check ESM theoretical P onset against waveform-level onset proxies."""

from __future__ import annotations

import argparse
import json
import math
import zipfile
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import pandas as pd

from build_esm_compact_features import (
    COMPONENTS,
    component_from_stream,
    p_offset_seconds,
    read_ascii_member,
    station_key,
    to_float,
)

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def station_group(header: dict[str, str]) -> str:
    network, station, location = station_key(header)
    out = f"{network}.{station}" if network or station else ""
    return f"{out}.{location}" if location else out


def sample_records(features: Path, n: int, seed: int) -> pd.DataFrame:
    cols = [
        "record_id",
        "event_id",
        "station_group",
        "zip_path",
        "early_seconds",
        "source_distance_km",
        "source_depth_km",
        "target_pga",
        "target_log10_pga",
        "p_arrival_offset_s",
        "trace_sampling_rate_hz",
    ]
    df = pd.read_csv(features, usecols=cols)
    base = df[df["early_seconds"].eq(10)].drop_duplicates("record_id").dropna(
        subset=["zip_path", "station_group", "source_distance_km", "target_log10_pga", "p_arrival_offset_s"]
    )
    base = base[base["p_arrival_offset_s"].between(1.0, 180.0)]
    base = base.copy()
    base["distance_bin"] = pd.qcut(base["source_distance_km"], 4, duplicates="drop")
    base["pga_bin"] = pd.qcut(base["target_log10_pga"], 4, duplicates="drop")

    per_bin = max(1, math.ceil(n / max(1, base.groupby(["distance_bin", "pga_bin"], observed=True).ngroups)))
    sampled = (
        base.groupby(["distance_bin", "pga_bin"], observed=True, group_keys=False)
        .apply(lambda g: g.sample(min(len(g), per_bin), random_state=seed))
        .drop_duplicates("record_id")
    )
    if len(sampled) < n:
        rest = base[~base["record_id"].isin(sampled["record_id"])]
        sampled = pd.concat([sampled, rest.sample(min(len(rest), n - len(sampled)), random_state=seed)], ignore_index=True)
    return sampled.head(n).reset_index(drop=True)


def moving_rms(x: np.ndarray, n: int) -> np.ndarray:
    n = max(1, min(n, x.size))
    return np.sqrt(np.convolve(x * x, np.ones(n, dtype=np.float32) / n, mode="same"))


def detect_onset(components: dict[str, np.ndarray], header: dict[str, str], search_s: float) -> dict[str, Any]:
    dt = to_float(header.get("SAMPLING_INTERVAL_S"))
    theory = p_offset_seconds(header, 6.0)
    if dt is None or dt <= 0 or theory is None or theory < 0:
        return {"detected": False, "reason": "bad_time"}
    arrays = [components[c] for c in COMPONENTS if c in components and components[c].size]
    if not arrays:
        return {"detected": False, "reason": "missing_components"}
    m = min(arr.size for arr in arrays)
    if m < int(5 / dt):
        return {"detected": False, "reason": "too_short"}
    stack = np.vstack([(arr[:m] - np.nanmedian(arr[:m])) for arr in arrays])
    env = np.sqrt(np.nanmean(stack * stack, axis=0))
    smooth = moving_rms(env.astype(np.float32), int(round(0.20 / dt)))

    p = int(round(theory / dt))
    noise_a = max(0, p - int(round(15 / dt)))
    noise_b = max(noise_a + 1, p - int(round(2 / dt)))
    if noise_b - noise_a < int(round(2 / dt)):
        noise_a, noise_b = 0, min(m, int(round(5 / dt)))
    noise = smooth[noise_a:noise_b]
    if noise.size < 10:
        return {"detected": False, "reason": "no_noise_window"}
    med = float(np.nanmedian(noise))
    mad = float(np.nanmedian(np.abs(noise - med)))
    p95 = float(np.nanpercentile(noise, 95))
    noise_rms = float(np.sqrt(np.nanmean(noise * noise)))
    threshold = max(med + 8.0 * 1.4826 * mad, p95 * 1.7, med * 5.0)

    s0 = max(0, p - int(round(search_s / dt)))
    s1 = min(m, p + int(round(search_s / dt)))
    seg = smooth[s0:s1]
    if seg.size < 10:
        return {"detected": False, "reason": "bad_search_window"}
    above = seg > threshold
    persist = max(1, int(round(0.10 / dt)))
    hits = np.convolve(above.astype(np.int16), np.ones(persist, dtype=np.int16), mode="same") >= persist
    if not hits.any():
        return {
            "detected": False,
            "reason": "below_threshold",
            "p_arrival_offset_s": theory,
            "peak_to_noise": float(np.nanmax(seg) / max(noise_rms, 1e-12)),
            "noise_rms": noise_rms,
            "threshold": threshold,
        }
    onset_idx = s0 + int(np.argmax(hits))
    peak_to_noise = float(np.nanmax(seg) / max(noise_rms, 1e-12))
    return {
        "detected": True,
        "reason": "",
        "p_arrival_offset_s": theory,
        "proxy_onset_offset_s": onset_idx * dt,
        "delta_s": onset_idx * dt - theory,
        "abs_delta_s": abs(onset_idx * dt - theory),
        "peak_to_noise": peak_to_noise,
        "noise_rms": noise_rms,
        "threshold": threshold,
        "high_confidence": bool(peak_to_noise >= 8.0),
    }


def read_requested_groups(zip_path: Path, groups: set[str]) -> dict[str, tuple[dict[str, str], dict[str, np.ndarray]]]:
    found: dict[str, tuple[dict[str, str], dict[str, np.ndarray]]] = {}
    prefixes = tuple(f"{g}." for g in groups)
    with zipfile.ZipFile(zip_path) as zf:
        names = [name for name in zf.namelist() if ".ACC.AP." in name and name.endswith(".ASC") and name.startswith(prefixes)]
        for name in names:
            header, data = read_ascii_member(zf, name)
            group = station_group(header)
            if group not in groups:
                continue
            comp = component_from_stream(header.get("STREAM", ""))
            if comp is None:
                continue
            base_header, comps = found.setdefault(group, (header, {}))
            comps[comp] = data
    return found


def summarize(results: pd.DataFrame, path: Path, args: argparse.Namespace) -> None:
    detected = results[results["detected"].astype(bool)]
    hi = detected[detected["high_confidence"].astype(bool)] if not detected.empty else detected

    def metric_block(df: pd.DataFrame, label: str) -> list[str]:
        if df.empty:
            return [f"| {label} | 0 | NA | NA | NA | NA | NA | NA |"]
        return [
            "| "
            + " | ".join(
                [
                    label,
                    str(len(df)),
                    f"{df['delta_s'].median():.3f}",
                    f"{df['abs_delta_s'].median():.3f}",
                    f"{df['abs_delta_s'].quantile(0.90):.3f}",
                    f"{df['abs_delta_s'].quantile(0.95):.3f}",
                    f"{(df['abs_delta_s'] <= 2.0).mean():.3f}",
                    f"{(df['abs_delta_s'] <= 5.0).mean():.3f}",
                ]
            )
            + " |"
        ]

    lines = [
        "# ESM Waveform-Level P-Onset Spot Audit",
        "",
        "This audit compares the ESM theoretical P-onset estimate with a waveform-level onset proxy computed from local ACC.AP streams.",
        "The proxy is an automated envelope threshold detector, not a manual or catalog P pick.",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Requested samples | {args.samples} |",
        f"| Processed samples | {len(results)} |",
        f"| Detected onset proxies | {len(detected)} |",
        f"| High-confidence proxies | {len(hi)} |",
        f"| Search half-width | {args.search_s:g} s |",
        "",
        "| subset | n | median delta s | median abs s | q90 abs s | q95 abs s | frac abs <=2s | frac abs <=5s |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        *metric_block(detected, "all detected"),
        *metric_block(hi, "high confidence"),
        "",
        "Interpretation:",
        "- The result is a waveform-level timing sanity check for ESM, not a replacement for manual P picks.",
        "- If the high-confidence absolute offsets remain within a few seconds, ESM can stay as an external transfer-domain check with explicit onset-proxy wording.",
        "- Records without a detected proxy or with low peak-to-noise should stay outside lead-time claims.",
        "",
        "Files:",
        f"- `{args.out_csv}`",
        f"- `{args.out_json}`",
        f"- `{args.figure}`",
    ]
    path.write_text("\n".join(lines) + "\n")


def plot_results(results: pd.DataFrame, figure: Path) -> None:
    detected = results[results["detected"].astype(bool)].copy()
    hi = detected[detected["high_confidence"].astype(bool)]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    axes[0].hist(detected["delta_s"].dropna(), bins=25, color="#356f9f", alpha=0.75, label="detected")
    if not hi.empty:
        axes[0].hist(hi["delta_s"].dropna(), bins=25, color="#c45a32", alpha=0.55, label="high confidence")
    axes[0].axvline(0, color="#333333", linewidth=1)
    axes[0].set_title("A. Proxy minus theoretical onset", loc="left")
    axes[0].set_xlabel("delta (s)")
    axes[0].set_ylabel("records")
    axes[0].legend(frameon=False, fontsize=8)

    axes[1].scatter(detected["source_distance_km"], detected["abs_delta_s"], s=18, alpha=0.75, color="#356f9f")
    axes[1].set_title("B. Offset by distance", loc="left")
    axes[1].set_xlabel("epicentral distance (km)")
    axes[1].set_ylabel("abs delta (s)")

    axes[2].scatter(detected["target_log10_pga"], detected["abs_delta_s"], s=18, alpha=0.75, color="#5f8f5a")
    axes[2].set_title("C. Offset by PGA", loc="left")
    axes[2].set_xlabel("log10 PGA")
    axes[2].set_ylabel("abs delta (s)")
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.tight_layout()
    figure.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure, dpi=240)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", type=Path, default=Path("work/esm_compact_features_full/esm_compact_features.csv.gz"))
    parser.add_argument("--samples", type=int, default=200)
    parser.add_argument("--seed", type=int, default=191)
    parser.add_argument("--search-s", type=float, default=8.0)
    parser.add_argument("--out-csv", type=Path, default=Path("outputs/esm_waveform_p_pick_spotcheck.csv"))
    parser.add_argument("--out-json", type=Path, default=Path("outputs/esm_waveform_p_pick_spotcheck.json"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/esm_waveform_p_pick_spotcheck.md"))
    parser.add_argument("--figure", type=Path, default=Path("outputs/figures/ground_motion_audit/esm_waveform_p_pick_spotcheck.png"))
    args = parser.parse_args()

    sample = sample_records(args.features, args.samples, args.seed)
    rows: list[dict[str, Any]] = []
    for zip_path_str, part in sample.groupby("zip_path"):
        zip_path = Path(zip_path_str)
        groups = set(part["station_group"].astype(str))
        found = read_requested_groups(zip_path, groups)
        for row in part.to_dict("records"):
            group = str(row["station_group"])
            base = {k: row[k] for k in ["record_id", "event_id", "station_group", "zip_path", "source_distance_km", "source_depth_km", "target_pga", "target_log10_pga"]}
            if group not in found:
                rows.append({**base, "detected": False, "high_confidence": False, "reason": "station_not_found"})
                continue
            header, comps = found[group]
            result = detect_onset(comps, header, args.search_s)
            rows.append({**base, **result})

    results = pd.DataFrame(rows)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.out_csv, index=False)
    report = {
        "samples": int(args.samples),
        "processed": int(len(results)),
        "detected": int(results["detected"].astype(bool).sum()) if not results.empty else 0,
        "high_confidence": int(results["high_confidence"].fillna(False).astype(bool).sum()) if "high_confidence" in results else 0,
        "median_abs_delta_s": float(results.loc[results["detected"].astype(bool), "abs_delta_s"].median()) if len(results) else None,
    }
    args.out_json.write_text(json.dumps(report, indent=2) + "\n")
    summarize(results, args.summary, args)
    plot_results(results, args.figure)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
