#!/usr/bin/env python3
"""Run a small PhaseNet/EQTransformer phase-picking pilot on the unified manifest."""

from __future__ import annotations

import argparse
import csv
import json
import math
import warnings
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd
import seisbench.models as sbm
from obspy import Stream, Trace, UTCDateTime


CHANNELS = ["Z", "N", "E"]
MODEL_REGISTRY = {
    "phasenet_stead": (sbm.PhaseNet, "stead"),
    "eqtransformer_stead": (sbm.EQTransformer, "stead"),
    "phasenet_instance": (sbm.PhaseNet, "instance"),
    "eqtransformer_instance": (sbm.EQTransformer, "instance"),
}


def is_blank(value: Any) -> bool:
    try:
        return value is None or pd.isna(value) or str(value) == ""
    except Exception:
        return value is None or str(value) == ""


def to_float(value: Any) -> float | None:
    if is_blank(value):
        return None
    try:
        value_f = float(value)
        if math.isfinite(value_f):
            return value_f
    except Exception:
        return None
    return None


def to_int(value: Any, default: int = 0) -> int:
    value_f = to_float(value)
    return default if value_f is None else int(round(value_f))


def sampling_rate(row: dict[str, Any]) -> float:
    sr = to_float(row.get("sampling_rate_hz"))
    if sr and sr > 0:
        return sr
    if row.get("dataset") in {"stead", "iquique", "knet"}:
        return 100.0
    return 100.0


def select_rows(
    manifest: Path,
    datasets: list[str],
    split: str,
    per_dataset: int,
    min_samples: int,
    max_samples: int,
    seed: int,
) -> list[dict[str, str]]:
    rng = np.random.default_rng(seed)
    pools: dict[str, list[dict[str, str]]] = {dataset: [] for dataset in datasets}
    usecols = None
    for chunk in pd.read_csv(manifest, chunksize=200_000, dtype=str, usecols=usecols):
        chunk = chunk[
            (chunk["dataset"].isin(datasets))
            & (chunk["split"] == split)
            & (chunk["has_phase_task"] == "1")
        ]
        n_samples = pd.to_numeric(chunk["n_samples"], errors="coerce")
        if min_samples:
            chunk = chunk[n_samples >= min_samples]
            n_samples = pd.to_numeric(chunk["n_samples"], errors="coerce")
        if max_samples:
            chunk = chunk[n_samples <= max_samples]
        for dataset in datasets:
            sub = chunk[chunk["dataset"] == dataset]
            if len(sub):
                pools[dataset].extend(sub.to_dict("records"))

    selected: list[dict[str, str]] = []
    for dataset in datasets:
        rows = pools[dataset]
        if not rows:
            continue
        idx = np.arange(len(rows))
        rng.shuffle(idx)
        for i in idx[:per_dataset]:
            selected.append(rows[int(i)])
    return selected


def load_waveform(row: dict[str, Any]) -> np.ndarray:
    start = to_int(row.get("sample_start"), 0)
    stop = to_int(row.get("sample_stop"), to_int(row.get("n_samples"), 0))
    with h5py.File(row["waveform_store"], "r") as h5:
        if row["dataset"] == "knet":
            arr = h5[row["hdf5_key"]][:, start:stop]
        else:
            arr = h5[row["hdf5_key"]][to_int(row["hdf5_index"]), :, start:stop]
    arr = np.asarray(arr, dtype=np.float32)
    if arr.shape[0] != 3:
        raise ValueError(f"Expected 3 components, got {arr.shape} for {row['global_id']}")
    return arr


def stream_from_row(row: dict[str, Any], arr: np.ndarray) -> Stream:
    sr = sampling_rate(row)
    stream = Stream()
    for data, component in zip(arr, CHANNELS):
        trace = Trace(data=np.asarray(data, dtype=np.float32))
        trace.stats.network = row.get("station_network_code") or "XX"
        trace.stats.station = row.get("station_code") or "STA"
        trace.stats.channel = f"HH{component}"
        trace.stats.sampling_rate = sr
        trace.stats.starttime = UTCDateTime(0)
        stream.append(trace)
    return stream


def true_phase_sec(row: dict[str, Any], phase: str) -> float | None:
    sec = to_float(row.get(f"{phase.lower()}_pick_sec"))
    if sec is not None:
        return sec
    sample = to_float(row.get(f"{phase.lower()}_pick_sample"))
    if sample is None:
        return None
    return sample / sampling_rate(row)


def best_pick(picks: Any, phase: str, true_sec: float | None) -> tuple[float | None, float | None, int]:
    phase_picks = [pick for pick in picks if getattr(pick, "phase", None) == phase]
    if not phase_picks:
        return None, None, 0
    if true_sec is None:
        pick = phase_picks[0]
    else:
        pick = min(phase_picks, key=lambda item: abs(float(item.peak_time.timestamp) - true_sec))
    return float(pick.peak_time.timestamp), float(getattr(pick, "peak_value", np.nan)), len(phase_picks)


