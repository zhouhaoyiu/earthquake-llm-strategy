#!/usr/bin/env python3
"""Train a compact waveform encoder for ground-motion targets.

This script is a go/no-go experiment for the NC route. It tests whether a
learned early-window waveform representation can compete with the hand-crafted
early-window features used in run_ground_motion_baseline.py.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from run_ground_motion_baseline import (
    METADATA_FEATURES,
    TARGET_COLUMNS,
    early_window,
    load_waveform,
    metadata_features,
    select_rows,
    to_float,
)


@dataclass
class PreparedData:
    global_ids: list[str]
    waveforms: np.ndarray
    metadata: np.ndarray
    targets: np.ndarray
    target_mask: np.ndarray


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def signed_log1p(x: np.ndarray) -> np.ndarray:
    return np.sign(x) * np.log1p(np.abs(x))


def fixed_window(row: dict[str, Any], early_seconds: float, target_samples: int) -> np.ndarray:
    arr = load_waveform(row)
    win = early_window(arr, row, early_seconds)
    if win.shape[1] == target_samples:
        return win.astype(np.float32, copy=False)
    if win.shape[1] <= 1:
        out = np.zeros((3, target_samples), dtype=np.float32)
        if win.shape[1] == 1:
            out[:] = win[:, :1]
        return out
    x_old = np.linspace(0.0, 1.0, win.shape[1], dtype=np.float32)
    x_new = np.linspace(0.0, 1.0, target_samples, dtype=np.float32)
    out = np.vstack([np.interp(x_new, x_old, win[i]).astype(np.float32) for i in range(3)])
    return out


def prepare_rows(
    rows: list[dict[str, str]],
    early_seconds: float,
    sample_rate: float,
    targets: dict[str, str],
) -> tuple[PreparedData, list[dict[str, str]]]:
    target_samples = int(round(early_seconds * sample_rate))
    global_ids: list[str] = []
    waveforms: list[np.ndarray] = []
    metadata_rows: list[list[float]] = []
    y_rows: list[list[float]] = []
    mask_rows: list[list[float]] = []
    errors: list[dict[str, str]] = []

    for row in rows:
        try:
            wf = fixed_window(row, early_seconds, target_samples)
            md = metadata_features(row)
            y_values: list[float] = []
            mask_values: list[float] = []
            for target_name, target_col in targets.items():
                value = to_float(row.get(target_col))
                if value is not None and value > 0:
                    y_values.append(math.log10(value))
                    mask_values.append(1.0)
                else:
                    y_values.append(0.0)
                    mask_values.append(0.0)
            if not any(mask_values):
                continue
            global_ids.append(row["global_id"])
            waveforms.append(wf)
            metadata_rows.append([float(md.get(col, np.nan)) for col in METADATA_FEATURES])
            y_rows.append(y_values)
            mask_rows.append(mask_values)
        except Exception as exc:
            errors.append(
                {
                    "global_id": row.get("global_id", ""),
                    "dataset": row.get("dataset", ""),
                    "error": repr(exc),
                }
            )

    data = PreparedData(
        global_ids=global_ids,
        waveforms=np.stack(waveforms).astype(np.float32) if waveforms else np.empty((0, 3, target_samples), dtype=np.float32),
        metadata=np.asarray(metadata_rows, dtype=np.float32) if metadata_rows else np.empty((0, len(METADATA_FEATURES)), dtype=np.float32),
        targets=np.asarray(y_rows, dtype=np.float32) if y_rows else np.empty((0, len(targets)), dtype=np.float32),
        target_mask=np.asarray(mask_rows, dtype=np.float32) if mask_rows else np.empty((0, len(targets)), dtype=np.float32),
    )
    return data, errors


def split_train_val(data: PreparedData, val_fraction: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    n = len(data.global_ids)
    idx = np.arange(n)
    rng = np.random.default_rng(seed)
    rng.shuffle(idx)
    val_n = max(1, int(round(n * val_fraction))) if n > 10 else 0
    val_idx = idx[:val_n]
    train_idx = idx[val_n:]
    return train_idx, val_idx


def fit_waveform_scaler(x_train: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = signed_log1p(x_train)
    mean = x.mean(axis=(0, 2), keepdims=True)
    std = x.std(axis=(0, 2), keepdims=True)
    std = np.where(std < 1e-6, 1.0, std)
    return mean.astype(np.float32), std.astype(np.float32)


def scale_waveforms(x: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return ((signed_log1p(x) - mean) / std).astype(np.float32)


def fit_metadata_scaler(x_train: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    med = np.nanmedian(x_train, axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    filled = np.where(np.isfinite(x_train), x_train, med)
    mean = filled.mean(axis=0)
    std = filled.std(axis=0)
    std = np.where(std < 1e-6, 1.0, std)
    return med.astype(np.float32), mean.astype(np.float32), std.astype(np.float32)


def scale_metadata(x: np.ndarray, med: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    filled = np.where(np.isfinite(x), x, med)
    return ((filled - mean) / std).astype(np.float32)


def fit_target_scaler(y_train: np.ndarray, mask_train: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    means = np.zeros(y_train.shape[1], dtype=np.float32)
    stds = np.ones(y_train.shape[1], dtype=np.float32)
    for idx in range(y_train.shape[1]):
        valid = mask_train[:, idx] > 0
        if valid.sum() == 0:
            continue
        values = y_train[valid, idx]
        means[idx] = float(values.mean())
        std = float(values.std())
        stds[idx] = std if std >= 1e-6 else 1.0
    return means, stds


def scale_targets(y: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return ((y - mean) / std).astype(np.float32)


def unscale_targets(y: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return (y * std + mean).astype(np.float32)


class WaveformRegressor(nn.Module):
    def __init__(self, n_targets: int, metadata_dim: int = 0) -> None:
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv1d(3, 32, kernel_size=9, stride=2, padding=4),
            nn.GELU(),
            nn.BatchNorm1d(32),
            nn.Conv1d(32, 64, kernel_size=7, stride=2, padding=3),
            nn.GELU(),
            nn.BatchNorm1d(64),
            nn.Conv1d(64, 128, kernel_size=5, stride=2, padding=2),
            nn.GELU(),
            nn.BatchNorm1d(128),
            nn.Conv1d(128, 128, kernel_size=3, stride=2, padding=1),
            nn.GELU(),
        )
        self.avg_pool = nn.AdaptiveAvgPool1d(1)
        self.max_pool = nn.AdaptiveMaxPool1d(1)
        hidden_in = 256 + metadata_dim
        self.head = nn.Sequential(
            nn.Linear(hidden_in, 128),
            nn.GELU(),
            nn.Dropout(0.10),
            nn.Linear(128, n_targets),
        )

    def forward(self, waveforms: torch.Tensor, metadata: torch.Tensor | None = None) -> torch.Tensor:
        h = self.encoder(waveforms)
        z = torch.cat([self.avg_pool(h).squeeze(-1), self.max_pool(h).squeeze(-1)], dim=1)
        if metadata is not None:
            z = torch.cat([z, metadata], dim=1)
        return self.head(z)


def masked_mse(pred: torch.Tensor, target: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    diff = (pred - target) ** 2 * mask
    return diff.sum() / mask.sum().clamp_min(1.0)


def masked_mae_np(pred: np.ndarray, target: np.ndarray, mask: np.ndarray) -> float:
    valid = mask > 0
    if not np.any(valid):
        return float("nan")
    return float(np.abs(pred[valid] - target[valid]).mean())


def choose_device(name: str) -> torch.device:
    if name != "auto":
        return torch.device(name)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def make_loader(
    waveforms: np.ndarray,
    metadata: np.ndarray,
    targets: np.ndarray,
    mask: np.ndarray,
    batch_size: int,
    shuffle: bool,
) -> DataLoader:
    ds = TensorDataset(
        torch.from_numpy(waveforms),
        torch.from_numpy(metadata),
        torch.from_numpy(targets),
        torch.from_numpy(mask),
    )
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, drop_last=False)


def evaluate_model(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    use_metadata: bool,
    target_mean: np.ndarray,
    target_std: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    model.eval()
    preds: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    masks: list[np.ndarray] = []
    with torch.no_grad():
        for xb, mb, yb, maskb in loader:
            xb = xb.to(device)
            mb = mb.to(device)
            pred = model(xb, mb if use_metadata else None)
            preds.append(pred.cpu().numpy())
            ys.append(yb.numpy())
            masks.append(maskb.numpy())
    pred_arr = unscale_targets(np.concatenate(preds, axis=0), target_mean, target_std)
    y_arr = unscale_targets(np.concatenate(ys, axis=0), target_mean, target_std)
    mask_arr = np.concatenate(masks, axis=0)
    return pred_arr, y_arr, mask_arr, masked_mae_np(pred_arr, y_arr, mask_arr)


def train_one(
    train_data: PreparedData,
    test_data: PreparedData,
    targets: list[str],
    use_metadata: bool,
    args: argparse.Namespace,
    device: torch.device,
    dataset: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    train_idx, val_idx = split_train_val(train_data, args.val_fraction, args.seed)
    wf_mean, wf_std = fit_waveform_scaler(train_data.waveforms[train_idx])
    x_train_all = scale_waveforms(train_data.waveforms, wf_mean, wf_std)
    x_test = scale_waveforms(test_data.waveforms, wf_mean, wf_std)

    md_med, md_mean, md_std = fit_metadata_scaler(train_data.metadata[train_idx])
    md_train_all = scale_metadata(train_data.metadata, md_med, md_mean, md_std)
    md_test = scale_metadata(test_data.metadata, md_med, md_mean, md_std)
    if not use_metadata:
        md_train_all = np.empty((md_train_all.shape[0], 0), dtype=np.float32)
        md_test = np.empty((md_test.shape[0], 0), dtype=np.float32)

    target_mean, target_std = fit_target_scaler(train_data.targets[train_idx], train_data.target_mask[train_idx])
    y_train_all = scale_targets(train_data.targets, target_mean, target_std)
    y_test = scale_targets(test_data.targets, target_mean, target_std)

    train_loader = make_loader(
        x_train_all[train_idx],
        md_train_all[train_idx],
        y_train_all[train_idx],
        train_data.target_mask[train_idx],
        args.batch_size,
        True,
    )
    val_loader = make_loader(
        x_train_all[val_idx],
        md_train_all[val_idx],
        y_train_all[val_idx],
        train_data.target_mask[val_idx],
        args.batch_size,
        False,
    )
    test_loader = make_loader(x_test, md_test, y_test, test_data.target_mask, args.batch_size, False)

    model = WaveformRegressor(n_targets=len(targets), metadata_dim=md_train_all.shape[1]).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    best_state = None
    best_val_mae = float("inf")
    history: list[dict[str, Any]] = []

    for epoch in range(1, args.epochs + 1):
        model.train()
        losses = []
        for xb, mb, yb, maskb in train_loader:
            xb = xb.to(device)
            mb = mb.to(device)
            yb = yb.to(device)
            maskb = maskb.to(device)
            opt.zero_grad(set_to_none=True)
            pred = model(xb, mb if use_metadata else None)
            loss = masked_mse(pred, yb, maskb)
            loss.backward()
            opt.step()
            losses.append(float(loss.detach().cpu()))

        _, _, _, val_mae = evaluate_model(model, val_loader, device, use_metadata, target_mean, target_std)
        history.append({"epoch": epoch, "train_loss": float(np.mean(losses)), "val_masked_mae": val_mae})
        print(
            f"{dataset} {'waveform+metadata' if use_metadata else 'waveform'} "
            f"epoch={epoch} train_loss={np.mean(losses):.4f} val_mae={val_mae:.4f}",
            flush=True,
        )
        if val_mae < best_val_mae:
            best_val_mae = val_mae
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)
    pred, y, mask, test_masked_mae = evaluate_model(model, test_loader, device, use_metadata, target_mean, target_std)

    feature_set = "cnn_waveform_metadata" if use_metadata else "cnn_waveform"
    metrics: list[dict[str, Any]] = []
    for target_idx, target_name in enumerate(targets):
        valid = mask[:, target_idx] > 0
        if valid.sum() < 2:
            metrics.append(
                {
                    "dataset": dataset,
                    "target": target_name,
                    "feature_set": feature_set,
                    "early_seconds": args.early_seconds,
                    "train_rows": int(train_data.target_mask[:, target_idx].sum()),
                    "test_rows": int(valid.sum()),
                    "mae_log10_target": None,
                    "rmse_log10_target": None,
                    "r2_log10_target": None,
                    "best_val_masked_mae": best_val_mae,
                    "test_masked_mae": test_masked_mae,
                    "epochs": args.epochs,
                    "device": str(device),
                    "skipped": True,
                }
            )
            continue
        y_true = y[valid, target_idx]
        y_pred = pred[valid, target_idx]
        metrics.append(
            {
                "dataset": dataset,
                "target": target_name,
                "feature_set": feature_set,
                "early_seconds": args.early_seconds,
                "train_rows": int(train_data.target_mask[:, target_idx].sum()),
                "test_rows": int(valid.sum()),
                "mae_log10_target": float(mean_absolute_error(y_true, y_pred)),
                "rmse_log10_target": float(mean_squared_error(y_true, y_pred) ** 0.5),
                "r2_log10_target": float(r2_score(y_true, y_pred)),
                "best_val_masked_mae": best_val_mae,
                "test_masked_mae": test_masked_mae,
                "epochs": args.epochs,
                "device": str(device),
                "skipped": False,
            }
        )

    prediction_rows: list[dict[str, Any]] = []
    for row_idx, global_id in enumerate(test_data.global_ids):
        for target_idx, target_name in enumerate(targets):
            if mask[row_idx, target_idx] <= 0:
                continue
            prediction_rows.append(
                {
                    "global_id": global_id,
                    "dataset": dataset,
                    "target": target_name,
                    "feature_set": feature_set,
                    "actual_log10_target": float(y[row_idx, target_idx]),
                    "pred_log10_target": float(pred[row_idx, target_idx]),
                    "residual_log10_target": float(pred[row_idx, target_idx] - y[row_idx, target_idx]),
                }
            )

    diagnostics = {
        "feature_set": feature_set,
        "history": history,
        "waveform_mean": wf_mean.reshape(-1).tolist(),
        "waveform_std": wf_std.reshape(-1).tolist(),
        "metadata_features": METADATA_FEATURES,
        "metadata_median": md_med.tolist(),
        "metadata_mean": md_mean.tolist(),
        "metadata_std": md_std.tolist(),
        "target_names": targets,
        "target_mean": target_mean.tolist(),
        "target_std": target_std.tolist(),
    }
    return metrics, prediction_rows, diagnostics


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("work/unified_manifest/unified_manifest.csv.gz"))
    parser.add_argument("--out-dir", type=Path, default=Path("work/waveform_encoder_ground_motion"))
    parser.add_argument("--datasets", nargs="+", default=["instancegm", "knet"])
    parser.add_argument("--targets", nargs="+", default=["pga", "pgv", "sa03", "sa10", "sa30"])
    parser.add_argument("--train-size", type=int, default=5000)
    parser.add_argument("--test-size", type=int, default=1000)
    parser.add_argument("--early-seconds", type=float, default=3.0)
    parser.add_argument("--sample-rate", type=float, default=100.0)
    parser.add_argument("--max-samples", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=37)
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-3)
    parser.add_argument("--val-fraction", type=float, default=0.1)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--no-metadata-model", action="store_true")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    set_seed(args.seed)
    device = choose_device(args.device)
    targets = {name: TARGET_COLUMNS[name] for name in args.targets if name in TARGET_COLUMNS}
    target_columns = list(targets.values())
    target_names = list(targets)

    all_metrics: list[dict[str, Any]] = []
    all_predictions: list[dict[str, Any]] = []
    all_errors: list[dict[str, str]] = []
    diagnostics: dict[str, Any] = {}

    for dataset in args.datasets:
        print(f"selecting {dataset}", flush=True)
        train_rows = select_rows(args.manifest, dataset, "train", args.train_size, args.seed, args.max_samples, target_columns)
        test_rows = select_rows(args.manifest, dataset, "test", args.test_size, args.seed + 1, args.max_samples, target_columns)
        print(f"preparing tensors {dataset}: train={len(train_rows)} test={len(test_rows)}", flush=True)
        train_data, train_errors = prepare_rows(train_rows, args.early_seconds, args.sample_rate, targets)
        test_data, test_errors = prepare_rows(test_rows, args.early_seconds, args.sample_rate, targets)
        all_errors.extend(train_errors + test_errors)
        print(
            f"prepared {dataset}: train={len(train_data.global_ids)} test={len(test_data.global_ids)} "
            f"errors={len(train_errors) + len(test_errors)}",
            flush=True,
        )
        if len(train_data.global_ids) < 20 or len(test_data.global_ids) < 20:
            print(f"skipping {dataset}: too few rows after preparation", flush=True)
            continue

        for use_metadata in [False, True]:
            if use_metadata and args.no_metadata_model:
                continue
            metrics, predictions, diag = train_one(train_data, test_data, target_names, use_metadata, args, device, dataset)
            all_metrics.extend(metrics)
            all_predictions.extend(predictions)
            diagnostics[f"{dataset}_{diag['feature_set']}"] = diag

    metrics_path = args.out_dir / "waveform_encoder_ground_motion_results.csv"
    predictions_path = args.out_dir / "waveform_encoder_ground_motion_predictions.csv"
    errors_path = args.out_dir / "waveform_encoder_ground_motion_errors.csv"
    write_csv(metrics_path, all_metrics)
    write_csv(predictions_path, all_predictions)
    write_csv(errors_path, all_errors)

    report = {
        "manifest": str(args.manifest),
        "datasets": args.datasets,
        "targets": target_names,
        "train_size_requested": args.train_size,
        "test_size_requested": args.test_size,
        "early_seconds": args.early_seconds,
        "sample_rate": args.sample_rate,
        "max_samples": args.max_samples,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "device": str(device),
        "metrics_path": str(metrics_path),
        "predictions_path": str(predictions_path),
        "errors_path": str(errors_path) if all_errors else "",
        "metrics": all_metrics,
        "diagnostics": diagnostics,
        "note": "Compact CNN encoder experiment. This is supervised ground-motion regression, not a foundation-model result.",
    }
    report_path = args.out_dir / "waveform_encoder_ground_motion_summary.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
