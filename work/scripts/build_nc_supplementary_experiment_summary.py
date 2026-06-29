#!/usr/bin/env python3
"""Summarize supplementary NC experiments into tables and one compact figure."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work/nc_supplementary_experiments"
FIG = ROOT / "outputs/figures/ground_motion_audit/nc_supplementary_experiments_summary.png"
SUMMARY = ROOT / "outputs/nc_supplementary_experiments_summary_zh.md"


def read_calibration() -> tuple[pd.DataFrame, pd.DataFrame]:
    table = pd.read_csv(ROOT / "work/nc_calibration_size_audit/target_calibration_size_audit.csv")
    target = table[table["mode"].eq("target_offset_conformal")].copy()
    cal = (
        target.groupby(["early_seconds", "calibration_rows"], as_index=False)
        .agg(
            median_coverage90=("coverage90", "median"),
            q25_coverage90=("coverage90", lambda s: s.quantile(0.25)),
            q75_coverage90=("coverage90", lambda s: s.quantile(0.75)),
            median_width_log10=("interval_width_log10", "median"),
        )
        .sort_values(["early_seconds", "calibration_rows"])
    )
    source = (
        table[table["mode"].eq("source_conformal")]
        .groupby("early_seconds", as_index=False)
        .agg(
            source_median_coverage90=("coverage90", "median"),
            source_median_width_log10=("interval_width_log10", "median"),
        )
    )
    return cal, source


def read_waveform_encoder() -> pd.DataFrame:
    table = pd.read_csv(ROOT / "work/waveform_encoder_vs_hgb_3s_10s_comparison.csv")
    rows: list[dict[str, object]] = []
    for (window, dataset), sub in table.groupby(["window_s", "dataset"]):
        for cnn_set in ["cnn_waveform", "cnn_waveform_metadata"]:
            cnn = sub[sub["cnn_feature_set"].eq(cnn_set)]
            if cnn.empty:
                continue
            rows.append(
                {
                    "window_s": window,
                    "dataset": dataset,
                    "model": cnn_set,
                    "median_mae_log10": float(cnn["cnn_mae"].median()),
                    "median_r2": float(cnn["cnn_r2"].median()),
                    "targets": int(cnn["target"].nunique()),
                }
            )
        hgb = sub[sub["hgb_feature_set"].eq("metadata_plus_early_waveform")]
        if not hgb.empty:
            rows.append(
                {
                    "window_s": window,
                    "dataset": dataset,
                    "model": "hgb_metadata_plus_early_waveform",
                    "median_mae_log10": float(hgb["hgb_mae"].median()),
                    "median_r2": float(hgb["hgb_r2"].median()),
                    "targets": int(hgb["target"].nunique()),
                }
            )
    return pd.DataFrame(rows).sort_values(["window_s", "dataset", "model"])


def read_transfer() -> pd.DataFrame:
    frames = []
    for seconds in [2, 5]:
        path = ROOT / f"work/cross_region_waveform_transfer_aq_esm_{seconds}s/cross_region_waveform_transfer_boundary.csv"
        chunk = pd.read_csv(path)
        chunk = chunk[
            chunk["feature_set"].eq("raw_waveform")
            & chunk["target"].eq("pga")
            & ~chunk["source_dataset"].eq(chunk["test_dataset"])
            & chunk["skipped"].astype(str).str.lower().eq("false")
        ].copy()
        chunk["window_s"] = seconds
        frames.append(chunk)
    table = pd.concat(frames, ignore_index=True)
    summary = (
        table.groupby(["window_s", "calibration"], as_index=False)
        .agg(
            median_mae_ratio=("mae_ratio_vs_within_target", "median"),
            q25_mae_ratio=("mae_ratio_vs_within_target", lambda s: s.quantile(0.25)),
            q75_mae_ratio=("mae_ratio_vs_within_target", lambda s: s.quantile(0.75)),
            median_mae_log10=("mae_log10_target", "median"),
            pairs=("mae_log10_target", "size"),
        )
        .sort_values(["window_s", "calibration"])
    )
    return summary


def write_summary(cal: pd.DataFrame, source: pd.DataFrame, encoder: pd.DataFrame, transfer: pd.DataFrame) -> None:
    lines = [
        "# 补充实验摘要",
        "",
        "本文件汇总三个补强实验：目标区校准样本量、轻量波形编码器对照、四域早期波形 transfer。它们补充主文边界结论，不替代主 held-station 和外部数据验证。",
        "",
        "## 1 目标区校准样本量",
        "",
        "source-domain conformal interval 在跨区应用时欠覆盖。只估计一个目标区 offset 和 conformal 残差宽度后，50 条目标区校准记录已经使两个窗口的覆盖率中位数接近 0.90；100 条记录更稳定。区间宽度仍然很大，说明校准修复的是覆盖率，不是把跨区问题变成域内问题。",
        "",
        "| P窗长/s | 校准条数 | 覆盖率中位数 | 覆盖率IQR | 区间宽度中位数(log10) |",
        "|---:|---:|---:|---:|---:|",
    ]
    for _, row in cal[cal["calibration_rows"].isin([10, 50, 100, 1000])].iterrows():
        lines.append(
            f"| {row.early_seconds:g} | {int(row.calibration_rows)} | {row.median_coverage90:.3f} | "
            f"{row.q25_coverage90:.3f}-{row.q75_coverage90:.3f} | {row.median_width_log10:.3f} |"
        )
    lines += [
        "",
        "source-domain conformal baseline：",
        "",
        "| P窗长/s | 源域覆盖率中位数 | 源域区间宽度中位数(log10) |",
        "|---:|---:|---:|",
    ]
    for _, row in source.iterrows():
        lines.append(f"| {row.early_seconds:g} | {row.source_median_coverage90:.3f} | {row.source_median_width_log10:.3f} |")

    lines += [
        "",
        "## 2 轻量波形编码器对照",
        "",
        "小型 CNN 证明端到端早期波形可以学习到强震动信息；但在当前样本量和训练设置下，它没有超过稳定树模型和手工早窗统计。该结果支持本文选择保守模型：主结论来自公开数据、划分和不确定性边界，不来自复杂模型冲分。",
        "",
        "| P窗长/s | 数据集 | 模型 | 目标数 | MAE中位数(log10) | R2中位数 |",
        "|---:|---|---|---:|---:|---:|",
    ]
    keep_models = ["cnn_waveform", "cnn_waveform_metadata", "hgb_metadata_plus_early_waveform"]
    for _, row in encoder[encoder["model"].isin(keep_models)].iterrows():
        lines.append(
            f"| {row.window_s:g} | {row.dataset} | {row.model} | {int(row.targets)} | "
            f"{row.median_mae_log10:.3f} | {row.median_r2:.3f} |"
        )

    lines += [
        "",
        "## 3 四域早期波形 transfer",
        "",
        "只用早期波形统计进行跨域迁移时，误差相对目标域训练保持明显 penalty。目标区 offset 校准能降低 penalty，但不能消除跨区域差异。这一层把主文结论从“域内可预测”推进到“跨区域可预测性有边界”。",
        "",
        "| P窗长/s | 校准方式 | MAE penalty中位数 | IQR | MAE中位数(log10) | pair数 |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for _, row in transfer.iterrows():
        lines.append(
            f"| {row.window_s:g} | {row.calibration} | {row.median_mae_ratio:.2f} | "
            f"{row.q25_mae_ratio:.2f}-{row.q75_mae_ratio:.2f} | {row.median_mae_log10:.3f} | {int(row.pairs)} |"
        )
    SUMMARY.write_text("\n".join(lines) + "\n")


def plot(cal: pd.DataFrame, source: pd.DataFrame, encoder: pd.DataFrame, transfer: pd.DataFrame) -> None:
    plt.rcParams.update(
        {
            "font.size": 8.5,
            "axes.titlesize": 9.5,
            "axes.labelsize": 8.5,
            "legend.fontsize": 7.5,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
        }
    )
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.25), constrained_layout=True)

    colors = {2.0: "#2f6f9f", 5.0: "#d07a2d"}
    ax = axes[0]
    for window, sub in cal.groupby("early_seconds"):
        color = colors.get(float(window), "0.3")
        ax.plot(sub["calibration_rows"], sub["median_coverage90"], marker="o", color=color, label=f"{window:g} s target")
        base = source[source["early_seconds"].eq(window)]
        if not base.empty:
            ax.axhline(float(base["source_median_coverage90"].iloc[0]), color=color, linestyle=":", linewidth=1.0, label=f"{window:g} s source")
    ax.axhline(0.9, color="0.2", linestyle="--", linewidth=1.0)
    ax.set_xscale("log")
    ax.set_ylim(0, 1.02)
    ax.set_title("A. Target calibration restores coverage")
    ax.set_xlabel("Target calibration rows")
    ax.set_ylabel("90% coverage")
    ax.grid(True, axis="y", color="0.9", linewidth=0.8)
    ax.legend(frameon=False, loc="lower right", ncol=1)

    ax = axes[1]
    enc = encoder[
        encoder["window_s"].isin([3, 10])
        & encoder["model"].isin(["cnn_waveform", "cnn_waveform_metadata", "hgb_metadata_plus_early_waveform"])
    ].copy()
    enc["label"] = enc["window_s"].astype(int).astype(str) + "s " + enc["dataset"]
    groups = list(dict.fromkeys(enc["label"].tolist()))
    models = ["cnn_waveform", "cnn_waveform_metadata", "hgb_metadata_plus_early_waveform"]
    model_labels = ["CNN wave", "CNN wave+meta", "Tree wave+meta"]
    x = np.arange(len(groups))
    width = 0.24
    for i, model in enumerate(models):
        vals = []
        for group in groups:
            hit = enc[enc["label"].eq(group) & enc["model"].eq(model)]
            vals.append(float(hit["median_mae_log10"].iloc[0]) if not hit.empty else np.nan)
        ax.bar(x + (i - 1) * width, vals, width=width, label=model_labels[i])
    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=25, ha="right")
    ax.set_title("B. CNN is a guardrail, not the driver")
    ax.set_ylabel("Median MAE (log10)")
    ax.grid(True, axis="y", color="0.9", linewidth=0.8)
    ax.legend(frameon=False, loc="upper right")

    ax = axes[2]
    tr = transfer.copy()
    tr["label"] = tr["window_s"].astype(int).astype(str) + " s"
    labels = ["2 s", "5 s"]
    x = np.arange(len(labels))
    for i, cal_name in enumerate(["source_only", "target_offset_calibrated"]):
        vals = []
        for label in labels:
            hit = tr[tr["label"].eq(label) & tr["calibration"].eq(cal_name)]
            vals.append(float(hit["median_mae_ratio"].iloc[0]) if not hit.empty else np.nan)
        ax.bar(x + (i - 0.5) * 0.28, vals, width=0.28, label=cal_name.replace("_", " "))
    ax.axhline(1.0, color="0.2", linestyle="--", linewidth=1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("C. Transfer keeps a penalty")
    ax.set_ylabel("MAE ratio vs target-trained")
    ax.set_ylim(0, max(4.8, float(tr["median_mae_ratio"].max()) * 1.12))
    ax.grid(True, axis="y", color="0.9", linewidth=0.8)
    ax.legend(frameon=False, loc="upper left")

    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG, dpi=300)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cal, source = read_calibration()
    encoder = read_waveform_encoder()
    transfer = read_transfer()
    cal.to_csv(OUT / "target_calibration_size_summary.csv", index=False)
    source.to_csv(OUT / "source_conformal_baseline_summary.csv", index=False)
    encoder.to_csv(OUT / "waveform_encoder_guardrail_summary.csv", index=False)
    transfer.to_csv(OUT / "four_domain_transfer_summary.csv", index=False)
    write_summary(cal, source, encoder, transfer)
    plot(cal, source, encoder, transfer)
    print(SUMMARY)
    print(FIG)


if __name__ == "__main__":
    main()
