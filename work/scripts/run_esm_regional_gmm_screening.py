#!/usr/bin/env python3
"""Regional GMM screening on compact ESM early-window splits."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import pandas as pd
from openquake.hazardlib.gsim.akkar_2014 import AkkarEtAlRhyp2014, AkkarEtAlRjb2014
from openquake.hazardlib.gsim.bindi_2014 import BindiEtAl2014Rhyp, BindiEtAl2014Rjb
from openquake.hazardlib.gsim.boore_2014 import BooreEtAl2014
from openquake.hazardlib.gsim.cauzzi_2014 import CauzziEtAl2014
from openquake.hazardlib.imt import PGA, PGV
from sklearn.metrics import mean_absolute_error, r2_score

from run_esm_compact_baseline import (
    DISTANCE_COLS,
    RAW_WAVEFORM_COLS,
    SITE_COLS,
    add_features,
    fit_predict,
    score,
    split_by_group,
)

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


G_CMPS2 = 980.665
TARGET_IMTS = {"pga": PGA(), "pgv": PGV()}
GMM_SPECS = [
    ("BooreEtAl2014_Rjb", BooreEtAl2014),
    ("AkkarEtAlRjb2014", AkkarEtAlRjb2014),
    ("AkkarEtAlRhyp2014", AkkarEtAlRhyp2014),
    ("BindiEtAl2014Rjb", BindiEtAl2014Rjb),
    ("BindiEtAl2014Rhyp", BindiEtAl2014Rhyp),
    ("CauzziEtAl2014", CauzziEtAl2014),
]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def make_ctx(df: pd.DataFrame) -> np.recarray:
    ctx = np.recarray(
        len(df),
        dtype=[
            ("mag", float),
            ("rake", float),
            ("rjb", float),
            ("rhypo", float),
            ("rrup", float),
            ("vs30", float),
        ],
    )
    ctx.mag = pd.to_numeric(df["source_magnitude"], errors="coerce").to_numpy(float)
    ctx.rake = 0.0
    ctx.rjb = pd.to_numeric(df["source_distance_km"], errors="coerce").clip(lower=1.0).to_numpy(float)
    hyp = pd.to_numeric(df["path_hyp_distance_km"], errors="coerce").clip(lower=1.0).to_numpy(float)
    ctx.rhypo = hyp
    ctx.rrup = hyp
    ctx.vs30 = (
        pd.to_numeric(df["station_vs30_mps"], errors="coerce")
        .clip(lower=150.0, upper=1500.0)
        .fillna(760.0)
        .to_numpy(float)
    )
    return ctx


def gmm_log10(df: pd.DataFrame, target: str, model_cls: type) -> np.ndarray:
    mean = np.zeros((1, len(df)))
    sig = np.zeros_like(mean)
    tau = np.zeros_like(mean)
    phi = np.zeros_like(mean)
    model_cls().compute(make_ctx(df), [TARGET_IMTS[target]], mean, sig, tau, phi)
    values = np.exp(mean[0])
    if target != "pgv":
        values = values * G_CMPS2
    return np.log10(values)


def evaluate_gmm(train: pd.DataFrame, test: pd.DataFrame, target: str, name: str, model_cls: type) -> dict[str, float]:
    y_train = train[f"target_log10_{target}"].to_numpy(float)
    y_test = test[f"target_log10_{target}"].to_numpy(float)
    pred_train = gmm_log10(train, target, model_cls)
    pred_test_raw = gmm_log10(test, target, model_cls)
    bias = float(np.nanmedian(y_train - pred_train))
    pred = pred_test_raw + bias
    return {
        "reference": name,
        "model_family": "regional_gmm_bias_corrected",
        "bias_log10": bias,
        "mae_log10_target": float(mean_absolute_error(y_test, pred)),
        "r2_log10_target": float(r2_score(y_test, pred)),
        "q90_abs_error_log10_target": float(np.nanquantile(np.abs(y_test - pred), 0.9)),
        "q95_abs_error_log10_target": float(np.nanquantile(np.abs(y_test - pred), 0.95)),
    }


def evaluate_split(
    train: pd.DataFrame,
    test: pd.DataFrame,
    target: str,
    early_cols: list[str],
    meta: dict[str, Any],
) -> list[dict[str, Any]]:
    target_col = f"target_log10_{target}"
    train_t = train[pd.to_numeric(train[target_col], errors="coerce").notna()].copy()
    test_t = test[pd.to_numeric(test[target_col], errors="coerce").notna()].copy()
    rows: list[dict[str, Any]] = []
    pred = fit_predict(train_t, test_t, early_cols, target_col, "p_waveform_distance_site")
    rows.append(
        {
            **meta,
            "target": target,
            "reference": "early_waveform_distance_site_hgb",
            "model_family": "early_waveform_model",
            "bias_log10": np.nan,
            **score(test_t[target_col].astype(float).to_numpy(), pred),
        }
    )
    for name, model_cls in GMM_SPECS:
        rows.append({**meta, "target": target, **evaluate_gmm(train_t, test_t, target, name, model_cls)})
    return rows


def plot_summary(rows: list[dict[str, Any]], path: Path) -> None:
    df = pd.DataFrame(rows)
    station = df[df["holdout"].eq("station")].copy()
    best = (
        station[station["model_family"].eq("regional_gmm_bias_corrected")]
        .sort_values("mae_log10_target")
        .groupby(["target", "early_seconds"], as_index=False)
        .first()
    )
    early = station[station["reference"].eq("early_waveform_distance_site_hgb")].copy()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4), dpi=180, sharey=True)
    for ax, target in zip(axes, ["pga", "pgv"]):
        sub_best = best[best["target"].eq(target)].sort_values("early_seconds")
        sub_early = early[early["target"].eq(target)].sort_values("early_seconds")
        ax.plot(
            sub_best["early_seconds"],
            sub_best["mae_log10_target"],
            marker="s",
            color="#c46a2b",
            label="best regional GMM",
        )
        ax.plot(
            sub_early["early_seconds"],
            sub_early["mae_log10_target"],
            marker="o",
            color="#2f6f9f",
            label="early P + distance + site",
        )
        for _, row in sub_best.iterrows():
            ax.text(
                row["early_seconds"],
                row["mae_log10_target"] + 0.012,
                str(row["reference"]).replace("EtAl", " "),
                ha="center",
                va="bottom",
                fontsize=7,
                color="#7a3d17",
            )
        ax.set_title(f"{target.upper()} held-station", loc="left", pad=8)
        ax.set_xlabel("P-window length (s)")
        ax.set_xticks(sorted(early["early_seconds"].unique()))
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("MAE (log10 target)")
    axes[1].legend(frameon=False, loc="upper right")
    fig.suptitle("ESM regional GMM screening", y=1.02)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def write_summary(path: Path, rows: list[dict[str, Any]], fig_path: Path, work_csv: Path) -> None:
    df = pd.DataFrame(rows)
    station = df[df["holdout"].eq("station")].copy()
    best = (
        station[station["model_family"].eq("regional_gmm_bias_corrected")]
        .sort_values("mae_log10_target")
        .groupby(["target", "early_seconds"], as_index=False)
        .first()
    )
    early = station[station["reference"].eq("early_waveform_distance_site_hgb")].copy()
    lines = [
        "# ESM regional GMM screening",
        "",
        "This screening layer compares early-window ESM held-station models with bias-corrected OpenQuake GMM candidates on the same train/test rows. Rows without source magnitude are excluded because a GMM requires magnitude. Vs30 is clipped to 150-1500 m/s and missing Vs30 is set to 760 m/s.",
        "",
        "Distance mapping: Rjb models use `source_distance_km`; Rhyp and Rrup models use `path_hyp_distance_km`. Rake is fixed to 0 because mechanism metadata are incomplete in the compact table. This is a reviewer-facing classical reference, not a complete engineering GMPE validation.",
        "",
        "| Target | Window | Best regional GMM | GMM MAE | Early P+distance+site MAE | Early reduction vs GMM |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for _, row in best.sort_values(["target", "early_seconds"]).iterrows():
        e = early[(early["target"].eq(row["target"])) & (early["early_seconds"].eq(row["early_seconds"]))].iloc[0]
        reduction = 100.0 * (row["mae_log10_target"] - e["mae_log10_target"]) / row["mae_log10_target"]
        lines.append(
            f"| {row['target'].upper()} | {row['early_seconds']:.0f}s | {row['reference']} | "
            f"{row['mae_log10_target']:.3f} | {e['mae_log10_target']:.3f} | {reduction:.1f}% |"
        )
    lines += [
        "",
        "Interpretation: the comparison uses a stronger classical reference than a median or distance-only baseline. It supports the claim that early P-wave information adds predictive content beyond regional magnitude-distance-site scaling, while the fixed rake, distance proxies and missing-site defaults keep the claim at screening level.",
        "",
        f"Work CSV: `{work_csv}`",
        f"Public CSV: `outputs/esm_regional_gmm_screening.csv`",
        f"Figure: `{fig_path}`",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", type=Path, default=Path("work/esm_compact_features_full/esm_compact_features.csv.gz"))
    parser.add_argument("--out-dir", type=Path, default=Path("work/esm_regional_gmm_screening"))
    parser.add_argument("--public-csv", type=Path, default=Path("outputs/esm_regional_gmm_screening.csv"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/esm_regional_gmm_screening_summary.md"))
    parser.add_argument(
        "--figure",
        type=Path,
        default=Path("outputs/figures/ground_motion_audit/esm_regional_gmm_screening.png"),
    )
    parser.add_argument("--windows", nargs="+", type=float, default=[2.0, 5.0, 10.0])
    parser.add_argument("--train-size", type=int, default=20000)
    parser.add_argument("--test-size", type=int, default=6000)
    parser.add_argument("--station-test-groups", type=int, default=200)
    parser.add_argument("--seed", type=int, default=71)
    args = parser.parse_args()

    df = add_features(pd.read_csv(args.features, low_memory=False))
    log_waveform = [f"log10_{col}" for col in RAW_WAVEFORM_COLS if f"log10_{col}" in df.columns]
    early_cols = log_waveform + [col for col in DISTANCE_COLS + SITE_COLS if col in df.columns]
    needed = ["source_magnitude", "source_distance_km", "path_hyp_distance_km"]
    rows: list[dict[str, Any]] = []
    splits: list[dict[str, Any]] = []
    for window in args.windows:
        sub = df[df["early_seconds"].astype(float).eq(float(window))].copy()
        sub = sub[sub["p_window_valid"].astype(bool)].copy()
        before = len(sub)
        sub = sub.dropna(subset=needed).copy()
        for holdout, group_col in [("event", "event_id"), ("station", "station_group")]:
            seed = args.seed + int(window * 10) + (1000 if holdout == "station" else 0)
            train, test, split = split_by_group(
                sub,
                group_col=group_col,
                train_size=args.train_size,
                test_size=args.test_size,
                seed=seed,
                station_test_groups=args.station_test_groups if holdout == "station" else 0,
            )
            split.update(
                {
                    "dataset": "esm",
                    "holdout": holdout,
                    "early_seconds": float(window),
                    "rows_before_gmm_filter": int(before),
                    "rows_after_gmm_filter": int(len(sub)),
                    "dropped_missing_source_magnitude_or_distance": int(before - len(sub)),
                    "vs30_missing_fraction_train": float(train["station_vs30_mps"].isna().mean()),
                    "vs30_missing_fraction_test": float(test["station_vs30_mps"].isna().mean()),
                }
            )
            splits.append(split)
            meta = {
                "dataset": "esm",
                "holdout": holdout,
                "early_seconds": float(window),
                "train_rows": int(len(train)),
                "test_rows": int(len(test)),
                "train_groups": int(split["train_groups"]),
                "test_groups": int(split["test_groups"]),
                "group_overlap": int(split["group_overlap"]),
                "rows_after_gmm_filter": int(len(sub)),
                "vs30_missing_fraction_train": float(train["station_vs30_mps"].isna().mean()),
                "vs30_missing_fraction_test": float(test["station_vs30_mps"].isna().mean()),
                "magnitude_missing_policy": "drop_missing_source_magnitude",
                "vs30_missing_policy": "fill_760_mps_for_gmm",
                "distance_mapping": "rjb=source_distance_km; rhypo/rrup=path_hyp_distance_km",
            }
            for target in TARGET_IMTS:
                rows.extend(evaluate_split(train, test, target, early_cols, meta))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    work_csv = args.out_dir / "esm_regional_gmm_screening.csv"
    split_csv = args.out_dir / "esm_regional_gmm_split_info.csv"
    write_csv(work_csv, rows)
    write_csv(split_csv, splits)
    write_csv(args.public_csv, rows)
    plot_summary(rows, args.figure)
    write_summary(args.summary, rows, args.figure, work_csv)
    print(f"wrote {work_csv}")
    print(f"wrote {split_csv}")
    print(f"wrote {args.public_csv}")
    print(f"wrote {args.summary}")
    print(f"wrote {args.figure}")


if __name__ == "__main__":
    main()
