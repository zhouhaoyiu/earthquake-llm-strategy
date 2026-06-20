#!/usr/bin/env python3
"""Audit whether current data support a fully specified regional GMM."""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd


FEATURE_DIR = Path("work/ground_motion_balanced_station_10s")
INSTANCE_META = Path("/Users/yojironoda/.seisbench/datasets/instancegm/metadata.csv")
OUT_CSV = Path("outputs/regional_gmm_readiness_audit.csv")
OUT_MD = Path("outputs/regional_gmm_readiness_audit.md")


def frac(n: int, d: int) -> float:
    return 0.0 if d == 0 else n / d


def nonmissing(df: pd.DataFrame, col: str) -> int:
    if col not in df:
        return 0
    return int(pd.to_numeric(df[col], errors="coerce").notna().sum())


def audit_instancegm(meta: pd.DataFrame, split: str) -> dict:
    feat = pd.read_csv(FEATURE_DIR / f"instancegm_held_station_{split}_features.csv")
    joined = feat[["record_id", "station_vs30_mps", "source_distance_km"]].merge(
        meta,
        left_on="record_id",
        right_on="trace_name",
        how="left",
    )
    rows = len(joined)
    mech = int(joined["source_mechanism_strike_dip_rake"].notna().sum())
    return {
        "dataset": "instancegm",
        "split": split,
        "rows": rows,
        "join_rows": int(joined["trace_name"].notna().sum()),
        "vs30_rows": nonmissing(joined, "station_vs30_mps"),
        "mechanism_rows": mech,
        "ep_distance_rows": nonmissing(joined, "path_ep_distance_km"),
        "hyp_distance_rows": nonmissing(joined, "path_hyp_distance_km"),
        "vs30_frac": frac(nonmissing(joined, "station_vs30_mps"), rows),
        "mechanism_frac": frac(mech, rows),
    }


def audit_knet(split: str) -> dict:
    feat = pd.read_csv(FEATURE_DIR / f"knet_held_station_{split}_features.csv")
    rows = len(feat)
    return {
        "dataset": "knet",
        "split": split,
        "rows": rows,
        "join_rows": rows,
        "vs30_rows": nonmissing(feat, "station_vs30_mps"),
        "mechanism_rows": 0,
        "ep_distance_rows": nonmissing(feat, "source_distance_km"),
        "hyp_distance_rows": nonmissing(feat, "source_distance_km"),
        "vs30_frac": frac(nonmissing(feat, "station_vs30_mps"), rows),
        "mechanism_frac": 0.0,
    }


def main() -> None:
    meta = pd.read_csv(
        INSTANCE_META,
        usecols=[
            "trace_name",
            "source_mechanism_strike_dip_rake",
            "path_ep_distance_km",
            "path_hyp_distance_km",
        ],
        low_memory=False,
    )
    rows = []
    for split in ["train", "test"]:
        rows.append(audit_instancegm(meta, split))
        rows.append(audit_knet(split))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    inst_train = next(r for r in rows if r["dataset"] == "instancegm" and r["split"] == "train")
    inst_test = next(r for r in rows if r["dataset"] == "instancegm" and r["split"] == "test")
    knet_train = next(r for r in rows if r["dataset"] == "knet" and r["split"] == "train")
    md = [
        "# Regional GMM Readiness Audit",
        "",
        "Date: 2026-06-18",
        "",
        "This audit checks whether the current balanced held-station data support a fully specified regional GMM comparison.",
        "",
        "## Findings",
        "",
        f"- InstanceGM joins back to metadata for {inst_train['join_rows']}/{inst_train['rows']} train records and {inst_test['join_rows']}/{inst_test['rows']} test records.",
        f"- InstanceGM has Vs30 for {inst_train['vs30_rows']}/{inst_train['rows']} train records and {inst_test['vs30_rows']}/{inst_test['rows']} test records.",
        f"- InstanceGM has focal-mechanism strings for {inst_train['mechanism_rows']}/{inst_train['rows']} train records and {inst_test['mechanism_rows']}/{inst_test['rows']} test records.",
        f"- K-NET has source-distance values for {knet_train['ep_distance_rows']}/{knet_train['rows']} train records, but no Vs30 or focal-mechanism fields in the current local package.",
        "",
        "## Interpretation",
        "",
        "The current package supports bias-corrected classical references and Japanese GMM screening, but it does not support a fully specified regional GMM claim. InstanceGM has site terms but sparse mechanism coverage. K-NET has the target and distance coverage needed for screening, but lacks Vs30, rupture distance, and focal-mechanism or tectonic-class metadata in the approved local data.",
        "",
        f"CSV: `{OUT_CSV}`",
    ]
    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"wrote {OUT_CSV} and {OUT_MD}")


if __name__ == "__main__":
    main()