def evaluate_one(model_name: str, model: Any, row: dict[str, Any], stream: Stream) -> dict[str, Any]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if model_name.startswith("eqtransformer"):
            out = model.classify(
                stream,
                P_threshold=0.1,
                S_threshold=0.1,
                detection_threshold=0.1,
            )
        else:
            out = model.classify(stream, P_threshold=0.1, S_threshold=0.1)

    result: dict[str, Any] = {
        "model": model_name,
        "global_id": row["global_id"],
        "dataset": row["dataset"],
        "record_id": row["record_id"],
        "split": row["split"],
        "n_samples": row["n_samples"],
        "sampling_rate_hz": sampling_rate(row),
        "source_magnitude": row.get("source_magnitude", ""),
        "source_distance_km": row.get("source_distance_km", ""),
        "picks_total": len(out.picks),
    }

    for phase in ["P", "S"]:
        true_sec = true_phase_sec(row, phase)
        pred_sec, confidence, phase_count = best_pick(out.picks, phase, true_sec)
        error = None if true_sec is None or pred_sec is None else pred_sec - true_sec
        result[f"{phase.lower()}_true_sec"] = "" if true_sec is None else f"{true_sec:.6f}"
        result[f"{phase.lower()}_pred_sec"] = "" if pred_sec is None else f"{pred_sec:.6f}"
        result[f"{phase.lower()}_error_sec"] = "" if error is None else f"{error:.6f}"
        result[f"{phase.lower()}_abs_error_sec"] = "" if error is None else f"{abs(error):.6f}"
        result[f"{phase.lower()}_confidence"] = "" if confidence is None or not math.isfinite(confidence) else f"{confidence:.6f}"
        result[f"{phase.lower()}_pick_count"] = phase_count
    return result


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["model"], row["dataset"])].append(row)

    for (model, dataset), items in groups.items():
        key = f"{model}|{dataset}"
        item_summary: dict[str, Any] = {"records": len(items)}
        for phase in ["p", "s"]:
            errors = [to_float(item.get(f"{phase}_abs_error_sec")) for item in items]
            errors = [err for err in errors if err is not None]
            item_summary[f"{phase}_matched"] = len(errors)
            item_summary[f"{phase}_missing"] = len(items) - len(errors)
            if errors:
                arr = np.asarray(errors, dtype=float)
                item_summary[f"{phase}_mae_sec"] = float(np.mean(arr))
                item_summary[f"{phase}_median_abs_error_sec"] = float(np.median(arr))
                item_summary[f"{phase}_within_0p5s"] = int(np.sum(arr <= 0.5))
                item_summary[f"{phase}_within_1s"] = int(np.sum(arr <= 1.0))
                item_summary[f"{phase}_large_error_gt_2s"] = int(np.sum(arr > 2.0))
        summary[key] = item_summary
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("work/unified_manifest/unified_manifest.csv.gz"))
    parser.add_argument("--out-dir", type=Path, default=Path("work/baseline_pilot"))
    parser.add_argument("--datasets", nargs="+", default=["stead", "instancegm", "iquique", "knet"])
    parser.add_argument("--split", default="test")
    parser.add_argument("--per-dataset", type=int, default=8)
    parser.add_argument("--min-samples", type=int, default=6_000)
    parser.add_argument("--max-samples", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--models", nargs="+", default=["phasenet_stead", "eqtransformer_stead"])
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows = select_rows(
        args.manifest,
        args.datasets,
        args.split,
        args.per_dataset,
        args.min_samples,
        args.max_samples,
        args.seed,
    )
    print(f"selected_rows={len(rows)}", flush=True)

    models = {}
    for model_name in args.models:
        cls, weight_name = MODEL_REGISTRY[model_name]
        print(f"loading {model_name}", flush=True)
        model = cls.from_pretrained(weight_name)
        model.eval()
        models[model_name] = model

    prediction_rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for i, row in enumerate(rows, 1):
        try:
            arr = load_waveform(row)
            if not np.isfinite(arr).all():
                raise ValueError("non-finite waveform values")
            stream = stream_from_row(row, arr)
            for model_name, model in models.items():
                prediction_rows.append(evaluate_one(model_name, model, row, stream))
        except Exception as exc:
            failures.append({"global_id": row.get("global_id", ""), "error": repr(exc)})
        if i % 5 == 0:
            print(f"processed_records={i}/{len(rows)}", flush=True)

    predictions_path = args.out_dir / "phase_baseline_pilot_predictions.csv"
    with predictions_path.open("w", newline="") as fh:
        if prediction_rows:
            fieldnames = list(prediction_rows[0].keys())
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(prediction_rows)

    report = {
        "manifest": str(args.manifest),
        "split": args.split,
        "datasets": args.datasets,
        "per_dataset": args.per_dataset,
        "min_samples": args.min_samples,
        "max_samples": args.max_samples,
        "models": args.models,
        "records_selected": len(rows),
        "predictions": len(prediction_rows),
        "failures": failures,
        "summary": summarize(prediction_rows),
        "outputs": {"predictions_csv": str(predictions_path)},
        "note": "Pilot only: small deterministic sample for pipeline and label-audit sanity checks, not manuscript evidence.",
    }
    report_path = args.out_dir / "phase_baseline_pilot_summary.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
