#!/usr/bin/env python3
"""AQ2009GM chunk-level early-window ground-motion baseline."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Any

import h5py
import matplotlib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline


matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


METADATA_FEATURES = [
    "source_magnitude",
    "source_depth_km",
    "path_ep_distance_km",
    "path_hyp_distance_km",
    "station_elevation_m",
    "trace_npts",
    "trace_sampling_rate_hz",
]
TARGETS = {
    "pga": "trace_pga_cmps2",
    "pgv": "trace_pgv_cmps",
}
TRACE_RE = re.compile(r"^(?P<bucket>[^$]+)\$(?P<index>\d+),")


def to_float(value: Any) -> float | None:
    try:
        if value is None or pd.isna(value) or str(value) == "":
            return None
        value_f = float(value)
        return value_f if math.isfinite(value_f) else None
    except Exception:
        return None


def read_data_format(h5: h5py.File) -> dict[str, str]:
    out: dict[str, str] = {}
    for key in ["component_order", "dimension_order", "measurement", "unit"]:
        value = h5[f"data_format/{key}"][()]
        out[key] = value.decode() if isinstance(value, bytes) else str(value)
    return out


def parse_trace_name(trace_name: str) -> tuple[str, int]:
    match = TRACE_RE.match(str(trace_name))
    if not match:
        raise ValueError(f"unsupported trace_name: {trace_name}")
    return match.group("bucket"), int(match.group("index"))


def load_waveform(h5: h5py.File, row: pd.Series) -> np.ndarray:
    bucket, index = parse_trace_name(row["trace_name"])
    npts = int(row["trace_npts"])
    arr = h5[f"data/{bucket}"][index, :, :npts]
    return np.asarray(arr, dtype=np.float32)


def early_window(arr: np.ndarray, row: pd.Series, seconds: float) -> np.ndarray:
    sr = to_float(row.get("trace_sampling_rate_hz"))
    if sr is None or sr <= 0:
        dt = to_float(row.get("trace_dt_s"))
        sr = 1.0 / dt if dt and dt > 0 else 100.0
    p_sample = int(round(to_float(row.get("trace_p_arrival_sample")) or 0))
    start = max(0, p_sample)
    stop = min(arr.shape[1], start + int(round(seconds * sr)))
    if stop <= start:
        return arr[:, : min(arr.shape[1], int(round(seconds * sr)))]
    return arr[:, start:stop]


def waveform_features(arr: np.ndarray, row: pd.Series, seconds: float) -> dict[str, float]:
    win = early_window(arr, row, seconds)
    feats: dict[str, float] = {"early_seconds": float(seconds)}
    if win.size == 0:
        return feats

    abs_win = np.abs(win)
    for idx, comp in enumerate(["z", "n", "e"]):
        x = win[idx]
        ax = abs_win[idx]
        feats[f"{comp}_early_absmax"] = float(np.nanmax(ax))
        feats[f"{comp}_early_rms"] = float(np.sqrt(np.nanmean(x * x)))
        feats[f"{comp}_early_std"] = float(np.nanstd(x))
        feats[f"{comp}_early_p95_abs"] = float(np.nanpercentile(ax, 95))

    horiz = np.sqrt(win[1] ** 2 + win[2] ** 2)
    vec = np.sqrt(np.sum(win**2, axis=0))
    feats["h_early_absmax"] = float(np.nanmax(horiz))
    feats["vec_early_absmax"] = float(np.nanmax(vec))
    feats["vec_early_rms"] = float(np.sqrt(np.nanmean(vec * vec)))
    return feats


def load_metadata(path: Path, chunk: str, row_offset: int = 0) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df["row_id"] = row_offset + np.arange(len(df))
    df["trace_chunk"] = chunk
    df["trace_sampling_rate_hz"] = 1.0 / pd.to_numeric(df["trace_dt_s"], errors="coerce")
    df["station_group"] = (
        df["station_network_code"].fillna("").astype(str) + "." + df["station_code"].fillna("").astype(str)
    )
    mask = pd.Series(True, index=df.index)
    for col in TARGETS.values():
        mask &= pd.to_numeric(df[col], errors="coerce").gt(0)
    mask &= pd.to_numeric(df["trace_p_arrival_sample"], errors="coerce").notna()
    mask &= pd.to_numeric(df["trace_npts"], errors="coerce").gt(0)
    mask &= df["trace_name"].notna()
    return df[mask].copy()


def split_by_group(
    df: pd.DataFrame,
    dataset: str,
    holdout: str,
    train_size: int,
    test_size: int,
    station_test_groups: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    work = df.copy()
    group_col = "source_id" if holdout == "event" else "station_group"
    work["_group"] = work[group_col].fillna("").astype(str)
    work = work[work["_group"].ne("") & work["_group"].ne(".")].copy()

    rng = np.random.default_rng(seed)
    group_sizes = work["_group"].value_counts()
    groups = np.array(group_sizes.index.tolist(), dtype=object)
    rng.shuffle(groups)

    test_groups: list[str] = []
    if holdout == "station":
        test_groups = [str(g) for g in groups[: min(station_test_groups, len(groups))]]
    else:
        test_rows = 0
        for group in groups:
            test_groups.append(str(group))
            test_rows += int(group_sizes.loc[group])
            if test_rows >= test_size:
                break

    test_group_set = set(test_groups)
    train = work[~work["_group"].isin(test_group_set)]
    test = work[work["_group"].isin(test_group_set)]

    if len(train) > train_size:
        train = train.sample(train_size, random_state=seed + 11)
    if len(test) > test_size:
        test = test.sample(test_size, random_state=seed + 17)

    overlap = set(train["_group"]).intersection(set(test["_group"]))
    if overlap:
        raise RuntimeError(f"held-{holdout} overlap: {sorted(overlap)[:3]}")

    info = {
        "dataset": dataset,
        "holdout": holdout,
        "group_column": group_col,
        "eligible_rows": int(len(work)),
        "eligible_groups": int(work["_group"].nunique()),
        "train_rows_selected": int(len(train)),
        "test_rows_selected": int(len(test)),
        "train_groups": int(train["_group"].nunique()),
        "test_groups": int(test["_group"].nunique()),
        "group_overlap": int(len(overlap)),
        "station_test_groups_requested": int(station_test_groups if holdout == "station" else 0),
    }
    return train["row_id"].to_numpy(), test["row_id"].to_numpy(), info


def build_features(
    metadata: pd.DataFrame,
    cache_dir: Path,
    windows: list[float],
) -> tuple[pd.DataFrame, dict[str, str], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    data_format: dict[str, str] = {}
    for chunk, chunk_metadata in metadata.groupby("trace_chunk", sort=True):
        with h5py.File(cache_dir / f"waveforms{chunk}.hdf5", "r") as h5:
            chunk_format = read_data_format(h5)
            if not data_format:
                data_format = chunk_format
            elif chunk_format != data_format:
                errors.append({"trace_chunk": chunk, "error": f"data_format mismatch: {chunk_format}"})
            for _, row in chunk_metadata.iterrows():
                try:
                    arr = load_waveform(h5, row)
                except Exception as exc:
                    errors.append({"row_id": int(row["row_id"]), "trace_name": row.get("trace_name", ""), "trace_chunk": chunk, "error": repr(exc)})
                    continue

                base = {
                    "row_id": int(row["row_id"]),
                    "trace_chunk": row.get("trace_chunk", ""),
                    "trace_name": row.get("trace_name", ""),
                    "source_id": row.get("source_id", ""),
                    "station_group": row.get("station_group", ""),
                    "station_network_code": row.get("station_network_code", ""),
                    "station_code": row.get("station_code", ""),
                    "source_magnitude": to_float(row.get("source_magnitude")),
                    "source_depth_km": to_float(row.get("source_depth_km")),
                    "path_ep_distance_km": to_float(row.get("path_ep_distance_km")),
                    "path_hyp_distance_km": to_float(row.get("path_hyp_distance_km")),
                    "station_elevation_m": to_float(row.get("station_elevation_m")),
                    "trace_npts": to_float(row.get("trace_npts")),
                    "trace_sampling_rate_hz": to_float(row.get("trace_sampling_rate_hz")),
                }
                for target, col in TARGETS.items():
                    value = to_float(row.get(col))
                    base[f"target_{target}"] = value
                    base[f"target_log10_{target}"] = math.log10(value) if value and value > 0 else np.nan

                for seconds in windows:
                    rec = dict(base)
                    rec.update(waveform_features(arr, row, seconds))
                    records.append(rec)
    return pd.DataFrame(records), data_format, errors


def waveform_feature_cols(df: pd.DataFrame) -> list[str]:
    return [
        col
        for col in df.columns
        if col.endswith("_early_absmax")
        or col.endswith("_early_rms")
        or col.endswith("_early_std")
        or col.endswith("_early_p95_abs")
    ]


def train_eval(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    features: list[str],
    feature_set: str,
    holdout: str,
    target: str,
    early_seconds: float,
    split_info: dict[str, Any],
    dataset: str,
) -> dict[str, Any]:
    target_col = f"target_log10_{target}"
    train = train_df.dropna(subset=[target_col]).copy()
    test = test_df.dropna(subset=[target_col]).copy()
    if len(train) == 0 or len(test) == 0:
        return {
            "dataset": dataset,
            "holdout": holdout,
            "target": target,
            "early_seconds": early_seconds,
            "feature_set": feature_set,
            "train_rows": int(len(train)),
            "test_rows": int(len(test)),
            "skipped": True,
        }

    if feature_set == "median":
        model = DummyRegressor(strategy="median")
    else:
        model = HistGradientBoostingRegressor(
            max_iter=200,
            learning_rate=0.05,
            max_leaf_nodes=31,
            random_state=17,
            l2_regularization=0.01,
        )
    pipe = make_pipeline(SimpleImputer(strategy="median"), model)
    pipe.fit(train[features], train[target_col].astype(float))
    pred = pipe.predict(test[features])
    y_test = test[target_col].astype(float).to_numpy()
    abs_err = np.abs(y_test - pred)
    return {
        "dataset": dataset,
        "holdout": holdout,
        "target": target,
        "early_seconds": early_seconds,
        "feature_set": feature_set,
        "model": "median" if feature_set == "median" else "hgb",
        "features": json.dumps(features),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_groups": split_info["train_groups"],
        "test_groups": split_info["test_groups"],
        "group_overlap": split_info["group_overlap"],
        "mae_log10_target": float(mean_absolute_error(y_test, pred)),
        "rmse_log10_target": float(mean_squared_error(y_test, pred) ** 0.5),
        "q95_abs_error_log10_target": float(np.nanpercentile(abs_err, 95)),
        "r2_log10_target": float(r2_score(y_test, pred)),
        "skipped": False,
    }


def compare_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    df = pd.DataFrame(results)
    rows: list[dict[str, Any]] = []
    keys = ["dataset", "holdout", "target", "early_seconds"]
    for key, sub in df.groupby(keys, dropna=False):
        by_set = sub.set_index("feature_set")
        if "metadata_only" not in by_set.index or "metadata_plus_early_velocity" not in by_set.index:
            continue
        meta = by_set.loc["metadata_only"]
        combined = by_set.loc["metadata_plus_early_velocity"]
        meta_mae = float(meta["mae_log10_target"])
        comb_mae = float(combined["mae_log10_target"])
        meta_q95 = float(meta["q95_abs_error_log10_target"])
        comb_q95 = float(combined["q95_abs_error_log10_target"])
        rows.append(
            {
                "dataset": key[0],
                "holdout": key[1],
                "target": key[2],
                "early_seconds": key[3],
                "metadata_mae_log10_target": meta_mae,
                "combined_mae_log10_target": comb_mae,
                "mae_reduction_pct": 100.0 * (meta_mae - comb_mae) / meta_mae if meta_mae else np.nan,
                "metadata_q95_abs_error": meta_q95,
                "combined_q95_abs_error": comb_q95,
                "q95_reduction_pct": 100.0 * (meta_q95 - comb_q95) / meta_q95 if meta_q95 else np.nan,
                "metadata_r2": float(meta["r2_log10_target"]),
                "combined_r2": float(combined["r2_log10_target"]),
                "train_rows": int(combined["train_rows"]),
                "test_rows": int(combined["test_rows"]),
                "train_groups": int(combined["train_groups"]),
                "test_groups": int(combined["test_groups"]),
                "group_overlap": int(combined["group_overlap"]),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(
    path: Path,
    dataset: str,
    chunks: list[str],
    metadata_all_rows: int,
    metadata: pd.DataFrame,
    data_format: dict[str, str],
    split_infos: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    figure_path: Path,
    out_dir: Path,
    prefix: str,
) -> None:
    comp = pd.DataFrame(comparisons)
    lines = [
        f"# AQ2009GM {','.join(chunks)} 早窗强震动补验",
        "",
        "## 数据范围",
        "",
        f"- SeisBench AQ2009GM chunks：{', '.join(chunks)}",
        f"- metadata 总行数：{metadata_all_rows}",
        f"- 有效 PGA/PGV 记录：{len(metadata)}",
        f"- 事件数：{metadata['source_id'].nunique()}",
        f"- 台站数：{metadata['station_group'].nunique()}",
        f"- HDF5 波形格式：measurement={data_format.get('measurement')}, unit={data_format.get('unit')}, component_order={data_format.get('component_order')}",
        "- 目标变量：`trace_pga_cmps2` 和 `trace_pgv_cmps`，均来自 AQ2009GM metadata。",
        "",
        f"这个检查覆盖 {len(chunks)} 个 AQ2009GM chunk。它是 2009 L'Aquila 余震数据子集，震级和幅值范围小于 K-NET 强震记录。这里适合作为独立 SeisBench 地震动补验，不应写成完整 AQ2009GM 结论。",
        "",
        "## 分组切分",
        "",
        "| Holdout | Eligible rows | Eligible groups | Train rows | Test rows | Train groups | Test groups | Overlap |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for info in split_infos:
        lines.append(
            f"| {info['holdout']} | {info['eligible_rows']} | {info['eligible_groups']} | "
            f"{info['train_rows_selected']} | {info['test_rows_selected']} | "
            f"{info['train_groups']} | {info['test_groups']} | {info['group_overlap']} |"
        )

    lines.extend(
        [
            "",
            "## Metadata + early velocity 相对 metadata-only",
            "",
            "| Holdout | Target | Window | Metadata MAE | Combined MAE | MAE reduction | Metadata R2 | Combined R2 |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    if not comp.empty:
        comp = comp.sort_values(["holdout", "target", "early_seconds"])
        for _, row in comp.iterrows():
            lines.append(
                f"| {row['holdout']} | {row['target'].upper()} | {row['early_seconds']:.0f}s | "
                f"{row['metadata_mae_log10_target']:.3f} | {row['combined_mae_log10_target']:.3f} | "
                f"{row['mae_reduction_pct']:.1f}% | {row['metadata_r2']:.3f} | {row['combined_r2']:.3f} |"
            )

    lines.extend(
        [
            "",
            "## 解释边界",
            "",
            f"- 支持的说法：在 AQ2009GM {','.join(chunks)} 子集内，P 后早窗速度波形为 PGA/PGV 提供了 metadata 之外的信息。",
            "- 暂不支持的说法：这不是完整 AQ2009GM 验证，也不是跨区域强震动完整外部验证。",
            "- 写入主文时应作为 supplementary independent SeisBench check；如果要把它升为主证据，需要下载更多 chunk，并固定事件/台站分组方案。",
            "",
            "## 文件",
            "",
            f"- Metrics CSV: `{out_dir / f'{prefix}_metrics.csv'}`",
            f"- Comparison CSV: `{out_dir / f'{prefix}_comparison.csv'}`",
            f"- Feature table: `{out_dir / f'{prefix}_features.csv.gz'}`",
            f"- Split info: `{out_dir / f'{prefix}_split_info.csv'}`",
            f"- Figure: `{figure_path}`",
        ]
    )
    if errors:
        lines.append(f"- Waveform read errors: {len(errors)}")
    path.write_text("\n".join(lines) + "\n")


def plot_comparison(comparisons: list[dict[str, Any]], out: Path, title: str) -> None:
    df = pd.DataFrame(comparisons)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    colors = {"event": "#2f6f9f", "station": "#b25d2a"}
    markers = {"pga": "o", "pgv": "s"}
    for ax, target in zip(axes, ["pga", "pgv"], strict=True):
        sub_target = df[df["target"] == target].copy()
        for holdout in ["event", "station"]:
            sub = sub_target[sub_target["holdout"] == holdout].sort_values("early_seconds")
            ax.plot(
                sub["early_seconds"],
                sub["mae_reduction_pct"],
                marker=markers[target],
                linewidth=2.2,
                color=colors[holdout],
                label=f"held-{holdout}",
            )
        ax.axhline(0, color="#666666", linewidth=0.8)
        ax.set_title(target.upper())
        ax.set_xlabel("Post-P window (s)")
        ax.set_xticks([1, 3, 10])
        ax.grid(True, axis="y", alpha=0.25)
    axes[0].set_ylabel("MAE reduction vs metadata-only (%)")
    axes[1].legend(frameon=False, loc="lower right")
    fig.suptitle(title, y=1.02)
    fig.tight_layout()
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", type=Path, default=Path.home() / ".seisbench/datasets/aq2009gm")
    parser.add_argument("--chunk", default="096")
    parser.add_argument("--chunks", nargs="+")
    parser.add_argument("--out-dir", type=Path, default=Path("work/aq2009gm_chunk096_baseline"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/aq2009gm_chunk096_baseline_summary.md"))
    parser.add_argument("--figure", type=Path, default=Path("outputs/figures/ground_motion_audit/aq2009gm_chunk096_panel.png"))
    parser.add_argument("--windows", nargs="+", type=float, default=[1.0, 3.0, 10.0])
    parser.add_argument("--train-size", type=int, default=2500)
    parser.add_argument("--test-size", type=int, default=700)
    parser.add_argument("--station-test-groups", type=int, default=5)
    parser.add_argument("--seed", type=int, default=43)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    chunks = args.chunks or [args.chunk]
    tag = f"chunk{chunks[0]}" if len(chunks) == 1 else f"chunks{chunks[0]}-{chunks[-1]}"
    dataset = f"aq2009gm_{tag}"
    prefix = f"aq2009gm_{tag}"

    metadata_frames = []
    metadata_all_rows = 0
    row_offset = 0
    for chunk in chunks:
        metadata_path = args.cache_dir / f"metadata{chunk}.csv"
        metadata_all_rows += len(pd.read_csv(metadata_path, usecols=["trace_name"], low_memory=False))
        frame = load_metadata(metadata_path, chunk, row_offset=row_offset)
        metadata_frames.append(frame)
        row_offset += len(pd.read_csv(metadata_path, usecols=["trace_name"], low_memory=False))
    metadata = pd.concat(metadata_frames, ignore_index=True)
    features, data_format, errors = build_features(metadata, args.cache_dir, args.windows)
    features_path = args.out_dir / f"{prefix}_features.csv.gz"
    features.to_csv(features_path, index=False)

    split_infos: list[dict[str, Any]] = []
    split_masks: dict[str, tuple[np.ndarray, np.ndarray, dict[str, Any]]] = {}
    for holdout in ["event", "station"]:
        train_ids, test_ids, info = split_by_group(
            metadata,
            dataset=dataset,
            holdout=holdout,
            train_size=args.train_size,
            test_size=args.test_size,
            station_test_groups=args.station_test_groups,
            seed=args.seed + (101 if holdout == "station" else 0),
        )
        split_infos.append(info)
        split_masks[holdout] = (train_ids, test_ids, info)

    all_results: list[dict[str, Any]] = []
    for holdout, (train_ids, test_ids, info) in split_masks.items():
        for seconds in args.windows:
            sub = features[features["early_seconds"].eq(float(seconds))]
            train_df = sub[sub["row_id"].isin(train_ids)].copy()
            test_df = sub[sub["row_id"].isin(test_ids)].copy()
            metadata_cols = [col for col in METADATA_FEATURES if col in sub.columns]
            wave_cols = waveform_feature_cols(sub)
            feature_sets = {
                "median": metadata_cols[:1],
                "metadata_only": metadata_cols,
                "early_velocity_only": wave_cols,
                "metadata_plus_early_velocity": metadata_cols + wave_cols,
            }
            for target in TARGETS:
                for feature_set, cols in feature_sets.items():
                    all_results.append(train_eval(train_df, test_df, cols, feature_set, holdout, target, seconds, info, dataset))

    comparisons = compare_results(all_results)
    write_csv(args.out_dir / f"{prefix}_metrics.csv", all_results)
    write_csv(args.out_dir / f"{prefix}_comparison.csv", comparisons)
    write_csv(args.out_dir / f"{prefix}_split_info.csv", split_infos)
    write_csv(args.out_dir / f"{prefix}_waveform_errors.csv", errors)
    plot_comparison(comparisons, args.figure, f"AQ2009GM {','.join(chunks)} early velocity information")

    report = {
        "chunks": chunks,
        "metadata_paths": [str(args.cache_dir / f"metadata{chunk}.csv") for chunk in chunks],
        "waveforms_paths": [str(args.cache_dir / f"waveforms{chunk}.hdf5") for chunk in chunks],
        "metadata_all_rows": metadata_all_rows,
        "valid_rows": int(len(metadata)),
        "valid_events": int(metadata["source_id"].nunique()),
        "valid_stations": int(metadata["station_group"].nunique()),
        "data_format": data_format,
        "windows": args.windows,
        "targets": TARGETS,
        "split_info": split_infos,
        "metrics_path": str(args.out_dir / f"{prefix}_metrics.csv"),
        "comparison_path": str(args.out_dir / f"{prefix}_comparison.csv"),
        "features_path": str(features_path),
        "summary_path": str(args.summary),
        "figure_path": str(args.figure),
        "errors": errors,
    }
    (args.out_dir / f"{prefix}_summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    write_summary(args.summary, dataset, chunks, metadata_all_rows, metadata, data_format, split_infos, comparisons, errors, args.figure, args.out_dir, prefix)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
