#!/usr/bin/env python3
"""PNW accelerometer early-window peak-amplitude baseline.

The cached PNWAccelerometers file identifies EN channels but does not store a
waveform unit in HDF5. The target is therefore reported as a full-record peak
horizontal waveform amplitude, not as publication-ready PGA.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline


TRACE_RE = re.compile(r"^(?P<bucket>[^$]+)\$(?P<index>\d+),:3,:(?P<samples>\d+)$")
METADATA_FEATURES = [
    "source_magnitude",
    "source_depth_km",
    "source_distance_km",
    "station_elevation_m",
    "year",
    "n_samples",
]


def haversine_km(lat1: pd.Series, lon1: pd.Series, lat2: pd.Series, lon2: pd.Series) -> pd.Series:
    radius = 6371.0
    phi1 = np.radians(pd.to_numeric(lat1, errors="coerce"))
    phi2 = np.radians(pd.to_numeric(lat2, errors="coerce"))
    dphi = phi2 - phi1
    dlambda = np.radians(pd.to_numeric(lon2, errors="coerce") - pd.to_numeric(lon1, errors="coerce"))
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    return pd.Series(2 * radius * np.arctan2(np.sqrt(a), np.sqrt(1 - a)))


def parse_trace_name(trace_name: str) -> tuple[str, int, int]:
    match = TRACE_RE.match(str(trace_name))
    if not match:
        raise ValueError(f"bad trace_name: {trace_name}")
    return match.group("bucket"), int(match.group("index")), int(match.group("samples"))


def load_metadata(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[
        df["source_type"].eq("earthquake")
        & pd.to_numeric(df["trace_missing_channel"], errors="coerce").fillna(1).eq(0)
    ].copy()
    df["source_magnitude"] = pd.to_numeric(df["preferred_source_magnitude"], errors="coerce")
    df["source_depth_km"] = pd.to_numeric(df["source_depth_km"], errors="coerce")
    df["station_elevation_m"] = pd.to_numeric(df["station_elevation_m"], errors="coerce")
    df["p_pick_sample"] = pd.to_numeric(df["trace_P_arrival_sample"], errors="coerce")
    df["sampling_rate_hz"] = pd.to_numeric(df["trace_sampling_rate_hz"], errors="coerce")
    df["source_distance_km"] = haversine_km(
        df["source_latitude_deg"],
        df["source_longitude_deg"],
        df["station_latitude_deg"],
        df["station_longitude_deg"],
    )
    df["year"] = df["source_origin_time"].astype(str).str[:4].where(
        df["source_origin_time"].astype(str).str[:4].str.isnumeric(), np.nan
    )
    parsed = df["trace_name"].apply(lambda name: pd.Series(parse_trace_name(name), index=["bucket", "hdf5_index", "n_samples"]))
    df = pd.concat([df, parsed], axis=1)
    return df.dropna(
        subset=["source_magnitude", "source_depth_km", "source_distance_km", "p_pick_sample", "sampling_rate_hz"]
    ).copy()


def feature_names(seconds: float) -> list[str]:
    label = f"w{seconds:g}s".replace(".", "p")
    return [
        f"{label}_e_absmax",
        f"{label}_n_absmax",
        f"{label}_z_absmax",
        f"{label}_h_absmax",
        f"{label}_h_rms",
        f"{label}_h_p95_abs",
    ]


def add_window_features(record: dict[str, Any], arr: np.ndarray, p_sample: int, sr: float, seconds: float) -> None:
    label = f"w{seconds:g}s".replace(".", "p")
    start = max(0, p_sample)
    stop = min(arr.shape[1], start + int(round(seconds * sr)))
    if stop <= start:
        for name in feature_names(seconds):
            record[name] = np.nan
        return
    win = arr[:, start:stop]
    abs_win = np.abs(win)
    horiz = np.sqrt(win[0] ** 2 + win[1] ** 2)
    record[f"{label}_e_absmax"] = float(np.nanmax(abs_win[0]))
    record[f"{label}_n_absmax"] = float(np.nanmax(abs_win[1]))
    record[f"{label}_z_absmax"] = float(np.nanmax(abs_win[2]))
    record[f"{label}_h_absmax"] = float(np.nanmax(np.abs(horiz)))
    record[f"{label}_h_rms"] = float(np.sqrt(np.nanmean(horiz * horiz)))
    record[f"{label}_h_p95_abs"] = float(np.nanpercentile(np.abs(horiz), 95))


def build_features(df: pd.DataFrame, waveform_path: Path, early_seconds: list[float]) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    with h5py.File(waveform_path, "r") as h5:
        for row in df.to_dict("records"):
            trace = row["trace_name"]
            try:
                arr = np.asarray(h5[f"data/{row['bucket']}"][int(row["hdf5_index"])], dtype=np.float64)
                horiz = np.sqrt(arr[0] ** 2 + arr[1] ** 2)
                target = float(np.nanmax(np.abs(horiz)))
                if not math.isfinite(target) or target <= 0:
                    continue
                rec: dict[str, Any] = {
                    "trace_name": trace,
                    "event_id": row["event_id"],
                    "station_network_code": row["station_network_code"],
                    "station_code": row["station_code"],
                    "source_magnitude": float(row["source_magnitude"]),
                    "source_depth_km": float(row["source_depth_km"]),
                    "source_distance_km": float(row["source_distance_km"]),
                    "station_elevation_m": float(row["station_elevation_m"]),
                    "year": float(row["year"]),
                    "n_samples": int(row["n_samples"]),
                    "p_pick_sample": int(row["p_pick_sample"]),
                    "sampling_rate_hz": float(row["sampling_rate_hz"]),
                    "target_peak_h_abs": target,
                    "target_log10_peak_h_abs": math.log10(target),
                }
                for seconds in early_seconds:
                    add_window_features(rec, arr, int(row["p_pick_sample"]), float(row["sampling_rate_hz"]), seconds)
                rows.append(rec)
            except Exception as exc:
                errors.append({"trace_name": trace, "error": repr(exc)})
    return pd.DataFrame(rows), errors


def group_key(df: pd.DataFrame, holdout: str) -> pd.Series:
    if holdout == "event":
        return df["event_id"].astype(str)
    if holdout == "station":
        return df["station_network_code"].astype(str) + "." + df["station_code"].astype(str)
    raise ValueError(holdout)


def split_by_group(
    df: pd.DataFrame,
    holdout: str,
    train_size: int,
    test_size: int,
    seed: int,
    station_test_groups: int,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    work = df.copy()
    work["_group"] = group_key(work, holdout)
    rng = np.random.default_rng(seed)
    sizes = work["_group"].value_counts()
    groups = np.array(sizes.index.tolist(), dtype=object)
    rng.shuffle(groups)

    test_groups: list[str] = []
    if holdout == "station" and station_test_groups:
        test_groups = list(groups[: min(station_test_groups, len(groups))])
    else:
        n_test = 0
        for group in groups:
            test_groups.append(group)
            n_test += int(sizes.loc[group])
            if n_test >= test_size:
                break

    test_set = set(test_groups)
    train = work[~work["_group"].isin(test_set)].copy()
    test = work[work["_group"].isin(test_set)].copy()
    if len(train) > train_size:
        train = train.sample(train_size, random_state=seed + 11)
    if len(test) > test_size:
        if holdout == "station" and test["_group"].nunique() <= test_size:
            keep = test.groupby("_group", group_keys=False).sample(1, random_state=seed + 17)
            rest = test.drop(index=keep.index)
            extra = rest.sample(test_size - len(keep), random_state=seed + 19)
            test = pd.concat([keep, extra]).sample(frac=1, random_state=seed + 23)
        else:
            test = test.sample(test_size, random_state=seed + 17)

    overlap = set(train["_group"]).intersection(set(test["_group"]))
    assert not overlap
    info = {
        "dataset": "pnwaccelerometers",
        "holdout": holdout,
        "eligible_rows": int(len(work)),
        "eligible_groups": int(work["_group"].nunique()),
        "train_rows_selected": int(len(train)),
        "test_rows_selected": int(len(test)),
        "train_groups": int(train["_group"].nunique()),
        "test_groups": int(test["_group"].nunique()),
        "group_overlap": int(len(overlap)),
    }
    return train.drop(columns=["_group"]), test.drop(columns=["_group"]), info


def train_eval(train: pd.DataFrame, test: pd.DataFrame, features: list[str], feature_set: str, holdout: str, seconds: float) -> dict[str, Any]:
    target = "target_log10_peak_h_abs"
    x_train = np.zeros((len(train), 1)) if not features else train[features]
    x_test = np.zeros((len(test), 1)) if not features else test[features]
    y_train = train[target].astype(float)
    y_test = test[target].astype(float)
    model = DummyRegressor(strategy="median") if not features else HistGradientBoostingRegressor(
        max_iter=200,
        learning_rate=0.05,
        max_leaf_nodes=31,
        random_state=17,
        l2_regularization=0.01,
    )
    pipe = make_pipeline(SimpleImputer(strategy="median"), model)
    pipe.fit(x_train, y_train)
    pred = pipe.predict(x_test)
    return {
        "dataset": "pnwaccelerometers",
        "target": "peak_horizontal_waveform_amplitude",
        "target_unit": "unknown_from_local_hdf5",
        "holdout": holdout,
        "early_seconds": seconds,
        "feature_set": feature_set,
        "features": features,
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "mae_log10_target": float(mean_absolute_error(y_test, pred)),
        "rmse_log10_target": float(mean_squared_error(y_test, pred) ** 0.5),
        "r2_log10_target": float(r2_score(y_test, pred)),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, default=Path("/Users/yojironoda/.seisbench/datasets/pnwaccelerometers/metadata.csv"))
    parser.add_argument("--waveforms", type=Path, default=Path("/Users/yojironoda/.seisbench/datasets/pnwaccelerometers/waveforms.hdf5"))
    parser.add_argument("--out-dir", type=Path, default=Path("work/pnw_accelerometer_peak_baseline"))
    parser.add_argument("--early-seconds", nargs="+", type=float, default=[1.0, 3.0, 10.0])
    parser.add_argument("--train-size", type=int, default=4000)
    parser.add_argument("--test-size", type=int, default=1000)
    parser.add_argument("--station-test-groups", type=int, default=40)
    parser.add_argument("--seed", type=int, default=83)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    metadata = load_metadata(args.metadata)
    features, errors = build_features(metadata, args.waveforms, args.early_seconds)
    features_path = args.out_dir / "pnw_accelerometer_peak_features.csv"
    errors_path = args.out_dir / "pnw_accelerometer_feature_errors.csv"
    features.to_csv(features_path, index=False)
    write_csv(errors_path, errors)

    results: list[dict[str, Any]] = []
    split_infos: list[dict[str, Any]] = []
    for holdout in ["event", "station"]:
        train, test, info = split_by_group(
            features,
            holdout=holdout,
            train_size=args.train_size,
            test_size=args.test_size,
            seed=args.seed + (101 if holdout == "station" else 0),
            station_test_groups=args.station_test_groups,
        )
        split_infos.append(info)
        train.to_csv(args.out_dir / f"pnw_accelerometer_held_{holdout}_train_features.csv", index=False)
        test.to_csv(args.out_dir / f"pnw_accelerometer_held_{holdout}_test_features.csv", index=False)
        for seconds in args.early_seconds:
            wave_cols = [col for col in feature_names(seconds) if col in features.columns]
            feature_sets = {
                "median": [],
                "metadata_only": [col for col in METADATA_FEATURES if col in features.columns],
                "early_waveform_only": wave_cols,
                "metadata_plus_early_waveform": [col for col in METADATA_FEATURES if col in features.columns] + wave_cols,
            }
            for feature_set, cols in feature_sets.items():
                result = train_eval(train, test, cols, feature_set, holdout, seconds)
                result["group_overlap"] = info["group_overlap"]
                results.append(result)
                print(holdout, seconds, feature_set, result["mae_log10_target"], result["r2_log10_target"], flush=True)

    results_path = args.out_dir / "pnw_accelerometer_peak_results.csv"
    split_path = args.out_dir / "pnw_accelerometer_split_info.csv"
    write_csv(results_path, results)
    write_csv(split_path, split_infos)
    summary = {
        "metadata": str(args.metadata),
        "waveforms": str(args.waveforms),
        "features_path": str(features_path),
        "results_path": str(results_path),
        "split_info_path": str(split_path),
        "eligible_metadata_rows": int(len(metadata)),
        "feature_rows": int(len(features)),
        "feature_errors": int(len(errors)),
        "early_seconds": args.early_seconds,
        "unit_caveat": "PNWAccelerometers HDF5 stores component_order=ENZ locally, but no waveform unit field was found; target is peak horizontal waveform amplitude, not publication-ready PGA.",
        "results": results,
        "split_info": split_infos,
    }
    (args.out_dir / "pnw_accelerometer_peak_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    )


if __name__ == "__main__":
    main()
