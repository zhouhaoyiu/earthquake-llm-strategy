#!/usr/bin/env python3
"""Masked waveform pretraining followed by ground-motion fine-tuning.

This is a representation-learning go/no-go trial. It pretrains a compact
waveform encoder by reconstructing masked post-P waveform windows, then
fine-tunes the same encoder on ground-motion targets.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader, TensorDataset

from run_ground_motion_baseline import TARGET_COLUMNS, select_rows
from run_waveform_encoder_ground_motion import (
    METADATA_FEATURES,
    PreparedData,
    fixed_window,
    fit_metadata_scaler,
    fit_target_scaler,
    prepare_rows,
    scale_metadata,
    scale_targets,
    split_train_val,
    unscale_targets,
)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def signed_log1p(x: np.ndarray) -> np.ndarray:
    return np.sign(x) * np.log1p(np.abs(x))


def choose_device(name: str) -> torch.device:
    if name != "auto":
        return torch.device(name)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def select_pretrain_rows(
    manifest: Path,
    datasets: list[str],
    split: str,
    n_per_dataset: int,
    seed: int,
    max_samples: int,
) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for dataset_idx, dataset in enumerate(datasets):
        rows: list[dict[str, str]] = []
        for chunk in pd.read_csv(manifest, chunksize=200_000, dtype=str):
            sub = chunk[
                (chunk["dataset"] == dataset)
                & (chunk["split"] == split)
                & (chunk["has_phase_task"] == "1")
            ].copy()
            if max_samples:
                sub["n_samples_num"] = pd.to_numeric(sub["n_samples"], errors="coerce")
                sub = sub[sub["n_samples_num"] <= max_samples]
            rows.extend(sub.drop(columns=[c for c in ["n_samples_num"] if c in sub]).to_dict("records"))
        rng = np.random.default_rng(seed + dataset_idx)
        if len(rows) > n_per_dataset:
            idx = np.arange(len(rows))
            rng.shuffle(idx)
            rows = [rows[int(i)] for i in idx[:n_per_dataset]]
        selected.extend(rows)
        print(f"selected pretrain {dataset}: {len(rows)}", flush=True)
    return selected


def prepare_pretrain_waveforms(
    rows: list[dict[str, str]],
    early_seconds: float,
    sample_rate: float,
) -> tuple[list[str], np.ndarray, list[dict[str, str]]]:
    target_samples = int(round(early_seconds * sample_rate))
    ids: list[str] = []
    waveforms: list[np.ndarray] = []
    errors: list[dict[str, str]] = []
    for row in rows:
        try:
            waveforms.append(fixed_window(row, early_seconds, target_samples))
            ids.append(row["global_id"])
        except Exception as exc:
            errors.append({"global_id": row.get("global_id", ""), "dataset": row.get("dataset", ""), "error": repr(exc)})
    if waveforms:
        arr = np.stack(waveforms).astype(np.float32)
    else:
        arr = np.empty((0, 3, target_samples), dtype=np.float32)
    return ids, arr, errors


def fit_waveform_scaler(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    z = signed_log1p(x)
    mean = z.mean(axis=(0, 2), keepdims=True)
    std = z.std(axis=(0, 2), keepdims=True)
    std = np.where(std < 1e-6, 1.0, std)
    return mean.astype(np.float32), std.astype(np.float32)


def scale_waveforms(x: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return ((signed_log1p(x) - mean) / std).astype(np.float32)


class SharedConvEncoder(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.net = nn.Sequential(
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

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class MaskedAutoencoder(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.encoder = SharedConvEncoder()
        self.decoder = nn.Sequential(
            nn.Conv1d(128, 64, kernel_size=5, padding=2),
            nn.GELU(),
            nn.Conv1d(64, 32, kernel_size=5, padding=2),
            nn.GELU(),
            nn.Conv1d(32, 3, kernel_size=3, padding=1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.encoder(x)
        h = F.interpolate(h, size=x.shape[-1], mode="linear", align_corners=False)
        return self.decoder(h)


class PretrainedRegressor(nn.Module):
    def __init__(self, n_targets: int, metadata_dim: int, encoder_state: dict[str, torch.Tensor]) -> None:
        super().__init__()
        self.encoder = SharedConvEncoder()
        self.encoder.load_state_dict(encoder_state)
        self.avg_pool = nn.AdaptiveAvgPool1d(1)
        self.max_pool = nn.AdaptiveMaxPool1d(1)
        self.head = nn.Sequential(
            nn.Linear(256 + metadata_dim, 128),
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


def make_mask(batch: torch.Tensor, mask_fraction: float, block_size: int) -> torch.Tensor:
    bsz, _, length = batch.shape
    mask = torch.zeros((bsz, 1, length), device=batch.device, dtype=batch.dtype)
    blocks = max(1, int(round(mask_fraction * length / max(1, block_size))))
    for row in range(bsz):
        starts = torch.randint(0, max(1, length - block_size + 1), (blocks,), device=batch.device)
        for start in starts:
            end = min(length, int(start.item()) + block_size)
            mask[row, :, int(start.item()) : end] = 1.0
    return mask


def masked_mse(pred: torch.Tensor, target: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    mask_full = mask.expand_as(target)
    return (((pred - target) ** 2) * mask_full).sum() / mask_full.sum().clamp_min(1.0)


def supervised_mse(pred: torch.Tensor, target: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    diff = ((pred - target) ** 2) * mask
    return diff.sum() / mask.sum().clamp_min(1.0)


def masked_mae_np(pred: np.ndarray, target: np.ndarray, mask: np.ndarray) -> float:
    valid = mask > 0
    if not np.any(valid):
        return float("nan")
    return float(np.abs(pred[valid] - target[valid]).mean())


def pretrain_encoder(
    x_pretrain: np.ndarray,
    args: argparse.Namespace,
    device: torch.device,
) -> tuple[dict[str, torch.Tensor], list[dict[str, float]]]:
    idx = np.arange(len(x_pretrain))
    rng = np.random.default_rng(args.seed)
    rng.shuffle(idx)
    val_n = max(1, int(round(len(idx) * args.pretrain_val_fraction)))
    val_idx = idx[:val_n]
    train_idx = idx[val_n:]
    train_loader = DataLoader(
        TensorDataset(torch.from_numpy(x_pretrain[train_idx])),
        batch_size=args.pretrain_batch_size,
        shuffle=True,
    )
    val_loader = DataLoader(
        TensorDataset(torch.from_numpy(x_pretrain[val_idx])),
        batch_size=args.pretrain_batch_size,
        shuffle=False,
    )
    model = MaskedAutoencoder().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.pretrain_lr, weight_decay=args.weight_decay)
    best_state: dict[str, torch.Tensor] | None = None
    best_val = float("inf")
    history: list[dict[str, float]] = []
    for epoch in range(1, args.pretrain_epochs + 1):
        model.train()
        train_losses: list[float] = []
        for (xb,) in train_loader:
            xb = xb.to(device)
            mask = make_mask(xb, args.mask_fraction, args.mask_block_size)
            masked = xb * (1.0 - mask)
            opt.zero_grad(set_to_none=True)
            pred = model(masked)
            loss = masked_mse(pred, xb, mask)
            loss.backward()
            opt.step()
            train_losses.append(float(loss.detach().cpu()))

        model.eval()
        val_losses: list[float] = []
        with torch.no_grad():
            for (xb,) in val_loader:
                xb = xb.to(device)
                mask = make_mask(xb, args.mask_fraction, args.mask_block_size)
                pred = model(xb * (1.0 - mask))
                val_losses.append(float(masked_mse(pred, xb, mask).detach().cpu()))
        train_loss = float(np.mean(train_losses))
        val_loss = float(np.mean(val_losses))
        history.append({"epoch": float(epoch), "train_masked_mse": train_loss, "val_masked_mse": val_loss})
        print(f"pretrain epoch={epoch} train_mse={train_loss:.4f} val_mse={val_loss:.4f}", flush=True)
        if val_loss < best_val:
            best_val = val_loss
            best_state = {key: value.detach().cpu().clone() for key, value in model.encoder.state_dict().items()}
    if best_state is None:
        best_state = {key: value.detach().cpu().clone() for key, value in model.encoder.state_dict().items()}
    return best_state, history


def make_supervised_loader(
    waveforms: np.ndarray,
    metadata: np.ndarray,
    targets: np.ndarray,
    mask: np.ndarray,
    batch_size: int,
    shuffle: bool,
) -> DataLoader:
    return DataLoader(
        TensorDataset(
            torch.from_numpy(waveforms),
            torch.from_numpy(metadata),
            torch.from_numpy(targets),
            torch.from_numpy(mask),
        ),
        batch_size=batch_size,
        shuffle=shuffle,
    )


def evaluate_regressor(
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


def finetune_one(
    dataset: str,
    train_data: PreparedData,
    test_data: PreparedData,
    target_names: list[str],
    encoder_state: dict[str, torch.Tensor],
    wf_mean: np.ndarray,
    wf_std: np.ndarray,
    use_metadata: bool,
    args: argparse.Namespace,
    device: torch.device,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    train_idx, val_idx = split_train_val(train_data, args.val_fraction, args.seed)
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

    train_loader = make_supervised_loader(
        x_train_all[train_idx],
        md_train_all[train_idx],
        y_train_all[train_idx],
        train_data.target_mask[train_idx],
        args.batch_size,
        True,
    )
    val_loader = make_supervised_loader(
        x_train_all[val_idx],
        md_train_all[val_idx],
        y_train_all[val_idx],
        train_data.target_mask[val_idx],
        args.batch_size,
        False,
    )
    test_loader = make_supervised_loader(x_test, md_test, y_test, test_data.target_mask, args.batch_size, False)

    model = PretrainedRegressor(len(target_names), md_train_all.shape[1], encoder_state).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    best_state = None
    best_val_mae = float("inf")
    history: list[dict[str, Any]] = []
    for epoch in range(1, args.epochs + 1):
        model.train()
        losses: list[float] = []
        for xb, mb, yb, maskb in train_loader:
            xb = xb.to(device)
            mb = mb.to(device)
            yb = yb.to(device)
            maskb = maskb.to(device)
            opt.zero_grad(set_to_none=True)
            pred = model(xb, mb if use_metadata else None)
            loss = supervised_mse(pred, yb, maskb)
            loss.backward()
            opt.step()
            losses.append(float(loss.detach().cpu()))
        _, _, _, val_mae = evaluate_regressor(model, val_loader, device, use_metadata, target_mean, target_std)
        history.append({"epoch": epoch, "train_loss": float(np.mean(losses)), "val_masked_mae": val_mae})
        print(
            f"{dataset} {'pretrained+metadata' if use_metadata else 'pretrained'} "
            f"epoch={epoch} train_loss={np.mean(losses):.4f} val_mae={val_mae:.4f}",
            flush=True,
        )
        if val_mae < best_val_mae:
            best_val_mae = val_mae
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
    if best_state is not None:
        model.load_state_dict(best_state)

    pred, y, mask, test_masked_mae = evaluate_regressor(model, test_loader, device, use_metadata, target_mean, target_std)
    feature_set = "masked_pretrain_cnn_metadata" if use_metadata else "masked_pretrain_cnn"
    metrics: list[dict[str, Any]] = []
    for target_idx, target_name in enumerate(target_names):
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
                "skipped": False,
            }
        )

    prediction_rows: list[dict[str, Any]] = []
    for row_idx, global_id in enumerate(test_data.global_ids):
        for target_idx, target_name in enumerate(target_names):
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
        "metadata_features": METADATA_FEATURES,
        "metadata_median": md_med.tolist(),
        "metadata_mean": md_mean.tolist(),
        "metadata_std": md_std.tolist(),
        "target_names": target_names,
        "target_mean": target_mean.tolist(),
        "target_std": target_std.tolist(),
    }
    return metrics, prediction_rows, diagnostics


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("work/unified_manifest/unified_manifest.csv.gz"))
    parser.add_argument("--out-dir", type=Path, default=Path("work/masked_pretrain_ground_motion"))
    parser.add_argument("--pretrain-datasets", nargs="+", default=["stead", "instancegm", "iquique", "knet"])
    parser.add_argument("--finetune-datasets", nargs="+", default=["instancegm", "knet"])
    parser.add_argument("--targets", nargs="+", default=["pga", "pgv", "sa03", "sa10", "sa30"])
    parser.add_argument("--pretrain-size-per-dataset", type=int, default=3000)
    parser.add_argument("--train-size", type=int, default=5000)
    parser.add_argument("--test-size", type=int, default=1000)
    parser.add_argument("--early-seconds", type=float, default=10.0)
    parser.add_argument("--sample-rate", type=float, default=100.0)
    parser.add_argument("--max-samples", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=53)
    parser.add_argument("--pretrain-epochs", type=int, default=10)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--pretrain-batch-size", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--pretrain-lr", type=float, default=1e-3)
    parser.add_argument("--lr", type=float, default=8e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-3)
    parser.add_argument("--mask-fraction", type=float, default=0.35)
    parser.add_argument("--mask-block-size", type=int, default=40)
    parser.add_argument("--pretrain-val-fraction", type=float, default=0.1)
    parser.add_argument("--val-fraction", type=float, default=0.1)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--no-metadata-model", action="store_true")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    set_seed(args.seed)
    device = choose_device(args.device)
    targets = {name: TARGET_COLUMNS[name] for name in args.targets if name in TARGET_COLUMNS}
    target_names = list(targets)
    target_columns = list(targets.values())

    print("selecting pretrain rows", flush=True)
    pretrain_rows = select_pretrain_rows(
        args.manifest,
        args.pretrain_datasets,
        "train",
        args.pretrain_size_per_dataset,
        args.seed,
        args.max_samples,
    )
    _, pretrain_wf, pretrain_errors = prepare_pretrain_waveforms(pretrain_rows, args.early_seconds, args.sample_rate)
    if len(pretrain_wf) < 100:
        raise RuntimeError(f"Too few pretraining waveforms: {len(pretrain_wf)}")
    wf_mean, wf_std = fit_waveform_scaler(pretrain_wf)
    pretrain_scaled = scale_waveforms(pretrain_wf, wf_mean, wf_std)
    encoder_state, pretrain_history = pretrain_encoder(pretrain_scaled, args, device)

    all_metrics: list[dict[str, Any]] = []
    all_predictions: list[dict[str, Any]] = []
    all_errors = pretrain_errors[:]
    diagnostics: dict[str, Any] = {
        "pretrain_history": pretrain_history,
        "waveform_mean": wf_mean.reshape(-1).tolist(),
        "waveform_std": wf_std.reshape(-1).tolist(),
        "pretrain_rows": len(pretrain_scaled),
    }

    for dataset in args.finetune_datasets:
        print(f"selecting finetune {dataset}", flush=True)
        train_rows = select_rows(args.manifest, dataset, "train", args.train_size, args.seed, args.max_samples, target_columns)
        test_rows = select_rows(args.manifest, dataset, "test", args.test_size, args.seed + 1, args.max_samples, target_columns)
        train_data, train_errors = prepare_rows(train_rows, args.early_seconds, args.sample_rate, targets)
        test_data, test_errors = prepare_rows(test_rows, args.early_seconds, args.sample_rate, targets)
        all_errors.extend(train_errors + test_errors)
        print(f"prepared {dataset}: train={len(train_data.global_ids)} test={len(test_data.global_ids)}", flush=True)
        if len(train_data.global_ids) < 20 or len(test_data.global_ids) < 20:
            continue
        for use_metadata in [False, True]:
            if use_metadata and args.no_metadata_model:
                continue
            metrics, predictions, diag = finetune_one(
                dataset,
                train_data,
                test_data,
                target_names,
                encoder_state,
                wf_mean,
                wf_std,
                use_metadata,
                args,
                device,
            )
            all_metrics.extend(metrics)
            all_predictions.extend(predictions)
            diagnostics[f"{dataset}_{diag['feature_set']}"] = diag

    metrics_path = args.out_dir / "masked_pretrain_ground_motion_results.csv"
    predictions_path = args.out_dir / "masked_pretrain_ground_motion_predictions.csv"
    errors_path = args.out_dir / "masked_pretrain_ground_motion_errors.csv"
    write_csv(metrics_path, all_metrics)
    write_csv(predictions_path, all_predictions)
    write_csv(errors_path, all_errors)

    report = {
        "manifest": str(args.manifest),
        "pretrain_datasets": args.pretrain_datasets,
        "finetune_datasets": args.finetune_datasets,
        "targets": target_names,
        "pretrain_size_per_dataset": args.pretrain_size_per_dataset,
        "train_size_requested": args.train_size,
        "test_size_requested": args.test_size,
        "early_seconds": args.early_seconds,
        "pretrain_epochs": args.pretrain_epochs,
        "epochs": args.epochs,
        "device": str(device),
        "metrics_path": str(metrics_path),
        "predictions_path": str(predictions_path),
        "errors_path": str(errors_path) if all_errors else "",
        "metrics": all_metrics,
        "diagnostics": diagnostics,
        "note": "Masked reconstruction pretraining followed by supervised ground-motion fine-tuning.",
    }
    report_path = args.out_dir / "masked_pretrain_ground_motion_summary.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
