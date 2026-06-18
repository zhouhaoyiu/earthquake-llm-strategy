#!/usr/bin/env python3
"""Screen Japanese/region-specific OpenQuake GMM references for K-NET PGA."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from openquake.hazardlib.gsim.kanno_2006 import Kanno2006Deep, Kanno2006Shallow
from openquake.hazardlib.gsim.si_midorikawa_1999 import (
    SiMidorikawa1999Asc,
    SiMidorikawa1999SInter,
    SiMidorikawa1999SSlab,
)
from openquake.hazardlib.gsim.zhao_2006 import ZhaoEtAl2006Asc, ZhaoEtAl2006SInter, ZhaoEtAl2006SSlab
from openquake.hazardlib.imt import PGA
from sklearn.metrics import mean_absolute_error, r2_score


G_CMPS2 = 980.665
GMM_SPECS = [
    ("Kanno2006Shallow", Kanno2006Shallow, 760.0),
    ("Kanno2006Deep", Kanno2006Deep, 760.0),
    ("ZhaoEtAl2006Asc", ZhaoEtAl2006Asc, 760.0),
    ("ZhaoEtAl2006SInter", ZhaoEtAl2006SInter, 760.0),
    ("ZhaoEtAl2006SSlab", ZhaoEtAl2006SSlab, 760.0),
    ("SiMidorikawa1999Asc", SiMidorikawa1999Asc, 600.0),
    ("SiMidorikawa1999SInter", SiMidorikawa1999SInter, 600.0),
    ("SiMidorikawa1999SSlab", SiMidorikawa1999SSlab, 600.0),
]


def make_ctx(df: pd.DataFrame, vs30_default: float) -> np.recarray:
    ctx = np.recarray(
        len(df),
        dtype=[("mag", float), ("rake", float), ("rrup", float), ("vs30", float), ("hypo_depth", float)],
    )
    ctx.mag = pd.to_numeric(df["source_magnitude"], errors="coerce").fillna(5.0).to_numpy(float)
    ctx.rake = 0.0
    # ponytail: source_distance_km is the available proxy; replace with rupture distance when a rupture model exists.
    ctx.rrup = pd.to_numeric(df["source_distance_km"], errors="coerce").clip(lower=1.0).fillna(10.0).to_numpy(float)
    ctx.hypo_depth = pd.to_numeric(df["source_depth_km"], errors="coerce").clip(lower=0.0).fillna(10.0).to_numpy(float)
    ctx.vs30 = vs30_default
    return ctx


def gmm_log10_cmps2(model_cls, df: pd.DataFrame, vs30_default: float) -> np.ndarray:
    ctx = make_ctx(df, vs30_default)
    mean = np.zeros((1, len(df)))
    sig = np.zeros_like(mean)
    tau = np.zeros_like(mean)
    phi = np.zeros_like(mean)
    model_cls().compute(ctx, [PGA()], mean, sig, tau, phi)
    return np.log10(np.exp(mean[0]) * G_CMPS2)


def evaluate(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    y_train = train["target_log10_pga"].to_numpy(float)
    y_test = test["target_log10_pga"].to_numpy(float)
    rows = []
    for name, cls, vs30_default in GMM_SPECS:
        pred_train = gmm_log10_cmps2(cls, train, vs30_default)
        pred_test_raw = gmm_log10_cmps2(cls, test, vs30_default)
        bias = float(np.median(y_train - pred_train))
        pred_test = pred_test_raw + bias
        rows.append(
            {
                "dataset": "knet",
                "target": "pga",
                "reference": name,
                "vs30_default_mps": vs30_default,
                "train_rows": int(len(train)),
                "test_rows": int(len(test)),
                "bias_log10": bias,
                "mae_log10_target": float(mean_absolute_error(y_test, pred_test)),
                "r2_log10_target": float(r2_score(y_test, pred_test)),
            }
        )
    return pd.DataFrame(rows).sort_values("mae_log10_target").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature-dir", type=Path, default=Path("work/ground_motion_balanced_station_10s"))
    parser.add_argument("--out", type=Path, default=Path("work/ground_motion_balanced_station_10s/knet_japan_gmm_reference.csv"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/knet_japan_gmm_reference_summary.md"))
    args = parser.parse_args()

    train = pd.read_csv(args.feature_dir / "knet_held_station_train_features.csv").dropna(subset=["target_log10_pga"])
    test = pd.read_csv(args.feature_dir / "knet_held_station_test_features.csv").dropna(subset=["target_log10_pga"])
    df = evaluate(train, test)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)

    best = df.iloc[0]
    combined_mae = 0.1112985036745596
    lines = [
        "# K-NET Japan GMM Reference Summary",
        "",
        "Date: 2026-06-18",
        "",
        "This screening reference evaluates OpenQuake Japanese or Japan-derived GMMs on the balanced held-station K-NET PGA split. Predictions use source distance as an Rrup proxy, missing Vs30 defaults, and train-set median bias correction.",
        "",
        f"Best candidate reference: {best['reference']}, MAE {best['mae_log10_target']:.3f}, R2 {best['r2_log10_target']:.3f}.",
        f"Current metadata plus early-waveform K-NET held-station MAE: {combined_mae:.3f}.",
        "",
        "Interpretation: this is a stronger classical screening check for K-NET than a single generic BooreEtAl2014 reference, while still limited by distance, Vs30, and tectonic-class approximations.",
        "",
        f"CSV: `{args.out}`",
        "",
    ]
    args.summary.write_text("\n".join(lines))
    print(df.to_string(index=False))
    print(f"wrote {args.out}")
    print(f"wrote {args.summary}")


if __name__ == "__main__":
    main()
