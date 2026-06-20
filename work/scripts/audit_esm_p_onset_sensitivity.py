#!/usr/bin/env python3
"""Audit ESM theoretical P-onset sensitivity from retained compact features."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


FEATURES = Path("work/esm_compact_features_full/esm_compact_features.csv.gz")
OUT_CSV = Path("outputs/esm_p_onset_sensitivity_audit.csv")
OUT_MD = Path("outputs/esm_p_onset_sensitivity_audit.md")
VPS = [5.5, 6.0, 6.5]


def main() -> None:
    cols = [
        "record_id",
        "early_seconds",
        "p_arrival_offset_s",
        "path_hyp_distance_km",
        "source_distance_km",
        "source_depth_km",
        "trace_npts",
        "trace_sampling_rate_hz",
    ]
    df = pd.read_csv(FEATURES, usecols=cols)
    hypo = pd.to_numeric(df["path_hyp_distance_km"], errors="coerce")
    fallback = np.sqrt(
        pd.to_numeric(df["source_distance_km"], errors="coerce") ** 2
        + pd.to_numeric(df["source_depth_km"], errors="coerce").fillna(0.0) ** 2
    )
    hypo = hypo.fillna(fallback)
    offset6 = pd.to_numeric(df["p_arrival_offset_s"], errors="coerce")
    duration = pd.to_numeric(df["trace_npts"], errors="coerce") / pd.to_numeric(
        df["trace_sampling_rate_hz"], errors="coerce"
    )
    origin_to_first = offset6 - hypo / 6.0

    rows = []
    valid_by_vp: dict[float, pd.Series] = {}
    for vp in VPS:
        offset = origin_to_first + hypo / vp
        delta = offset - offset6
        valid = offset.ge(0) & (offset + pd.to_numeric(df["early_seconds"], errors="coerce")).le(duration)
        valid_by_vp[vp] = valid
        for window, sub_idx in df.groupby("early_seconds").groups.items():
            idx = list(sub_idx)
            d = delta.iloc[idx]
            v = valid.iloc[idx]
            rows.append(
                {
                    "vp_km_s": vp,
                    "window_s": float(window),
                    "rows": int(len(idx)),
                    "valid_fraction": float(v.mean()),
                    "invalid_rows": int((~v).sum()),
                    "delta_vs_6s_q05": float(d.quantile(0.05)),
                    "delta_vs_6s_median": float(d.median()),
                    "delta_vs_6s_q95": float(d.quantile(0.95)),
                    "abs_delta_vs_6s_median": float(d.abs().median()),
                    "abs_delta_vs_6s_q95": float(d.abs().quantile(0.95)),
                }
            )

    out = pd.DataFrame(rows).sort_values(["vp_km_s", "window_s"])
    all_valid = valid_by_vp[5.5] & valid_by_vp[6.0] & valid_by_vp[6.5]
    all_valid_by_window = (
        pd.DataFrame({"window_s": df["early_seconds"], "valid_all_vp": all_valid})
        .groupby("window_s")["valid_all_vp"]
        .mean()
    )
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)
    write_summary(df, out, all_valid_by_window)

    assert len(out) == len(VPS) * 5
    assert out["valid_fraction"].min() > 0.99
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")


def write_summary(df: pd.DataFrame, out: pd.DataFrame, all_valid_by_window: pd.Series) -> None:
    v55 = out[out["vp_km_s"].eq(5.5)].iloc[0]
    v65 = out[out["vp_km_s"].eq(6.5)].iloc[0]
    lines = [
        "# ESM P-Onset Sensitivity Audit",
        "",
        "This audit uses the retained ESM compact feature table generated with `theoretical_vp_6kmps`. It does not create new waveform features and does not replace catalog/manual P picks.",
        "",
        f"Rows audited: {len(df):,}. Unique event-station records: {df['record_id'].nunique():,}.",
        "",
        "| Vp km/s | Window | Valid fraction among retained rows | Median shift vs 6 km/s | q95 absolute shift |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in out.itertuples(index=False):
        lines.append(
            f"| {row.vp_km_s:.1f} | {row.window_s:.0f}s | {row.valid_fraction:.4f} | "
            f"{row.delta_vs_6s_median:.3f}s | {row.abs_delta_vs_6s_q95:.3f}s |"
        )
    lines.extend(
        [
            "",
            "All-Vp retained-window fraction:",
            "",
            "| Window | Fraction valid under 5.5/6.0/6.5 km/s |",
            "|---:|---:|",
        ]
    )
    for window, frac in all_valid_by_window.items():
        lines.append(f"| {window:.0f}s | {frac:.4f} |")
    lines.extend(
        [
            "",
            "Interpretation:",
            f"- Changing Vp from 6.0 to 5.5 km/s delays the theoretical P onset by a median {v55.delta_vs_6s_median:.2f} s.",
            f"- Changing Vp from 6.0 to 6.5 km/s advances it by a median {abs(v65.delta_vs_6s_median):.2f} s.",
            "- The retained-row definition is stable under these plausible velocities, with all-window valid fractions above 0.99.",
            "- The timing shift is large relative to 1-2 s windows, so ESM remains an external strong-motion supplement and transfer-domain check, not a catalog-P lead-time proof.",
            "",
            "Files:",
            f"- `{OUT_CSV}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
