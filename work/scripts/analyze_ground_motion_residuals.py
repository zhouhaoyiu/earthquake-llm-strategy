#!/usr/bin/env python3
"""Residual analysis for ground-motion HGB baselines."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline


METADATA_FEATURES = [
    "source_magnitude",
    "source_depth_km",
    "source_distance_km",
    "station_elevation_m",
    "station_vs30_mps",
    "year",
    "n_samples",
]

TARGETS = ["pga", "pgv", "sa03", "sa10", "sa30"]

BIN_VARIABLES = [
    "source_magnitude",
    "source_depth_km",
    "source_distance_km",
    "station_elevation_m",
    "station_vs30_mps",
    "year",
    "vec_early_absmax",
    "vec_early_rms",
]


def numeric_cols(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        if col in out:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def waveform_feature_cols(df: pd.DataFrame) -> list[str]:
    return [
        col
        for col in df.columns
        if col.endswith("_early_absmax")
        or col.endswith("_early_rms")
        or col.endswith("_early_std")
        or col.endswith("_early_p95_abs")
    ]


def make_model() -> Any:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        HistGradientBoostingRegressor(
            max_iter=200,
            learning_rate=0.05,
            max_leaf_nodes=31,
            random_state=17,
            l2_regularization=0.01,
        ),
    )


def regression_metrics(y_true: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {
        "mae_log10_target": float(mean_absolute_error(y_true, pred)),
        "rmse_log10_target": float(mean_squared_error(y_true, pred) ** 0.5),
        "r2_log10_target": float(r2_score(y_true, pred)),
    }


def train_predict(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    dataset: str,
    target: str,
    feature_set: str,
    features: list[str],
) -> tuple[dict[str, Any] | None, pd.DataFrame | None]:
    target_col = f"target_log10_{target}"
    if target_col not in train_df or target_col not in test_df:
        return None, None
    train = train_df.dropna(subset=[target_col]).copy()
    test = test_df.dropna(subset=[target_col]).copy()
    if len(train) == 0 or len(test) == 0:
        return None, None

    model = make_model()
    x_train = train[features]
    y_train = train[target_col].astype(float)
    x_test = test[features]
    y_test = test[target_col].astype(float)
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    residual = pred - y_test.to_numpy()
    abs_residual = np.abs(residual)

    keep_cols = [
        "global_id",
        "dataset",
        "split",
        "source_magnitude",
        "source_depth_km",
        "source_distance_km",
        "station_elevation_m",
        "station_vs30_mps",
        "year",
        "n_samples",
        "vec_early_absmax",
        "vec_early_rms",
        "h_early_absmax",
    ]
    keep_cols = [col for col in keep_cols if col in test.columns]
    pred_df = test[keep_cols].copy()
    pred_df["target"] = target
    pred_df["feature_set"] = feature_set
    pred_df["actual_log10_target"] = y_test.to_numpy()
    pred_df["pred_log10_target"] = pred
    pred_df["residual_log10_target"] = residual
    pred_df["abs_residual_log10_target"] = abs_residual
    pred_df["under_over"] = np.where(residual >= 0, "overpredict", "underpredict")

    metrics = {
        "dataset": dataset,
        "target": target,
        "feature_set": feature_set,
        "features": features,
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        **regression_metrics(y_test.to_numpy(), pred),
        "median_signed_residual": float(np.median(residual)),
        "mean_signed_residual": float(np.mean(residual)),
        "q90_abs_residual": float(np.quantile(abs_residual, 0.90)),
        "q95_abs_residual": float(np.quantile(abs_residual, 0.95)),
        "overpredict_fraction": float(np.mean(residual >= 0)),
    }
    return metrics, pred_df


def corr_rows(pred_df: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for var in BIN_VARIABLES:
        if var not in pred_df.columns:
            continue
        x = pd.to_numeric(pred_df[var], errors="coerce")
        y = pred_df["residual_log10_target"]
        mask = x.notna() & y.notna()
        if mask.sum() < 20:
            continue
        rows.append(
            {
                "dataset": pred_df["dataset"].iloc[0],
                "target": pred_df["target"].iloc[0],
                "feature_set": pred_df["feature_set"].iloc[0],
                "variable": var,
                "n": int(mask.sum()),
                "pearson_residual": float(np.corrcoef(x[mask], y[mask])[0, 1]),
                "pearson_abs_residual": float(np.corrcoef(x[mask], pred_df.loc[mask, "abs_residual_log10_target"])[0, 1]),
            }
        )
    return rows


def bin_summary(pred_df: pd.DataFrame, bins: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for var in BIN_VARIABLES:
        if var not in pred_df.columns:
            continue
        work = pred_df[[var, "residual_log10_target", "abs_residual_log10_target"]].copy()
        work[var] = pd.to_numeric(work[var], errors="coerce")
        work = work.dropna()
        if len(work) < max(30, bins * 5) or work[var].nunique() < 3:
            continue
        try:
            work["bin"] = pd.qcut(work[var], q=bins, duplicates="drop")
        except ValueError:
            continue
        for interval, sub in work.groupby("bin", observed=True):
            rows.append(
                {
                    "dataset": pred_df["dataset"].iloc[0],
                    "target": pred_df["target"].iloc[0],
                    "feature_set": pred_df["feature_set"].iloc[0],
                    "variable": var,
                    "bin": str(interval),
                    "n": int(len(sub)),
                    "x_min": float(sub[var].min()),
                    "x_max": float(sub[var].max()),
                    "median_signed_residual": float(sub["residual_log10_target"].median()),
                    "mean_signed_residual": float(sub["residual_log10_target"].mean()),
                    "mae_residual": float(sub["abs_residual_log10_target"].mean()),
                    "q90_abs_residual": float(sub["abs_residual_log10_target"].quantile(0.90)),
                    "overpredict_fraction": float((sub["residual_log10_target"] >= 0).mean()),
                }
            )
    return pd.DataFrame(rows)


def plot_residuals(pred_df: pd.DataFrame, out_dir: Path, max_points: int) -> list[str]:
    paths: list[str] = []
    dataset = pred_df["dataset"].iloc[0]
    target = pred_df["target"].iloc[0]
    feature_set = pred_df["feature_set"].iloc[0]
    for var in ["source_magnitude", "source_distance_km", "source_depth_km", "vec_early_absmax"]:
        if var not in pred_df.columns:
            continue
        x = pd.to_numeric(pred_df[var], errors="coerce")
        y = pred_df["residual_log10_target"]
        mask = x.notna() & y.notna()
        if mask.sum() < 20:
            continue
        sub = pred_df.loc[mask, [var, "residual_log10_target", "abs_residual_log10_target"]].copy()
        if len(sub) > max_points:
            sub = sub.sample(max_points, random_state=17)
        fig, ax = plt.subplots(figsize=(6.0, 4.0), dpi=160)
        ax.scatter(sub[var], sub["residual_log10_target"], s=10, alpha=0.45, linewidths=0)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xlabel(var)
        ax.set_ylabel("predicted - observed log10 target")
        ax.set_title(f"{dataset} {target} {feature_set}")
        fig.tight_layout()
        path = out_dir / f"{dataset}_{target}_{feature_set}_{var}.png"
        fig.savefig(path)
        plt.close(fig)
        paths.append(str(path))
    return paths


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature-dir", type=Path, default=Path("work/ground_motion_baseline_multi_10s"))
    parser.add_argument("--out-dir", type=Path, default=Path("work/ground_motion_residuals_10s"))
    parser.add_argument("--datasets", nargs="+", default=["instancegm", "knet"])
    parser.add_argument("--targets", nargs="+", default=TARGETS)
    parser.add_argument("--feature-sets", nargs="+", default=["metadata_only", "metadata_plus_early_waveform"])
    parser.add_argument("--bins", type=int, default=5)
    parser.add_argument("--plot-max-points", type=int, default=1200)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    plot_dir = args.out_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    all_metrics: list[dict[str, Any]] = []
    all_predictions: list[pd.DataFrame] = []
    all_bins: list[pd.DataFrame] = []
    all_corrs: list[dict[str, Any]] = []
    all_worst: list[pd.DataFrame] = []
    plot_paths: list[str] = []

    for dataset in args.datasets:
        train_path = args.feature_dir / f"{dataset}_train_features.csv"
        test_path = args.feature_dir / f"{dataset}_test_features.csv"
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)
        numeric_candidates = METADATA_FEATURES + waveform_feature_cols(train_df) + [f"target_log10_{target}" for target in args.targets]
        train_df = numeric_cols(train_df, numeric_candidates)
        test_df = numeric_cols(test_df, numeric_candidates)
        waveform_cols = waveform_feature_cols(train_df)
        feature_map = {
            "metadata_only": [col for col in METADATA_FEATURES if col in train_df.columns],
            "early_waveform_only": waveform_cols,
            "metadata_plus_early_waveform": [col for col in METADATA_FEATURES if col in train_df.columns] + waveform_cols,
        }
        for target in args.targets:
            for feature_set in args.feature_sets:
                features = feature_map.get(feature_set, [])
                if not features:
                    continue
                metrics, pred_df = train_predict(train_df, test_df, dataset, target, feature_set, features)
                if metrics is None or pred_df is None:
                    continue
                all_metrics.append(metrics)
                all_predictions.append(pred_df)
                all_corrs.extend(corr_rows(pred_df))
                bins_df = bin_summary(pred_df, args.bins)
                if len(bins_df):
                    all_bins.append(bins_df)
                all_worst.append(
                    pred_df.sort_values("abs_residual_log10_target", ascending=False)
                    .head(25)
                    .assign(rank=lambda df: np.arange(1, len(df) + 1))
                )
                plot_paths.extend(plot_residuals(pred_df, plot_dir, args.plot_max_points))
                print(
                    dataset,
                    target,
                    feature_set,
                    metrics["mae_log10_target"],
                    metrics["r2_log10_target"],
                    flush=True,
                )

    predictions_df = pd.concat(all_predictions, ignore_index=True) if all_predictions else pd.DataFrame()
    bins_df = pd.concat(all_bins, ignore_index=True) if all_bins else pd.DataFrame()
    worst_df = pd.concat(all_worst, ignore_index=True) if all_worst else pd.DataFrame()
    corrs_df = pd.DataFrame(all_corrs)

    metrics_path = args.out_dir / "ground_motion_residual_metrics.csv"
    predictions_path = args.out_dir / "ground_motion_residual_predictions.csv"
    bins_path = args.out_dir / "ground_motion_residual_bins.csv"
    corrs_path = args.out_dir / "ground_motion_residual_correlations.csv"
    worst_path = args.out_dir / "ground_motion_residual_worst_cases.csv"
    write_csv(metrics_path, all_metrics)
    predictions_df.to_csv(predictions_path, index=False)
    bins_df.to_csv(bins_path, index=False)
    corrs_df.to_csv(corrs_path, index=False)
    worst_df.to_csv(worst_path, index=False)

    report = {
        "feature_dir": str(args.feature_dir),
        "datasets": args.datasets,
        "targets": args.targets,
        "feature_sets": args.feature_sets,
        "metrics_path": str(metrics_path),
        "predictions_path": str(predictions_path),
        "bins_path": str(bins_path),
        "correlations_path": str(corrs_path),
        "worst_cases_path": str(worst_path),
        "plot_paths": plot_paths,
        "metrics": all_metrics,
        "note": "Residual is pred_log10_target - actual_log10_target; positive values are overprediction.",
    }
    report_path = args.out_dir / "ground_motion_residual_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
