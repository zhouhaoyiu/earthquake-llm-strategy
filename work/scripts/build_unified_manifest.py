#!/usr/bin/env python3
"""Build a unified manifest across local SeisBench datasets and converted K-NET."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


TRACE_RE = re.compile(r"^(?P<bucket>[^$]+)\$(?P<index>\d+),:3,:(?P<samples>\d+)$")

UNIFIED_COLUMNS = [
    "global_id",
    "dataset",
    "record_id",
    "event_id",
    "station_network_code",
    "station_code",
    "original_split",
    "split",
    "waveform_store",
    "hdf5_key",
    "hdf5_index",
    "sample_start",
    "sample_stop",
    "component_order",
    "dimension_order",
    "n_components",
    "n_samples",
    "sampling_rate_hz",
    "trace_start_time",
    "detection_label",
    "p_pick_sample",
    "s_pick_sample",
    "p_pick_sec",
    "s_pick_sec",
    "source_magnitude",
    "source_magnitude_type",
    "source_depth_km",
    "source_latitude_deg",
    "source_longitude_deg",
    "source_distance_km",
    "source_distance_deg",
    "station_latitude_deg",
    "station_longitude_deg",
    "station_elevation_m",
    "station_vs30_mps",
    "pga_cmps2",
    "pgv_cmps",
    "sa03_cmps2",
    "sa10_cmps2",
    "sa30_cmps2",
    "snr_db",
    "trace_category",
    "year",
    "has_phase_task",
    "has_detection_task",
    "has_ground_motion_task",
    "source_metadata_path",
    "unit_notes",
]


def clean(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    return str(value)


def number(value: Any) -> float | None:
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def integer(value: Any) -> int | None:
    val = number(value)
    if val is None:
        return None
    return int(round(val))


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if not math.isfinite(value):
            return ""
        return f"{value:.8g}"
    return clean(value)


def normalize_split(split: Any) -> str:
    s = clean(split).lower()
    if s == "dev":
        return "val"
    if s in {"train", "val", "test"}:
        return s
    return s


def parse_trace_name(trace_name: Any) -> tuple[str, str, str, str]:
    name = clean(trace_name)
    match = TRACE_RE.match(name)
    if not match:
        return "", "", "", ""
    return f"/data/{match.group('bucket')}", match.group("index"), "0", match.group("samples")


def pick_seconds(sample: Any, sampling_rate_hz: Any = None, dt_s: Any = None) -> str:
    sample_i = integer(sample)
    if sample_i is None:
        return ""
    sr = number(sampling_rate_hz)
    if sr and sr > 0:
        return f"{sample_i / sr:.6f}"
    dt = number(dt_s)
    if dt and dt > 0:
        return f"{sample_i * dt:.6f}"
    return ""


def year_from_time(value: Any) -> str:
    s = clean(value)
    return s[:4] if len(s) >= 4 and s[:4].isdigit() else ""


def write_rows(path: Path, rows: Iterable[dict[str, Any]], append: bool) -> int:
    mode = "at" if append else "wt"
    count = 0
    with gzip.open(path, mode, newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=UNIFIED_COLUMNS)
        if not append:
            writer.writeheader()
        for row in rows:
            writer.writerow({col: fmt(row.get(col, "")) for col in UNIFIED_COLUMNS})
            count += 1
    return count


def seisbench_rows(dataset: str, metadata_path: Path, waveform_store: Path, chunk: pd.DataFrame) -> Iterable[dict[str, Any]]:
    ds = dataset.lower()
    for row_idx, row in chunk.iterrows():
        hdf5_key, hdf5_index, sample_start, sample_stop = parse_trace_name(row.get("trace_name"))
        n_samples = sample_stop
        original_split = row.get("split")
        split = normalize_split(original_split)
        station = clean(row.get("station_code"))
        source_id = clean(row.get("source_id"))
        trace_name = clean(row.get("trace_name"))
        record_id = trace_name or f"{ds}:{row_idx}"
        event_id = source_id
        sampling = row.get("trace_sampling_rate_hz")
        dt_s = row.get("trace_dt_s")
        if clean(sampling) == "" and number(dt_s):
            sampling = 1.0 / number(dt_s)

        p_sample = row.get("trace_p_arrival_sample", row.get("trace_P_arrival_sample"))
        s_sample = row.get("trace_s_arrival_sample", row.get("trace_S_arrival_sample"))
        trace_category = clean(row.get("trace_category"))
        detection_label = ""
        if trace_category:
            detection_label = "0" if trace_category == "noise" else "1"
        elif clean(p_sample) or clean(s_sample):
            detection_label = "1"

        pga = row.get("trace_pga_cmps2")
        pgv = row.get("trace_pgv_cmps")
        sa03 = row.get("trace_sa03_cmps2")
        sa10 = row.get("trace_sa10_cmps2")
        sa30 = row.get("trace_sa30_cmps2")
        has_ground = any(clean(x) for x in [pga, pgv, sa03, sa10, sa30])

        yield {
            "global_id": f"{ds}:{record_id}",
            "dataset": ds,
            "record_id": record_id,
            "event_id": event_id,
            "station_network_code": row.get("station_network_code"),
            "station_code": station,
            "original_split": original_split,
            "split": split,
            "waveform_store": waveform_store,
            "hdf5_key": hdf5_key,
            "hdf5_index": hdf5_index,
            "sample_start": sample_start,
            "sample_stop": sample_stop,
            "component_order": row.get("trace_component_order", "ZNE"),
            "dimension_order": "NCW",
            "n_components": 3,
            "n_samples": n_samples or row.get("trace_npts"),
            "sampling_rate_hz": sampling,
            "trace_start_time": row.get("trace_start_time"),
            "detection_label": detection_label,
            "p_pick_sample": p_sample,
            "s_pick_sample": s_sample,
            "p_pick_sec": pick_seconds(p_sample, sampling, dt_s),
            "s_pick_sec": pick_seconds(s_sample, sampling, dt_s),
            "source_magnitude": row.get("source_magnitude"),
            "source_magnitude_type": row.get("source_magnitude_type"),
            "source_depth_km": row.get("source_depth_km"),
            "source_latitude_deg": row.get("source_latitude_deg"),
            "source_longitude_deg": row.get("source_longitude_deg"),
            "source_distance_km": row.get("source_distance_km", row.get("path_ep_distance_km")),
            "source_distance_deg": row.get("source_distance_deg"),
            "station_latitude_deg": row.get("station_latitude_deg"),
            "station_longitude_deg": row.get("station_longitude_deg"),
            "station_elevation_m": row.get("station_elevation_m"),
            "station_vs30_mps": row.get("station_vs_30_mps"),
            "pga_cmps2": pga,
            "pgv_cmps": pgv,
            "sa03_cmps2": sa03,
            "sa10_cmps2": sa10,
            "sa30_cmps2": sa30,
            "snr_db": row.get("trace_snr_db"),
            "trace_category": trace_category,
            "year": year_from_time(row.get("source_origin_time", row.get("trace_start_time"))),
            "has_phase_task": int(bool(clean(p_sample) or clean(s_sample))),
            "has_detection_task": int(bool(clean(detection_label))),
            "has_ground_motion_task": int(has_ground),
            "source_metadata_path": metadata_path,
            "unit_notes": "SeisBench source units; InstanceGM ground-motion targets are cm/s/s and cm/s where populated.",
        }


def knet_rows(manifest_path: Path, chunk: pd.DataFrame) -> Iterable[dict[str, Any]]:
    for _, row in chunk.iterrows():
        event_id = clean(row.get("event_id"))
        yield {
            "global_id": f"knet:{row.get('record_id')}",
            "dataset": "knet",
            "record_id": row.get("record_id"),
            "event_id": event_id,
            "station_network_code": "KNET",
            "station_code": row.get("station_code"),
            "original_split": row.get("split"),
            "split": normalize_split(row.get("split")),
            "waveform_store": row.get("waveform_hdf5"),
            "hdf5_key": row.get("hdf5_key"),
            "hdf5_index": row.get("dataset_index"),
            "sample_start": 0,
            "sample_stop": row.get("n_samples"),
            "component_order": row.get("component_order"),
            "dimension_order": "CW",
            "n_components": 3,
            "n_samples": row.get("n_samples"),
            "sampling_rate_hz": row.get("sampling_rate_hz"),
            "trace_start_time": row.get("record_time"),
            "detection_label": row.get("detection"),
            "p_pick_sample": row.get("p_pick_sample"),
            "s_pick_sample": row.get("s_pick_sample"),
            "p_pick_sec": row.get("p_pick_sec"),
            "s_pick_sec": row.get("s_pick_sec"),
            "source_magnitude": row.get("magnitude"),
            "source_magnitude_type": "",
            "source_depth_km": row.get("source_depth_km"),
            "source_latitude_deg": row.get("source_latitude_deg"),
            "source_longitude_deg": row.get("source_longitude_deg"),
            "source_distance_km": row.get("source_distance_km"),
            "source_distance_deg": "",
            "station_latitude_deg": row.get("station_latitude_deg"),
            "station_longitude_deg": row.get("station_longitude_deg"),
            "station_elevation_m": row.get("station_elevation_m"),
            "station_vs30_mps": "",
            "pga_cmps2": row.get("pga_gal"),
            "pgv_cmps": "",
            "sa03_cmps2": "",
            "sa10_cmps2": "",
            "sa30_cmps2": "",
            "snr_db": "",
            "trace_category": "earthquake_local",
            "year": row.get("year"),
            "has_phase_task": int(bool(clean(row.get("p_pick_sample")) or clean(row.get("s_pick_sample")))),
            "has_detection_task": 1,
            "has_ground_motion_task": int(bool(clean(row.get("pga_gal")))),
            "source_metadata_path": manifest_path,
            "unit_notes": "K-NET pga_gal is treated as cm/s/s pending source documentation verification.",
        }


def update_summary(summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    for row in rows:
        ds = row["dataset"]
        item = summary.setdefault(
            ds,
            {
                "rows": 0,
                "split_counts": Counter(),
                "phase_rows": 0,
                "detection_rows": 0,
                "ground_motion_rows": 0,
                "min_samples": None,
                "max_samples": None,
            },
        )
        item["rows"] += 1
        item["split_counts"][row.get("split", "")] += 1
        item["phase_rows"] += int(row.get("has_phase_task") or 0)
        item["detection_rows"] += int(row.get("has_detection_task") or 0)
        item["ground_motion_rows"] += int(row.get("has_ground_motion_task") or 0)
        n = integer(row.get("n_samples"))
        if n is not None:
            item["min_samples"] = n if item["min_samples"] is None else min(item["min_samples"], n)
            item["max_samples"] = n if item["max_samples"] is None else max(item["max_samples"], n)


def serializable_summary(summary: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for ds, item in summary.items():
        out[ds] = dict(item)
        out[ds]["split_counts"] = dict(item["split_counts"])
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--chunksize", type=int, default=100_000)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    output_path = args.out_dir / "unified_manifest.csv.gz"
    summary_path = args.out_dir / "unified_manifest_summary.json"
    if output_path.exists():
        output_path.unlink()

    datasets = [
        (
            "stead",
            Path("/Users/yojironoda/.seisbench/datasets/stead/metadata.csv"),
            Path("/Users/yojironoda/.seisbench/datasets/stead/waveforms.hdf5"),
        ),
        (
            "instancegm",
            Path("/Users/yojironoda/.seisbench/datasets/instancegm/metadata.csv"),
            Path("/Users/yojironoda/.seisbench/datasets/instancegm/waveforms.hdf5"),
        ),
        (
            "iquique",
            Path("/Users/yojironoda/.seisbench/datasets/iquique/metadata.csv"),
            Path("/Users/yojironoda/.seisbench/datasets/iquique/waveforms.hdf5"),
        ),
    ]

    summary: dict[str, Any] = {}
    append = False
    total_rows = 0
    for dataset, metadata_path, waveform_store in datasets:
        for chunk in pd.read_csv(metadata_path, chunksize=args.chunksize, low_memory=False):
            rows = list(seisbench_rows(dataset, metadata_path, waveform_store, chunk))
            update_summary(summary, rows)
            total_rows += write_rows(output_path, rows, append=append)
            append = True
        print(f"processed {dataset}", flush=True)

    knet_manifest = Path("work/knet_converted/knet_full_manifest.csv")
    for chunk in pd.read_csv(knet_manifest, chunksize=args.chunksize, dtype={"event_id": str}, low_memory=False):
        rows = list(knet_rows(knet_manifest, chunk))
        update_summary(summary, rows)
        total_rows += write_rows(output_path, rows, append=append)
        append = True
    print("processed knet", flush=True)

    report = {
        "unified_manifest": str(output_path),
        "rows": total_rows,
        "columns": UNIFIED_COLUMNS,
        "datasets": serializable_summary(summary),
    }
    summary_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
