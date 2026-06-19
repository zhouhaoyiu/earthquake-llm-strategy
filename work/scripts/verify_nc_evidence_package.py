#!/usr/bin/env python3
"""Verify the current NC evidence package from generated artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import h5py
from PIL import Image
import pandas as pd


ROOT = Path(".")
REPORT = Path("outputs/nc_evidence_verification_report.md")
FIGURES = [
    "outputs/figures/figure1_dataset_task_matrix.png",
    "outputs/figures/figure2_early_window_performance.png",
    "outputs/figures/figure3_heldout_generalization.png",
    "outputs/figures/figure4_classical_uncertainty.png",
    "outputs/figures/figure5_residual_waveform_audit.png",
    "outputs/figures/figure6_phase_label_audit.png",
]
DOCS = [
    "outputs/nc_minimum_submission_package.md",
    "outputs/manuscript_scaffold_cross_dataset_early_window_residual_audit.md",
    "outputs/nc_evidence_packet_zh.md",
]
METHOD_SCRIPTS = [
    "work/scripts/convert_knet_bson.py",
    "work/scripts/build_unified_manifest.py",
    "work/scripts/run_ground_motion_baseline.py",
    "work/scripts/audit_early_window_peak_capture.py",
    "work/scripts/audit_knet_prepeak_subset.py",
    "work/scripts/run_ground_motion_heldout_baseline.py",
    "work/scripts/run_attenuation_reference.py",
    "work/scripts/audit_regional_gmm_readiness.py",
    "work/scripts/run_openquake_pga_reference.py",
    "work/scripts/run_knet_japan_gmm_reference.py",
    "work/scripts/run_conformal_intervals.py",
    "work/scripts/analyze_ground_motion_residuals.py",
    "work/scripts/stream_aq2009gm_full_validation.py",
    "work/scripts/build_esm_compact_features.py",
    "work/scripts/run_esm_compact_baseline.py",
    "work/scripts/run_pnw_accelerometer_peak_baseline.py",
    "work/scripts/build_predictability_boundary_table.py",
    "work/scripts/summarize_held_station_window_scan.py",
    "work/scripts/run_cross_region_waveform_transfer.py",
    "work/scripts/summarize_cross_region_window_scan.py",
]


def check(condition: bool, message: str, rows: list[str]) -> None:
    if not condition:
        raise AssertionError(message)
    rows.append(f"- PASS: {message}")


def approx(value: float, expected: float, tol: float = 0.05) -> bool:
    return abs(value - expected) <= tol


def main() -> None:
    rows: list[str] = [
        "# NC Evidence Verification Report",
        "",
        "Date: 2026-06-20",
        "",
        "This report verifies generated artifacts only. NC 60% remains an empirical target beyond this verifier.",
        "",
        "## Checks",
        "",
    ]

    unified = json.load(open("work/unified_manifest/unified_manifest_summary.json"))
    check(unified["rows"] == 2460425, "unified manifest has 2,460,425 rows", rows)
    check(unified["datasets"]["instancegm"]["ground_motion_rows"] == 1159223, "InstanceGM has 1,159,223 ground-motion rows", rows)
    check(unified["datasets"]["knet"]["rows"] == 22119, "K-NET has 22,119 unified records", rows)

    knet = json.load(open("work/knet_converted/knet_full_convert_report.json"))
    check(knet["input_dir"] == "/Users/yojironoda/Downloads/s7rk7bj3zn-1/knet_1530", "K-NET source is the approved Downloads/s7rk7bj3zn-1 path", rows)
    check(knet["complete_records"] == 22119 and knet["component_order"] == "ZNE", "K-NET conversion has 22,119 complete ZNE records", rows)

    provenance = Path("outputs/methods_provenance_table.md")
    check(provenance.exists() and provenance.stat().st_size > 0, "methods provenance table exists", rows)
    for script in METHOD_SCRIPTS:
        check(Path(script).exists(), f"method script exists: {script}", rows)

    risk_matrix = Path("outputs/nc_reviewer_risk_matrix.md")
    check(risk_matrix.exists() and risk_matrix.stat().st_size > 0, "NC reviewer risk matrix exists", rows)
    risk_text = risk_matrix.read_text()
    for phrase in [
        "10 s window",
        "group leakage",
        "distribution artifacts",
        "attenuation-shaped",
        "fully specified regional GMM",
        "AQ2009GM supplement",
        "PNW target official PGA",
        "Phase alignment",
        "calibrated under station shift",
        "physical causality",
        "NC 60%",
    ]:
        check(phrase in risk_text, f"reviewer risk matrix covers: {phrase}", rows)

    pnw_audit = Path("outputs/pnw_unit_provenance_audit.md")
    check(pnw_audit.exists() and pnw_audit.stat().st_size > 0, "PNW unit provenance audit exists", rows)
    with h5py.File("/Users/yojironoda/.seisbench/datasets/pnwaccelerometers/waveforms.hdf5", "r") as h5:
        data_format_keys = set(h5["data_format"].keys())
    check("component_order" in data_format_keys and "unit" not in data_format_keys, "PNWAccelerometers local HDF5 has component_order but no unit field", rows)

    aq_summary = Path("outputs/aq2009gm_full_stream_validation_summary.md")
    aq_figure = Path("outputs/figures/ground_motion_audit/aq2009gm_full_stream_panel.png")
    aq_summary_json = json.load(open("work/aq2009gm_full_stream_validation/aq2009gm_full_stream_summary.json"))
    aq_inventory = pd.read_csv("work/aq2009gm_full_stream_validation/chunk_inventory.csv")
    aq_comparison = pd.read_csv("work/aq2009gm_full_stream_validation/aq2009gm_full_stream_comparison.csv")
    chunk_manifest = [
        line.strip()
        for line in Path("/Users/yojironoda/.seisbench/datasets/aq2009gm/chunks").read_text().splitlines()
        if line.strip()
    ]
    check(aq_summary.exists() and aq_summary.stat().st_size > 0, "AQ2009GM full-manifest streaming summary exists", rows)
    check(aq_summary_json["chunk_count"] == len(chunk_manifest) == 254, "AQ2009GM streaming covers all 254 local manifest chunks", rows)
    check(len(aq_inventory) == 254 and (aq_inventory["errors"] == 0).all(), "AQ2009GM chunk inventory has 254 chunks and zero extraction errors", rows)
    check(aq_summary_json["valid_rows"] == 345226, "AQ2009GM streaming has 345,226 valid PGA/PGV records", rows)
    check(aq_summary_json["valid_events"] == 60310 and aq_summary_json["valid_stations"] == 66, "AQ2009GM streaming event/station counts match summary", rows)
    check(len(aq_comparison) == 18, "AQ2009GM full-manifest comparison has 18 rows across holdout/target/window combinations", rows)
    check(set(aq_comparison["holdout"]) == {"event", "station", "time"}, "AQ2009GM full-manifest includes held-event, held-station, and held-time splits", rows)
    check(set(aq_comparison["target"]) == {"pga", "pgv"}, "AQ2009GM full-manifest includes PGA and PGV targets", rows)
    check(set(aq_comparison["early_seconds"]) == {1.0, 3.0, 10.0}, "AQ2009GM full-manifest covers 1/3/10 s windows", rows)
    check((aq_comparison["group_overlap"] == 0).all(), "AQ2009GM full-manifest held-out group overlap is zero", rows)
    check((aq_comparison["mae_reduction_pct"] > 0).all(), "AQ2009GM full-manifest combined model improves over metadata-only for every row", rows)
    station_aq = aq_comparison[aq_comparison["holdout"] == "station"]
    check(station_aq["test_rows"].min() >= 10000 and station_aq["test_groups"].min() >= 20, "AQ2009GM full-manifest station split has 10,000 test rows and 20 held station groups", rows)
    check(aq_figure.exists() and aq_figure.stat().st_size > 0, "AQ2009GM full-manifest supplementary figure exists", rows)
    aq_im = Image.open(aq_figure)
    check(aq_im.width >= 1000 and aq_im.height >= 700, f"AQ2009GM full-manifest supplementary figure opens ({aq_im.width}x{aq_im.height})", rows)

    esm_feature_summary = Path("outputs/esm_compact_features_full_summary.md")
    esm_feature_path = Path("work/esm_compact_features_full/esm_compact_features.csv.gz")
    esm_feature_json = json.load(open("work/esm_compact_features_full/esm_compact_feature_summary.json"))
    check(esm_feature_summary.exists() and esm_feature_summary.stat().st_size > 0, "ESM compact feature summary exists", rows)
    check(esm_feature_path.exists() and esm_feature_path.stat().st_size > 0, "ESM compact feature table exists", rows)
    check(esm_feature_json["zip_files"] == 951, "ESM compact feature extraction covers 951 local zip packages", rows)
    check(esm_feature_json["feature_rows"] == 134250, "ESM compact feature table has 134,250 early-window rows", rows)
    check(esm_feature_json["events"] == 861 and esm_feature_json["stations"] == 1568, "ESM compact feature event/station counts match summary", rows)
    check(esm_feature_json["target_pga_nonmissing_rows"] == 134250, "ESM compact feature table has complete PGA targets", rows)
    check(esm_feature_json["target_pgv_nonmissing_rows"] == 134245 and esm_feature_json["target_pgv_missing_rows"] == 5, "ESM compact feature table records the five missing PGV window rows", rows)
    check(esm_feature_json["errors"] == 0, "ESM compact feature extraction has zero read errors", rows)
    esm_features = pd.read_csv(esm_feature_path)
    check(set(esm_features["early_seconds"]) == {1.0, 2.0, 3.0, 5.0, 10.0}, "ESM compact feature table covers 1/2/3/5/10 s windows", rows)
    check(esm_features["p_window_valid"].astype(bool).all(), "ESM compact feature table excludes invalid theoretical P windows", rows)
    check(pd.to_numeric(esm_features["target_pga"], errors="coerce").gt(0).all(), "ESM compact feature table has positive PGA targets", rows)
    esm_pgv = pd.to_numeric(esm_features["target_pgv"], errors="coerce")
    check(esm_pgv.dropna().gt(0).all() and int(esm_pgv.isna().sum()) == 5, "ESM compact feature table has positive nonmissing PGV targets and five missing PGV rows", rows)

    esm_heldout_summary = Path("outputs/esm_heldout_baseline_summary.md")
    esm_heldout_metrics = pd.read_csv("work/esm_heldout_baseline/esm_heldout_metrics.csv")
    esm_heldout_split = pd.read_csv("work/esm_heldout_baseline/esm_heldout_split_info.csv")
    check(esm_heldout_summary.exists() and esm_heldout_summary.stat().st_size > 0, "ESM held-out baseline summary exists", rows)
    check(len(esm_heldout_metrics) == 80, "ESM held-out baseline has 80 rows across holdout/window/target/feature-set combinations", rows)
    check(set(esm_heldout_metrics["early_seconds"]) == {1.0, 2.0, 3.0, 5.0, 10.0}, "ESM held-out baseline covers 1/2/3/5/10 s windows", rows)
    check(set(esm_heldout_metrics["holdout"]) == {"event", "station"}, "ESM held-out baseline includes held-event and held-station splits", rows)
    check((esm_heldout_metrics["group_overlap"] == 0).all() and (esm_heldout_split["group_overlap"] == 0).all(), "ESM held-out baseline group overlap is zero", rows)
    station_esm = esm_heldout_metrics[esm_heldout_metrics["holdout"] == "station"]
    median_esm = station_esm[station_esm["feature_set"] == "median"].set_index(["target", "early_seconds"])["mae_log10_target"]
    site_esm = station_esm[station_esm["feature_set"] == "p_waveform_distance_site"].set_index(["target", "early_seconds"])["mae_log10_target"]
    check((site_esm < median_esm).all(), "ESM held-station P+distance+site model improves over median for every target/window", rows)

    for fig in FIGURES:
        path = Path(fig)
        check(path.exists() and path.stat().st_size > 0, f"{fig} exists", rows)
        im = Image.open(path)
        check(im.width >= 1000 and im.height >= 700, f"{fig} opens as a nontrivial image ({im.width}x{im.height})", rows)

    fig2 = pd.read_csv("outputs/figure2_early_window_performance.csv")
    check(len(fig2) == 18 and set(fig2["window_s"]) == {1, 3, 10}, "Figure 2 table has 18 rows across 1/3/10 s windows", rows)
    check((fig2["mae_reduction_pct"] > 0).all(), "Figure 2 MAE reductions are positive for all tested rows", rows)
    k10 = fig2[(fig2["dataset"] == "knet") & (fig2["target"] == "pga") & (fig2["window_s"] == 10)].iloc[0]
    check(approx(k10["mae_reduction_pct"], 51.8), "Figure 2 K-NET 10 s PGA reduction matches reported value", rows)

    peak = pd.read_csv("outputs/early_window_peak_capture_audit.csv")
    check(len(peak) == 6, "early-window peak-capture audit has 6 dataset-window rows", rows)
    kpeak10 = peak[(peak["dataset"] == "knet") & (peak["window_s"] == 10)].iloc[0]
    ipeak10 = peak[(peak["dataset"] == "instancegm") & (peak["window_s"] == 10)].iloc[0]
    check(kpeak10["frac_ratio_ge_0p8"] > 0.9, "K-NET 10 s windows often contain target-scale PGA amplitudes", rows)
    check(ipeak10["ratio_median"] < 0.01, "InstanceGM early/PGA amplitude ratios are not directly comparable", rows)

    prepeak_path = Path("outputs/knet_prepeak_subset_audit.md")
    check(prepeak_path.exists() and prepeak_path.stat().st_size > 0, "K-NET pre-peak subset audit exists", rows)
    prepeak = pd.read_csv("outputs/knet_prepeak_subset_audit.csv")
    check(len(prepeak) == 9, "K-NET pre-peak subset audit has 9 rows across 3 thresholds and 3 windows", rows)
    check(set(prepeak["threshold"]) == {0.5, 0.8, 1.0}, "K-NET pre-peak subset audit includes 0.5/0.8/1.0 thresholds", rows)
    main_prepeak = prepeak[prepeak["threshold"] == 0.8]
    check(set(main_prepeak["window_s"]) == {1, 3, 10}, "K-NET pre-peak main threshold covers 1/3/10 s windows", rows)
    p1 = main_prepeak[main_prepeak["window_s"] == 1].iloc[0]
    p3 = main_prepeak[main_prepeak["window_s"] == 3].iloc[0]
    p10 = main_prepeak[main_prepeak["window_s"] == 10].iloc[0]
    check(p1["records"] >= 300 and p3["records"] >= 250, "K-NET 1 s and 3 s pre-peak subsets have enough records for audit interpretation", rows)
    check(p10["records"] >= 50, "K-NET 10 s pre-peak subset is present but small", rows)
    check((main_prepeak["combined_mae"] < main_prepeak["metadata_mae"]).all(), "K-NET pre-peak subsets improve over metadata-only", rows)
    check(p1["mae_reduction_pct"] > 10 and p3["mae_reduction_pct"] > 10, "K-NET 1 s and 3 s pre-peak reductions exceed 10%", rows)

    fig3 = pd.read_csv("outputs/figure3_heldout_generalization.csv")
    check(len(fig3) == 12, "Figure 3 table has 12 held-out rows", rows)
    check(set(fig3["holdout"]) == {"event", "station"}, "Figure 3 includes held-event and held-station splits", rows)
    check((fig3["group_overlap_metadata"] == 0).all() and (fig3["group_overlap_combined"] == 0).all(), "Figure 3 held-out group overlap is zero", rows)
    check((fig3["mae_reduction_pct"] > 0).all(), "Figure 3 MAE reductions are positive for every held-out target", rows)

    attenuation_summary = Path("outputs/attenuation_reference_summary.md")
    check(attenuation_summary.exists() and attenuation_summary.stat().st_size > 0, "attenuation-shaped reference summary exists", rows)
    attenuation = pd.read_csv("work/ground_motion_balanced_station_10s/attenuation_reference.csv")
    check(len(attenuation) == 6, "attenuation-shaped reference has 6 balanced held-station target rows", rows)
    gmm_ready_path = Path("outputs/regional_gmm_readiness_audit.md")
    check(gmm_ready_path.exists() and gmm_ready_path.stat().st_size > 0, "regional GMM readiness audit exists", rows)
    gmm_ready = pd.read_csv("outputs/regional_gmm_readiness_audit.csv")
    inst_train = gmm_ready[(gmm_ready["dataset"] == "instancegm") & (gmm_ready["split"] == "train")].iloc[0]
    inst_test = gmm_ready[(gmm_ready["dataset"] == "instancegm") & (gmm_ready["split"] == "test")].iloc[0]
    knet_train = gmm_ready[(gmm_ready["dataset"] == "knet") & (gmm_ready["split"] == "train")].iloc[0]
    check(inst_train["join_rows"] == inst_train["rows"] and inst_test["join_rows"] == inst_test["rows"], "InstanceGM GMM readiness audit joins all held-station records", rows)
    check(inst_train["vs30_frac"] == 1.0 and inst_test["vs30_frac"] == 1.0, "InstanceGM GMM readiness audit has complete Vs30 in this split", rows)
    check(inst_train["mechanism_frac"] < 0.05 and inst_test["mechanism_frac"] < 0.05, "InstanceGM focal-mechanism coverage is sparse for full GMM claims", rows)
    check(knet_train["vs30_frac"] == 0.0 and knet_train["mechanism_frac"] == 0.0, "K-NET lacks Vs30 and focal-mechanism fields in approved local data", rows)
    inst_vs30 = pd.read_csv("work/ground_motion_balanced_station_10s/instancegm_held_station_train_features.csv", usecols=["station_vs30_mps"])
    knet_vs30 = pd.read_csv("work/ground_motion_balanced_station_10s/knet_held_station_train_features.csv", usecols=["station_vs30_mps"])
    check(pd.to_numeric(inst_vs30["station_vs30_mps"], errors="coerce").notna().any(), "InstanceGM attenuation reference has Vs30 values available", rows)
    check(pd.to_numeric(knet_vs30["station_vs30_mps"], errors="coerce").notna().sum() == 0, "K-NET attenuation reference is not site-corrected because Vs30 is missing", rows)
    station = fig3[fig3["holdout"] == "station"][["dataset", "target", "combined_mae"]].copy()
    merged = attenuation.merge(station, on=["dataset", "target"], how="inner")
    check(len(merged) == 6, "attenuation reference aligns with all Figure 3 station targets", rows)
    check((merged["combined_mae"] < merged["mae_log10_target"]).all(), "combined model beats attenuation-shaped reference for all station targets", rows)

    fig4 = pd.read_csv("outputs/figure4_classical_uncertainty.csv")
    check(len(fig4) == 6, "Figure 4 table has 6 OpenQuake/conformal rows", rows)
    check((fig4["combined_mae"] < fig4["boore2014_mae"]).all(), "Figure 4 combined MAE is below Boore2014 for all rows", rows)
    check(fig4["coverage"].between(0, 1).all(), "Figure 4 conformal coverage values are valid probabilities", rows)

    boundary_path = Path("outputs/predictability_boundary_table.csv")
    boundary_summary = Path("outputs/predictability_boundary_summary.md")
    check(boundary_path.exists() and boundary_path.stat().st_size > 0, "predictability boundary table exists", rows)
    check(boundary_summary.exists() and boundary_summary.stat().st_size > 0, "predictability boundary summary exists", rows)
    boundary = pd.read_csv(boundary_path)
    check(len(boundary) == 6, "predictability boundary table has 6 main target rows", rows)
    check((boundary["held_event_group_overlap"] == 0).all(), "predictability boundary table preserves held-event zero overlap", rows)
    check((boundary["held_station_group_overlap"] == 0).all(), "predictability boundary table preserves held-station zero overlap", rows)
    check((boundary["robust_heldout_gain_pct"] > 0).all(), "predictability boundary table has positive robust held-out gains", rows)
    check(boundary["coverage_gap_to_90"].lt(0).any(), "predictability boundary table reports at least one conformal under-coverage case", rows)

    held_window_summary = Path("outputs/held_station_window_scan_summary.md")
    held_window_path = Path("work/held_station_window_scan.csv")
    held_window_figure = Path("outputs/figures/ground_motion_audit/held_station_window_scan.png")
    check(held_window_summary.exists() and held_window_summary.stat().st_size > 0, "held-station 1/2/3/5/10 window-scan summary exists", rows)
    check(held_window_path.exists() and held_window_path.stat().st_size > 0, "held-station 1/2/3/5/10 window-scan table exists", rows)
    check(held_window_figure.exists() and held_window_figure.stat().st_size > 0, "held-station 1/2/3/5/10 window-scan figure exists", rows)
    held_window_im = Image.open(held_window_figure)
    check(held_window_im.width >= 1000 and held_window_im.height >= 700, f"held-station window-scan figure opens ({held_window_im.width}x{held_window_im.height})", rows)
    held_window = pd.read_csv(held_window_path)
    check(set(held_window["window_s"]) == {1, 2, 3, 5, 10}, "held-station window scan covers 1/2/3/5/10 s windows", rows)
    check(held_window["mae_reduction_pct"].gt(0).all(), "held-station window scan has positive early-waveform gain for every row", rows)
    group_cols = [col for col in held_window.columns if col.startswith("group_overlap")]
    check(held_window[group_cols].fillna(0).eq(0).all().all(), "held-station window scan preserves zero group overlap", rows)

    transfer_summary = Path("outputs/cross_region_waveform_transfer_summary.md")
    transfer_metrics_path = Path("work/cross_region_waveform_transfer/cross_region_waveform_transfer_metrics.csv")
    transfer_boundary_path = Path("work/cross_region_waveform_transfer/cross_region_waveform_transfer_boundary.csv")
    transfer_split_path = Path("work/cross_region_waveform_transfer/cross_region_waveform_transfer_split_info.csv")
    transfer_figure = Path("outputs/figures/ground_motion_audit/cross_region_waveform_transfer_boundary.png")
    check(transfer_summary.exists() and transfer_summary.stat().st_size > 0, "cross-region waveform transfer summary exists", rows)
    check(transfer_metrics_path.exists() and transfer_metrics_path.stat().st_size > 0, "cross-region waveform transfer metrics exist", rows)
    check(transfer_boundary_path.exists() and transfer_boundary_path.stat().st_size > 0, "cross-region waveform transfer boundary table exists", rows)
    check(transfer_figure.exists() and transfer_figure.stat().st_size > 0, "cross-region waveform transfer boundary figure exists", rows)
    transfer_im = Image.open(transfer_figure)
    check(transfer_im.width >= 1000 and transfer_im.height >= 700, f"cross-region waveform transfer figure opens ({transfer_im.width}x{transfer_im.height})", rows)
    transfer_split = pd.read_csv(transfer_split_path)
    check(set(transfer_split["dataset"]) == {"instancegm", "knet", "aq2009gm"}, "cross-region transfer covers InstanceGM, K-NET, and AQ2009GM", rows)
    check((transfer_split["group_overlap"] == 0).all(), "cross-region transfer split group overlap is zero", rows)
    transfer = pd.read_csv(transfer_boundary_path)
    check(set(transfer["target"]) == {"pga", "pgv"}, "cross-region transfer covers PGA and PGV where available", rows)
    check((transfer["source_dataset"] != transfer["test_dataset"]).all(), "cross-region boundary table contains only cross-domain rows", rows)
    check((transfer["mae_ratio_vs_within_target"] > 1.0).all(), "cross-region transfer is worse than target-domain training for every cross-domain row", rows)
    direct_ratio = transfer[transfer["calibration"] == "source_only"]["mae_ratio_vs_within_target"].median()
    calibrated_ratio = transfer[transfer["calibration"] == "target_offset_calibrated"]["mae_ratio_vs_within_target"].median()
    check(direct_ratio > 2.0, "zero-shot cross-region transfer median penalty exceeds 2x target-domain MAE", rows)
    check(1.5 < calibrated_ratio < direct_ratio, "target-train offset calibration reduces but does not remove the cross-region penalty", rows)

    for window in [1, 2, 3, 5, 10]:
        esm_transfer_summary = Path(f"outputs/cross_region_waveform_transfer_esm_{window}s_summary.md")
        esm_transfer_metrics = Path(f"work/cross_region_waveform_transfer_esm_{window}s/cross_region_waveform_transfer_metrics.csv")
        esm_transfer_boundary = Path(f"work/cross_region_waveform_transfer_esm_{window}s/cross_region_waveform_transfer_boundary.csv")
        esm_transfer_split = Path(f"work/cross_region_waveform_transfer_esm_{window}s/cross_region_waveform_transfer_split_info.csv")
        esm_transfer_figure = Path(f"outputs/figures/ground_motion_audit/cross_region_waveform_transfer_esm_{window}s_boundary.png")
        check(esm_transfer_summary.exists() and esm_transfer_summary.stat().st_size > 0, f"ESM four-domain transfer {window}s summary exists", rows)
        check(esm_transfer_metrics.exists() and esm_transfer_metrics.stat().st_size > 0, f"ESM four-domain transfer {window}s metrics exist", rows)
        check(esm_transfer_boundary.exists() and esm_transfer_boundary.stat().st_size > 0, f"ESM four-domain transfer {window}s boundary table exists", rows)
        check(esm_transfer_figure.exists() and esm_transfer_figure.stat().st_size > 0, f"ESM four-domain transfer {window}s figure exists", rows)
        esm_transfer_im = Image.open(esm_transfer_figure)
        check(esm_transfer_im.width >= 1000 and esm_transfer_im.height >= 700, f"ESM four-domain transfer {window}s figure opens ({esm_transfer_im.width}x{esm_transfer_im.height})", rows)
        esm_split = pd.read_csv(esm_transfer_split)
        expected_domains = {"instancegm", "knet", "esm"} if window in {2, 5} else {"instancegm", "knet", "aq2009gm", "esm"}
        check(set(esm_split["dataset"]) == expected_domains, f"ESM transfer {window}s split covers expected domains", rows)
        check((esm_split["group_overlap"] == 0).all(), f"ESM four-domain transfer {window}s split group overlap is zero", rows)
        esm_boundary = pd.read_csv(esm_transfer_boundary)
        check((esm_boundary["source_dataset"] != esm_boundary["test_dataset"]).all(), f"ESM four-domain transfer {window}s boundary contains only cross-domain rows", rows)
        check((esm_boundary["mae_ratio_vs_within_target"] > 1.0).all(), f"ESM four-domain transfer {window}s rows remain worse than target-domain training", rows)
        if window == 10:
            esm_target = esm_boundary[
                (esm_boundary["test_dataset"] == "esm")
                & (esm_boundary["calibration"] == "target_offset_calibrated")
            ]
            best_esm = esm_target.sort_values("mae_log10_target").groupby("target").head(1).set_index("target")
            check(best_esm.loc["pga", "mae_ratio_vs_within_target"] > 2.0, "10 s external-to-ESM PGA transfer remains above 2x target-domain MAE after offset calibration", rows)
            check(best_esm.loc["pgv", "mae_ratio_vs_within_target"] > 1.5, "10 s external-to-ESM PGV transfer remains above 1.5x target-domain MAE after offset calibration", rows)

    window_summary = Path("outputs/cross_region_waveform_transfer_window_scan_summary.md")
    window_csv = Path("work/cross_region_waveform_transfer_window_scan.csv")
    window_figure = Path("outputs/figures/ground_motion_audit/cross_region_waveform_transfer_window_scan.png")
    check(window_summary.exists() and window_summary.stat().st_size > 0, "cross-region window-scan summary exists", rows)
    check(window_csv.exists() and window_csv.stat().st_size > 0, "cross-region window-scan table exists", rows)
    check(window_figure.exists() and window_figure.stat().st_size > 0, "cross-region window-scan figure exists", rows)
    window_im = Image.open(window_figure)
    check(window_im.width >= 1000 and window_im.height >= 700, f"cross-region window-scan figure opens ({window_im.width}x{window_im.height})", rows)
    window_scan = pd.read_csv(window_csv)
    check(set(window_scan["window_s"]) == {1, 3, 10}, "cross-region window-scan covers 1/3/10 s windows", rows)
    check((window_scan["mae_ratio_vs_within_target"] > 1.0).all(), "cross-region window-scan rows remain worse than target-domain training", rows)
    direct_window = window_scan[window_scan["calibration"] == "source_only"].groupby("window_s")["mae_ratio_vs_within_target"].median()
    calibrated_window = window_scan[window_scan["calibration"] == "target_offset_calibrated"].groupby("window_s")["mae_ratio_vs_within_target"].median()
    check(direct_window.loc[1] < direct_window.loc[3] < direct_window.loc[10], "zero-shot transfer penalty increases from 1 s to 10 s", rows)
    check(calibrated_window.loc[1] < calibrated_window.loc[3] < calibrated_window.loc[10], "offset-calibrated transfer penalty increases from 1 s to 10 s", rows)

    japan = pd.read_csv("work/ground_motion_balanced_station_10s/knet_japan_gmm_reference.csv")
    knet_station = pd.read_csv("outputs/figure3_heldout_generalization.csv")
    knet_combined = knet_station[
        (knet_station["dataset"] == "knet")
        & (knet_station["target"] == "pga")
        & (knet_station["holdout"] == "station")
    ]["combined_mae"].iloc[0]
    check(len(japan) == 8, "K-NET Japan GMM screening has 8 candidate references", rows)
    check(knet_combined < japan["mae_log10_target"].min(), "K-NET early-waveform model beats best Japan GMM screening reference", rows)

    fig6 = pd.read_csv("outputs/figure6_phase_label_audit.csv")
    check(len(fig6) == 16, "Figure 6 table has 16 rows: 4 datasets x 2 models x P/S", rows)
    check(set(fig6["dataset"]) == {"stead", "instancegm", "iquique", "knet"}, "Figure 6 covers STEAD, InstanceGM, Iquique, and K-NET", rows)

    for doc in DOCS:
        text = Path(doc).read_text()
        for idx in range(1, 7):
            check(f"figure{idx}_" in text, f"{doc} references Figure {idx}", rows)
        check("AQ2009GM" in text, f"{doc} references AQ2009GM supplementary check", rows)
    article = Path("outputs/nc_article_draft_v1.md").read_text()
    for phrase in [
        "Figure 1. Cross-dataset waveform-task benchmark",
        "Figure 6. Phase-label transfer audit",
        "2,460,425 manifest records",
        "35.5% for InstanceGM PGA",
        "52.6% for InstanceGM PGV",
        "49.9% for K-NET PGA",
        "0.925 coverage for K-NET PGA",
        "The retained AQ2009GM evidence consists of compact feature tables",
        "ESM provides an external European strong-motion check",
        "theoretical P-onset estimate",
        "2.53x for PGA and 1.58x for PGV",
    ]:
        check(phrase in article, f"article draft contains bounded claim: {phrase}", rows)

    rows.extend(
        [
            "",
            "## Current Acceptance-Probability Status",
            "",
            "The verified package supports the current NC submission story: cross-dataset early waveform information, empirical predictability-boundary table, cross-region waveform-transfer boundary, K-NET pre-peak subset auditing, held-out generalization, attenuation-shaped and OpenQuake references, K-NET Japanese GMM screening, regional-GMM readiness auditing, conformal uncertainty, residual auditing, phase-label auditing, full-manifest AQ2009GM feature-table validation, and ESM European strong-motion compact-feature validation.",
            "",
            "The remaining gap is empirical: a fully specified regional GMM comparison, ESM P-onset auditing, or a stronger physical residual mechanism would be needed before claiming a high-confidence NC route.",
            "",
        ]
    )
    REPORT.write_text("\n".join(rows))
    print(f"wrote {REPORT}")


if __name__ == "__main__":
    main()
