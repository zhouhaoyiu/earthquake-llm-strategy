#!/usr/bin/env python3
"""Convert the local K-NET BSON package into HDF5 waveforms plus a CSV manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import h5py
import numpy as np
from bson import decode_file_iter


COMPONENT_TO_INDEX = {"UD": 0, "NS": 1, "EW": 2}
COMPONENT_ORDER = "ZNE"
CSV_COLUMNS = [
    "record_id",
    "event_id",
    "station_code",
    "dataset_index",
    "waveform_hdf5",
    "hdf5_key",
    "component_order",
    "n_samples",
    "split",
    "detection",
    "p_pick_sample",
    "s_pick_sample",
    "p_pick_sec",
    "s_pick_sec",
    "magnitude",
    "pga_gal",
    "source_distance_km",
    "source_depth_km",
    "source_latitude_deg",
    "source_longitude_deg",
    "station_latitude_deg",
    "station_longitude_deg",
    "station_elevation_m",
    "duration_s",
    "sampling_rate_hz",
    "year",
    "has_UD",
    "has_NS",
    "has_EW",
    "origin_time",
    "record_time",
    "last_corrected",
]


def as_float(value: Any) -> float | None:
    try:
        if value in ("", None):
            return None
        return float(value)
    except Exception:
        return None


def as_int(value: Any) -> int | None:
    try:
        if value in ("", None):
            return None
        return int(float(value))
    except Exception:
        return None


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    return str(value)


def split_for_event(event_id: str) -> str:
    bucket = int(hashlib.sha1(event_id.encode("utf-8")).hexdigest()[:8], 16) % 100
    if bucket < 80:
        return "train"
    if bucket < 90:
        return "val"
    return "test"


def read_headers(header_path: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    headers: list[dict[str, Any]] = []
    header_by_id: dict[str, dict[str, Any]] = {}
    with header_path.open("rb") as fh:
        for doc in decode_file_iter(fh):
            record_id = str(doc["_id"])
            doc = dict(doc)
            doc["record_id"] = record_id
            headers.append(doc)
            header_by_id[record_id] = doc
    return headers, header_by_id


def parse_acc_id(acc_id: str) -> tuple[str, str]:
    if "." not in acc_id:
        raise ValueError(f"Accelerogram _id has no component suffix: {acc_id}")
    record_id, component = acc_id.rsplit(".", 1)
    return record_id, component


def write_manifest(
    manifest_path: Path,
    waveform_path: Path,
    headers: list[dict[str, Any]],
    record_to_index: dict[str, int],
    component_seen: dict[str, set[str]],
    record_lengths: dict[str, int],
) -> Counter:
    split_counts: Counter = Counter()
    with manifest_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for header in headers:
            record_id = header["record_id"]
            if record_id not in record_to_index:
                continue
            event_id = text(header.get("EventName"))
            sr = as_float(header.get("SamplingRate_Hz"))
            p_sample = as_int(header.get("pIndex")) if as_bool(header.get("p")) else None
            s_sample = as_int(header.get("sIndex")) if as_bool(header.get("s")) else None
            split = split_for_event(event_id)
            split_counts[split] += 1
            seen = component_seen.get(record_id, set())
            row = {
                "record_id": record_id,
                "event_id": event_id,
                "station_code": text(header.get("StationCode")),
                "dataset_index": record_to_index[record_id],
                "waveform_hdf5": str(waveform_path),
                "hdf5_key": f"/waveforms/{record_id}",
                "component_order": COMPONENT_ORDER,
                "n_samples": record_lengths.get(record_id, ""),
                "split": split,
                "detection": 1 if as_bool(header.get("p")) or as_bool(header.get("s")) else 0,
                "p_pick_sample": "" if p_sample is None else p_sample,
                "s_pick_sample": "" if s_sample is None else s_sample,
                "p_pick_sec": "" if p_sample is None or not sr else f"{p_sample / sr:.6f}",
                "s_pick_sec": "" if s_sample is None or not sr else f"{s_sample / sr:.6f}",
                "magnitude": text(header.get("Magnitude")),
                "pga_gal": text(header.get("PGA_gal")),
                "source_distance_km": text(header.get("Distance")),
                "source_depth_km": text(header.get("Depth_km")),
                "source_latitude_deg": text(header.get("Latitude")),
                "source_longitude_deg": text(header.get("Longitude")),
                "station_latitude_deg": text(header.get("StationLat")),
                "station_longitude_deg": text(header.get("StationLong")),
                "station_elevation_m": text(header.get("StationHeight_m")),
                "duration_s": text(header.get("Duration_s")),
                "sampling_rate_hz": text(header.get("SamplingRate_Hz")),
                "year": text(header.get("Year")),
                "has_UD": int("UD" in seen),
                "has_NS": int("NS" in seen),
                "has_EW": int("EW" in seen),
                "origin_time": text(header.get("OriginTime")),
                "record_time": text(header.get("RecordTime")),
                "last_corrected": text(header.get("LastCorrected")),
            }
            writer.writerow(row)
    return split_counts


def convert_full(args: argparse.Namespace) -> dict[str, Any]:
    header_path = args.input_dir / "header.bson"
    acc_path = args.input_dir / "accelerogram.bson"
    headers, header_by_id = read_headers(header_path)
    record_to_index = {header["record_id"]: i for i, header in enumerate(headers)}
    n_records = len(headers)

    component_seen: dict[str, set[str]] = {record_id: set() for record_id in record_to_index}
    component_counts: Counter = Counter()
    length_counts: Counter = Counter()
    record_lengths: dict[str, int] = {}
    unknown_components: Counter = Counter()
    unknown_records = 0
    acc_docs = 0

    with acc_path.open("rb") as fh:
        for doc in decode_file_iter(fh):
            record_id, component = parse_acc_id(str(doc["_id"]))
            if component not in COMPONENT_TO_INDEX:
                unknown_components[component] += 1
                continue
            if record_id not in record_to_index:
                unknown_records += 1
                continue
            n_values = len(doc["accelerogram"])
            length_counts[n_values] += 1
            previous = record_lengths.get(record_id)
            if previous is None:
                record_lengths[record_id] = n_values
            elif previous != n_values:
                raise ValueError(
                    f"Inconsistent component lengths for {record_id}: {previous} and {n_values}"
                )

    with h5py.File(args.waveforms, "w") as h5:
        root = h5.create_group("waveforms")
        root.attrs["component_order"] = COMPONENT_ORDER
        root.attrs["dimension_order"] = "CW"
        root.attrs["measurement"] = "acceleration"
        root.attrs["unit"] = "gal_unverified"
        root.attrs["source"] = str(args.input_dir)

        with acc_path.open("rb") as fh:
            for doc in decode_file_iter(fh):
                acc_docs += 1
                record_id, component = parse_acc_id(str(doc["_id"]))
                if component not in COMPONENT_TO_INDEX:
                    continue
                if record_id not in record_to_index:
                    continue
                values = np.asarray(doc["accelerogram"], dtype=np.float32)
                if record_id not in root:
                    n_values = record_lengths[record_id]
                    dset = root.create_dataset(
                        record_id,
                        shape=(3, n_values),
                        dtype="float32",
                        compression=args.compression,
                        shuffle=args.compression is not None,
                        chunks=(3, min(n_values, 4096)),
                    )
                    dset.attrs["component_order"] = COMPONENT_ORDER
                    dset.attrs["dimension_order"] = "CW"
                else:
                    dset = root[record_id]
                if values.shape[0] != dset.shape[1]:
                    raise ValueError(f"Inconsistent sample count for {doc['_id']}: {values.shape[0]}")
                dset[COMPONENT_TO_INDEX[component], :] = values
                component_seen[record_id].add(component)
                component_counts[component] += 1

                if args.progress and acc_docs % args.progress == 0:
                    print(f"processed_acc_docs={acc_docs}", flush=True)

    complete_records = sum(1 for comps in component_seen.values() if set(COMPONENT_TO_INDEX) <= comps)
    split_counts = write_manifest(
        args.manifest,
        args.waveforms,
        headers,
        record_to_index,
        component_seen,
        record_lengths,
    )
    missing_counts = Counter()
    for comps in component_seen.values():
        for comp in COMPONENT_TO_INDEX:
            if comp not in comps:
                missing_counts[comp] += 1

    return {
        "mode": "full",
        "input_dir": str(args.input_dir),
        "waveforms": str(args.waveforms),
        "manifest": str(args.manifest),
        "records": n_records,
        "accelerogram_docs": acc_docs,
        "complete_records": complete_records,
        "component_order": COMPONENT_ORDER,
        "variable_length_records": True,
        "length_counts_top": dict(length_counts.most_common(20)),
        "min_samples_per_component": min(length_counts) if length_counts else None,
        "max_samples_per_component": max(length_counts) if length_counts else None,
        "component_counts": dict(component_counts),
        "missing_component_counts": dict(missing_counts),
        "unknown_component_counts": dict(unknown_components),
        "unknown_accelerogram_records": unknown_records,
        "split_counts": dict(split_counts),
        "unit_note": "Accelerogram values are stored as acceleration; gal consistency should be verified against K-NET documentation before publication.",
    }


def convert_sample(args: argparse.Namespace) -> dict[str, Any]:
    header_path = args.input_dir / "header.bson"
    acc_path = args.input_dir / "accelerogram.bson"
    _, header_by_id = read_headers(header_path)
    groups: dict[str, dict[str, np.ndarray]] = {}
    acc_docs = 0

    with acc_path.open("rb") as fh:
        for doc in decode_file_iter(fh):
            acc_docs += 1
            record_id, component = parse_acc_id(str(doc["_id"]))
            if component not in COMPONENT_TO_INDEX or record_id not in header_by_id:
                continue
            groups.setdefault(record_id, {})[component] = np.asarray(doc["accelerogram"], dtype=np.float32)
            complete = [rid for rid, comps in groups.items() if set(COMPONENT_TO_INDEX) <= set(comps)]
            if len(complete) >= args.sample_records:
                break

    complete_ids = [rid for rid, comps in groups.items() if set(COMPONENT_TO_INDEX) <= set(comps)]
    complete_ids = complete_ids[: args.sample_records]
    if not complete_ids:
        raise RuntimeError("No complete records found in sample scan")

    n_samples = len(groups[complete_ids[0]]["UD"])
    headers = [header_by_id[rid] for rid in complete_ids]
    for i, header in enumerate(headers):
        header["record_id"] = complete_ids[i]
    record_to_index = {rid: i for i, rid in enumerate(complete_ids)}
    component_seen = {rid: set(groups[rid]) for rid in complete_ids}
    record_lengths = {rid: n_samples for rid in complete_ids}

    with h5py.File(args.waveforms, "w") as h5:
        root = h5.create_group("waveforms")
        root.attrs["component_order"] = COMPONENT_ORDER
        root.attrs["dimension_order"] = "CW"
        root.attrs["measurement"] = "acceleration"
        root.attrs["unit"] = "gal_unverified"
        for rid, idx in record_to_index.items():
            dset = root.create_dataset(rid, shape=(3, n_samples), dtype="float32")
            dset.attrs["component_order"] = COMPONENT_ORDER
            dset.attrs["dimension_order"] = "CW"
            for comp, comp_idx in COMPONENT_TO_INDEX.items():
                dset[comp_idx, :] = groups[rid][comp]

    split_counts = write_manifest(
        args.manifest,
        args.waveforms,
        headers,
        record_to_index,
        component_seen,
        record_lengths,
    )
    return {
        "mode": "sample",
        "input_dir": str(args.input_dir),
        "waveforms": str(args.waveforms),
        "manifest": str(args.manifest),
        "records": len(complete_ids),
        "accelerogram_docs_scanned": acc_docs,
        "record_ids": complete_ids,
        "component_order": COMPONENT_ORDER,
        "samples_per_component": n_samples,
        "split_counts": dict(split_counts),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=["sample", "full"], default="sample")
    parser.add_argument("--sample-records", type=int, default=8)
    parser.add_argument("--samples", type=int, default=11900)
    parser.add_argument("--compression", choices=["gzip", "lzf", "none"], default="lzf")
    parser.add_argument("--progress", type=int, default=5000)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.waveforms = args.out_dir / f"knet_{args.mode}_waveforms.hdf5"
    args.manifest = args.out_dir / f"knet_{args.mode}_manifest.csv"
    args.report = args.out_dir / f"knet_{args.mode}_convert_report.json"
    if args.compression == "none":
        args.compression = None
    return args


def main() -> None:
    args = parse_args()
    if args.mode == "sample":
        report = convert_sample(args)
    else:
        report = convert_full(args)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
