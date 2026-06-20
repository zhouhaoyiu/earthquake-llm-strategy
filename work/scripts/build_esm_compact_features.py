#!/usr/bin/env python3
"""Build compact early-window features from local ESM ASCII zip packages."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


COMPONENTS = ["z", "n", "e"]


def to_float(value: Any) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        out = float(str(value).strip())
        return out if math.isfinite(out) else None
    except Exception:
        return None


def parse_datetime(value: str) -> datetime | None:
    value = value.strip()
    for fmt in ("%Y%m%d_%H%M%S.%f", "%Y%m%d_%H%M%S", "%Y%m%d%H%M%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None


def read_ascii_member(zf: zipfile.ZipFile, name: str) -> tuple[dict[str, str], np.ndarray]:
    with zf.open(name) as fh:
        text = fh.read().decode("utf-8", errors="replace").splitlines()
    header: dict[str, str] = {}
    data_start = 0
    for idx, line in enumerate(text):
        if ":" not in line:
            data_start = idx
            break
        key, value = line.split(":", 1)
        header[key.strip()] = value.strip()
    values = []
    for line in text[data_start:]:
        line = line.strip()
        if not line:
            continue
        try:
            values.append(float(line))
        except ValueError:
            continue
    return header, np.asarray(values, dtype=np.float32)


def component_from_stream(stream: str) -> str | None:
    if not stream:
        return None
    suffix = stream[-1].upper()
    if suffix in {"Z", "U"}:
        return "z"
    if suffix == "N":
        return "n"
    if suffix == "E":
        return "e"
    return None


def station_key(header: dict[str, str]) -> tuple[str, str, str]:
    return (
        header.get("NETWORK", ""),
        header.get("STATION_CODE", ""),
        header.get("LOCATION", ""),
    )


def origin_time(header: dict[str, str]) -> datetime | None:
    return parse_datetime(header.get("EVENT_DATE_YYYYMMDD", "") + header.get("EVENT_TIME_HHMMSS", ""))


def p_offset_seconds(header: dict[str, str], vp_km_s: float) -> float | None:
    origin = origin_time(header)
    first = parse_datetime(header.get("DATE_TIME_FIRST_SAMPLE_YYYYMMDD_HHMMSS", ""))
    epi = to_float(header.get("EPICENTRAL_DISTANCE_KM"))
    depth = to_float(header.get("EVENT_DEPTH_KM")) or 0.0
    if origin is None or first is None or epi is None or epi < 0 or vp_km_s <= 0:
        return None
    hypo = math.sqrt(epi * epi + depth * depth)
    return (origin - first).total_seconds() + hypo / vp_km_s


def target_peak(components: dict[str, np.ndarray]) -> float | None:
    arrays = [arr for arr in components.values() if arr.size]
    if not arrays:
        return None
    n = min(arr.size for arr in arrays)
    if n <= 0:
        return None
    stack = np.vstack([arr[:n] for arr in arrays])
    vec = np.sqrt(np.sum(stack * stack, axis=0))
    out = float(np.nanmax(np.abs(vec)))
    return out if math.isfinite(out) and out > 0 else None


def waveform_features(components: dict[str, np.ndarray], header: dict[str, str], seconds: float, vp_km_s: float) -> dict[str, Any]:
    dt = to_float(header.get("SAMPLING_INTERVAL_S"))
    p_offset = p_offset_seconds(header, vp_km_s)
    feats: dict[str, Any] = {
        "early_seconds": float(seconds),
        "p_arrival_offset_s": p_offset,
        "p_time_method": f"theoretical_vp_{vp_km_s:g}kmps",
        "p_window_valid": False,
    }
    if dt is None or dt <= 0 or p_offset is None or p_offset < 0:
        return feats
    start = max(0, int(round(p_offset / dt)))
    stop = start + int(round(seconds / dt))
    windows: dict[str, np.ndarray] = {}
    for comp in COMPONENTS:
        arr = components.get(comp)
        if arr is None or arr.size <= start:
            continue
        windows[comp] = arr[start : min(arr.size, stop)]
    if not windows:
        return feats
    feats["p_window_valid"] = True
    for comp in COMPONENTS:
        win = windows.get(comp)
        if win is None or win.size == 0:
            continue
        abs_win = np.abs(win)
        feats[f"{comp}_early_absmax"] = float(np.nanmax(abs_win))
        feats[f"{comp}_early_rms"] = float(np.sqrt(np.nanmean(win * win)))
        feats[f"{comp}_early_std"] = float(np.nanstd(win))
        feats[f"{comp}_early_p95_abs"] = float(np.nanpercentile(abs_win, 95))
    if "n" in windows and "e" in windows:
        n = min(windows["n"].size, windows["e"].size)
        horiz = np.sqrt(windows["n"][:n] ** 2 + windows["e"][:n] ** 2)
        feats["h_early_absmax"] = float(np.nanmax(horiz))
    if windows:
        n = min(arr.size for arr in windows.values())
        stack = np.vstack([arr[:n] for arr in windows.values()])
        vec = np.sqrt(np.sum(stack * stack, axis=0))
        feats["vec_early_absmax"] = float(np.nanmax(vec))
        feats["vec_early_rms"] = float(np.sqrt(np.nanmean(vec * vec)))
    return feats


def base_record(header: dict[str, str], zip_path: Path) -> dict[str, Any]:
    magnitude = to_float(header.get("MAGNITUDE_W")) or to_float(header.get("MAGNITUDE_L"))
    epi = to_float(header.get("EPICENTRAL_DISTANCE_KM"))
    depth = to_float(header.get("EVENT_DEPTH_KM")) or 0.0
    hypo = math.sqrt(epi * epi + depth * depth) if epi is not None else None
    network, station, location = station_key(header)
    event_id = header.get("EVENT_ID", "")
    station_group = f"{network}.{station}" if network or station else ""
    if location:
        station_group = f"{station_group}.{location}"
    return {
        "global_id": f"esm:{event_id}:{station_group}",
        "record_id": f"{event_id}:{station_group}",
        "event_id": event_id,
        "source_id": event_id,
        "station_network_code": network,
        "station_code": station,
        "station_group": station_group,
        "dataset": "esm",
        "split": "",
        "source_latitude_deg": to_float(header.get("EVENT_LATITUDE_DEGREE")),
        "source_longitude_deg": to_float(header.get("EVENT_LONGITUDE_DEGREE")),
        "station_latitude_deg": to_float(header.get("STATION_LATITUDE_DEGREE")),
        "station_longitude_deg": to_float(header.get("STATION_LONGITUDE_DEGREE")),
        "source_magnitude": magnitude,
        "source_depth_km": to_float(header.get("EVENT_DEPTH_KM")),
        "source_distance_km": epi,
        "path_ep_distance_km": epi,
        "path_hyp_distance_km": hypo,
        "path_back_azimuth_deg": to_float(header.get("EARTHQUAKE_BACKAZIMUTH_DEGREE")),
        "station_elevation_m": to_float(header.get("STATION_ELEVATION_M")),
        "station_vs30_mps": to_float(header.get("VS30_M/S")),
        "site_classification_ec8": header.get("SITE_CLASSIFICATION_EC8", ""),
        "trace_npts": to_float(header.get("NDATA")),
        "trace_sampling_rate_hz": 1.0 / to_float(header.get("SAMPLING_INTERVAL_S")) if to_float(header.get("SAMPLING_INTERVAL_S")) else None,
        "source_origin_time": origin_time(header).isoformat(sep=" ") if origin_time(header) else "",
        "trace_start_time": header.get("DATE_TIME_FIRST_SAMPLE_YYYYMMDD_HHMMSS", ""),
        "zip_path": str(zip_path),
    }


def process_zip(zip_path: Path, windows: list[float], vp_km_s: float) -> tuple[list[dict[str, Any]], list[dict[str, str]], int]:
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    skipped_windows = 0
    with zipfile.ZipFile(zip_path) as zf:
        names = [name for name in zf.namelist() if name.endswith(".ASC")]
        acc_names = [name for name in names if ".ACC.AP." in name]
        vel_names = {name.replace(".VEL.AP.", ".ACC.AP."): name for name in names if ".VEL.AP." in name}
        grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
        for name in acc_names:
            try:
                header, data = read_ascii_member(zf, name)
            except Exception as exc:
                errors.append({"zip_path": str(zip_path), "member": name, "error": repr(exc)})
                continue
            comp = component_from_stream(header.get("STREAM", ""))
            if comp is None:
                continue
            key = station_key(header)
            group = grouped.setdefault(key, {"header": header, "acc": {}, "vel": {}})
            group["acc"][comp] = data
            vel_name = vel_names.get(name)
            if vel_name:
                try:
                    _, vel_data = read_ascii_member(zf, vel_name)
                    group["vel"][comp] = vel_data
                except Exception as exc:
                    errors.append({"zip_path": str(zip_path), "member": vel_name, "error": repr(exc)})

        for group in grouped.values():
            header = group["header"]
            pga = target_peak(group["acc"])
            pgv = target_peak(group["vel"])
            if pga is None:
                continue
            base = base_record(header, zip_path)
            base["target_pga"] = pga
            base["target_log10_pga"] = math.log10(pga)
            base["target_pgv"] = pgv
            base["target_log10_pgv"] = math.log10(pgv) if pgv and pgv > 0 else np.nan
            for seconds in windows:
                row = dict(base)
                row.update(waveform_features(group["acc"], header, seconds, vp_km_s))
                if not row.get("p_window_valid"):
                    skipped_windows += 1
                    continue
                rows.append(row)
    return rows, errors, skipped_windows


def write_summary(
    path: Path,
    features: pd.DataFrame,
    errors: list[dict[str, str]],
    feature_path: Path,
    error_path: Path,
    report_path: Path,
    skipped_windows: int,
    args: argparse.Namespace,
) -> None:
    pga_nonmissing = int(features["target_pga"].notna().sum()) if "target_pga" in features else 0
    pgv_nonmissing = int(features["target_pgv"].notna().sum()) if "target_pgv" in features else 0
    pgv_missing = int(features["target_pgv"].isna().sum()) if "target_pgv" in features else 0
    lines = [
        "# Local ESM compact feature table",
        "",
        "This table is generated from local ESM ASCII zip packages. Raw zip files are read in place and left unchanged.",
        "",
        "P-arrival windows use a deterministic theoretical onset from origin time, first sample time, epicentral distance, depth, and a fixed P velocity.",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Zip files requested | {args.max_zips or 'all'} |",
        f"| Feature rows | {len(features)} |",
        f"| Events | {features['event_id'].nunique() if not features.empty else 0} |",
        f"| Stations | {features['station_group'].nunique() if not features.empty else 0} |",
        f"| Non-missing PGA rows | {pga_nonmissing} |",
        f"| Non-missing PGV rows | {pgv_nonmissing} |",
        f"| Missing PGV rows | {pgv_missing} |",
        f"| Windows | {', '.join(str(w) for w in args.windows)} |",
        f"| P velocity km/s | {args.vp_km_s:g} |",
        f"| Skipped invalid P windows | {skipped_windows} |",
        f"| Read errors | {len(errors)} |",
        "",
        "Files:",
        f"- `{feature_path}`",
        f"- `{error_path}`",
        f"- `{report_path}`",
    ]
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--esm-dir", type=Path, default=Path("/Users/yojironoda/Documents/New project 2/outputs/strong_motion_downloads/欧洲_ESM"))
    parser.add_argument("--out-dir", type=Path, default=Path("work/esm_compact_features_pilot"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/esm_compact_features_pilot_summary.md"))
    parser.add_argument("--windows", nargs="+", type=float, default=[1.0, 2.0, 3.0, 5.0, 10.0])
    parser.add_argument("--max-zips", type=int, default=25)
    parser.add_argument("--vp-km-s", type=float, default=6.0)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)

    zip_paths = sorted(args.esm_dir.rglob("*.zip"))
    if args.max_zips:
        zip_paths = zip_paths[: args.max_zips]

    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    skipped_windows = 0
    for idx, zip_path in enumerate(zip_paths, 1):
        print(f"[{idx}/{len(zip_paths)}] {zip_path}", flush=True)
        zip_rows, zip_errors, zip_skipped_windows = process_zip(zip_path, args.windows, args.vp_km_s)
        rows.extend(zip_rows)
        errors.extend(zip_errors)
        skipped_windows += zip_skipped_windows

    features = pd.DataFrame(rows)
    feature_path = args.out_dir / "esm_compact_features.csv.gz"
    features.to_csv(feature_path, index=False, compression="gzip")

    error_path = args.out_dir / "esm_compact_feature_errors.csv"
    with error_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["zip_path", "member", "error"])
        writer.writeheader()
        writer.writerows(errors)

    report_path = args.out_dir / "esm_compact_feature_summary.json"
    report = {
        "feature_path": str(feature_path),
        "summary": str(args.summary),
        "zip_files": len(zip_paths),
        "feature_rows": int(len(features)),
        "events": int(features["event_id"].nunique()) if not features.empty else 0,
        "stations": int(features["station_group"].nunique()) if not features.empty else 0,
        "target_pga_nonmissing_rows": int(features["target_pga"].notna().sum()) if "target_pga" in features else 0,
        "target_pgv_nonmissing_rows": int(features["target_pgv"].notna().sum()) if "target_pgv" in features else 0,
        "target_pgv_missing_rows": int(features["target_pgv"].isna().sum()) if "target_pgv" in features else 0,
        "errors": len(errors),
        "skipped_invalid_p_windows": skipped_windows,
        "p_time_method": f"theoretical_vp_{args.vp_km_s:g}kmps",
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    if features.empty:
        with gzip.open(feature_path, "wt") as fh:
            fh.write("")
    write_summary(args.summary, features, errors, feature_path, error_path, report_path, skipped_windows, args)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
