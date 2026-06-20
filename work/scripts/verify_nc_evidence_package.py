#!/usr/bin/env python3
"""Verify the current NC evidence package from generated artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

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
EXTENDED_FIGURES = [
    "outputs/figures/extended_waveform_case_audit.png",
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
    "work/scripts/audit_matched_station_gain.py",
    "work/scripts/audit_held_station_bootstrap_ci.py",
    "work/scripts/audit_held_station_tail.py",
    "work/scripts/run_attenuation_reference.py",
    "work/scripts/audit_regional_gmm_readiness.py",
    "work/scripts/run_openquake_pga_reference.py",
    "work/scripts/run_knet_japan_gmm_reference.py",
    "work/scripts/run_conformal_intervals.py",
    "work/scripts/analyze_ground_motion_residuals.py",
    "work/scripts/stream_aq2009gm_full_validation.py",
    "work/scripts/build_esm_compact_features.py",
    "work/scripts/audit_esm_p_onset_sensitivity.py",
    "work/scripts/audit_esm_waveform_p_pick_spotcheck.py",
    "work/scripts/run_esm_compact_baseline.py",
    "work/scripts/run_pnw_accelerometer_peak_baseline.py",
    "work/scripts/build_predictability_boundary_table.py",
    "work/scripts/summarize_held_station_window_scan.py",
    "work/scripts/run_cross_region_waveform_transfer.py",
    "work/scripts/summarize_cross_region_window_scan.py",
    "work/scripts/run_nc_boundary_sensitivity.py",
    "work/scripts/build_nc_core_boundary_figure.py",
    "work/scripts/redraw_nc_main_figures.py",
    "work/scripts/audit_nc_figure_style.py",
    "work/scripts/build_figure5_source_data.py",
    "work/scripts/build_nc_source_data_workbook.mjs",
]
SOURCE_DATA_SHEETS = {
    "README",
    "Fig1_TaskMatrix",
    "Fig2_EarlyWindow",
    "Fig3_Heldout",
    "Fig3_BootstrapCI",
    "Fig3_TailAudit",
    "Fig4_ClassicalUnc",
    "Fig4_CalSize",
    "Fig5_Residuals",
    "Fig6_PhaseAudit",
    "Fig7_Boundary",
    "SI_FeatureGroups",
    "SI_ESM_Onset",
    "SI_ESM_Spotcheck",
    "SI_EarlyPeak",
    "SI_PhaseTable",
}


def check(condition: bool, message: str, rows: list[str]) -> None:
    if not condition:
        raise AssertionError(message)
    rows.append(f"- PASS: {message}")


def approx(value: float, expected: float, tol: float = 0.05) -> bool:
    return abs(value - expected) <= tol


def xlsx_sheet_names(path: Path) -> set[str]:
    with ZipFile(path) as zf:
        root = ET.fromstring(zf.read("xl/workbook.xml"))
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    return {sheet.attrib["name"] for sheet in root.findall(".//x:sheet", ns)}


def file_contains_casefold(path: Path, needle: str) -> bool:
    if path.suffix == ".xlsx":
        with ZipFile(path) as zf:
            data = b"".join(zf.read(name) for name in zf.namelist())
    else:
        data = path.read_bytes()
    return needle.lower().encode() in data.lower()


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
    provenance_text = provenance.read_text()
    check("Core boundary synthesis" in provenance_text, "methods provenance table covers core boundary synthesis", rows)
    check("Boundary sensitivity checks" in provenance_text, "methods provenance table covers boundary sensitivity checks", rows)
    check("ESM P-onset sensitivity audit" in provenance_text, "methods provenance table covers ESM P-onset sensitivity audit", rows)
    check("ESM waveform P-onset spot audit" in provenance_text, "methods provenance table covers ESM waveform P-onset spot audit", rows)
    check("Matched held-station gain audit" in provenance_text, "methods provenance table covers matched held-station gain audit", rows)
    check("Held-station bootstrap CI audit" in provenance_text, "methods provenance table covers held-station bootstrap CI audit", rows)
    check("Held-station strong-tail audit" in provenance_text, "methods provenance table covers held-station strong-tail audit", rows)
    check("Uncertainty boundary note" in provenance_text, "methods provenance table covers uncertainty boundary note", rows)
    check("Regional GMM boundary note" in provenance_text, "methods provenance table covers regional GMM boundary note", rows)
    check("Main figure redraw and style audit" in provenance_text, "methods provenance table covers main figure redraw and style audit", rows)
    check("Next experiment decision" in provenance_text, "methods provenance table covers next experiment decision", rows)
    for script in METHOD_SCRIPTS:
        check(Path(script).exists(), f"method script exists: {script}", rows)

    risk_matrix = Path("outputs/nc_reviewer_risk_matrix.md")
    check(risk_matrix.exists() and risk_matrix.stat().st_size > 0, "NC reviewer risk matrix exists", rows)
    risk_text = risk_matrix.read_text()
    for phrase in [
        "10 s window",
        "group leakage",
        "distribution artifacts",
        "matched-support audit",
        "source-path support",
        "sampling stability",
        "strong-tail",
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

    aq25_summary = Path("outputs/aq2009gm_full_stream_validation_2s5s_summary.md")
    aq25_figure = Path("outputs/figures/ground_motion_audit/aq2009gm_full_stream_2s5s_panel.png")
    aq25_summary_json = json.load(open("work/aq2009gm_full_stream_validation_2s5s/aq2009gm_full_stream_summary.json"))
    aq25_inventory = pd.read_csv("work/aq2009gm_full_stream_validation_2s5s/chunk_inventory.csv")
    aq25_comparison = pd.read_csv("work/aq2009gm_full_stream_validation_2s5s/aq2009gm_full_stream_comparison.csv")
    check(aq25_summary.exists() and aq25_summary.stat().st_size > 0, "AQ2009GM 2/5 s streaming summary exists", rows)
    check(aq25_summary_json["chunk_count"] == len(chunk_manifest) == 254, "AQ2009GM 2/5 s streaming covers all 254 local manifest chunks", rows)
    check(len(aq25_inventory) == 254 and (aq25_inventory["errors"] == 0).all(), "AQ2009GM 2/5 s chunk inventory has 254 chunks and zero extraction errors", rows)
    check(aq25_summary_json["valid_rows"] == 345226, "AQ2009GM 2/5 s streaming has 345,226 valid PGA/PGV records", rows)
    check(len(aq25_comparison) == 12, "AQ2009GM 2/5 s comparison has 12 rows across holdout/target/window combinations", rows)
    check(set(aq25_comparison["early_seconds"]) == {2.0, 5.0}, "AQ2009GM 2/5 s full-manifest covers 2/5 s windows", rows)
    check((aq25_comparison["group_overlap"] == 0).all(), "AQ2009GM 2/5 s held-out group overlap is zero", rows)
    check((aq25_comparison["mae_reduction_pct"] > 0).all(), "AQ2009GM 2/5 s combined model improves over metadata-only for every row", rows)
    check(aq25_figure.exists() and aq25_figure.stat().st_size > 0, "AQ2009GM 2/5 s supplementary figure exists", rows)
    aq25_im = Image.open(aq25_figure)
    check(aq25_im.width >= 1000 and aq25_im.height >= 700, f"AQ2009GM 2/5 s supplementary figure opens ({aq25_im.width}x{aq25_im.height})", rows)

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

    esm_onset_summary = Path("outputs/esm_p_onset_sensitivity_audit.md")
    esm_onset_path = Path("outputs/esm_p_onset_sensitivity_audit.csv")
    check(esm_onset_summary.exists() and esm_onset_summary.stat().st_size > 0, "ESM P-onset sensitivity summary exists", rows)
    check(esm_onset_path.exists() and esm_onset_path.stat().st_size > 0, "ESM P-onset sensitivity table exists", rows)
    esm_onset = pd.read_csv(esm_onset_path)
    check(len(esm_onset) == 15, "ESM P-onset sensitivity table has 15 rows across 3 Vp values and 5 windows", rows)
    check(set(esm_onset["vp_km_s"]) == {5.5, 6.0, 6.5}, "ESM P-onset sensitivity covers Vp 5.5/6.0/6.5 km/s", rows)
    check(set(esm_onset["window_s"]) == {1.0, 2.0, 3.0, 5.0, 10.0}, "ESM P-onset sensitivity covers 1/2/3/5/10 s windows", rows)
    check(esm_onset["valid_fraction"].min() > 0.99, "ESM P-onset retained-window validity remains above 0.99", rows)
    esm_vp55 = esm_onset[esm_onset["vp_km_s"] == 5.5]["delta_vs_6s_median"].median()
    esm_vp65 = esm_onset[esm_onset["vp_km_s"] == 6.5]["delta_vs_6s_median"].median()
    check(esm_vp55 > 2.0 and esm_vp65 < -2.0, "ESM P-onset sensitivity records multi-second timing shifts for plausible Vp values", rows)

    esm_spot_summary = Path("outputs/esm_waveform_p_pick_spotcheck.md")
    esm_spot_path = Path("outputs/esm_waveform_p_pick_spotcheck.csv")
    esm_spot_json = Path("outputs/esm_waveform_p_pick_spotcheck.json")
    esm_spot_figure = Path("outputs/figures/ground_motion_audit/esm_waveform_p_pick_spotcheck.png")
    check(esm_spot_summary.exists() and esm_spot_summary.stat().st_size > 0, "ESM waveform onset-proxy spot-audit summary exists", rows)
    check(esm_spot_path.exists() and esm_spot_path.stat().st_size > 0, "ESM waveform onset-proxy spot-audit table exists", rows)
    check(esm_spot_json.exists() and esm_spot_json.stat().st_size > 0, "ESM waveform onset-proxy spot-audit JSON exists", rows)
    check(esm_spot_figure.exists() and esm_spot_figure.stat().st_size > 0, "ESM waveform onset-proxy spot-audit figure exists", rows)
    esm_spot_im = Image.open(esm_spot_figure)
    check(esm_spot_im.width >= 1000 and esm_spot_im.height >= 700, f"ESM waveform onset-proxy spot-audit figure opens ({esm_spot_im.width}x{esm_spot_im.height})", rows)
    esm_spot = pd.read_csv(esm_spot_path)
    check(len(esm_spot) == 200, "ESM waveform onset-proxy spot audit has 200 sampled records", rows)
    check(esm_spot["detected"].astype(bool).sum() >= 100, "ESM waveform onset-proxy spot audit detects at least 100 records", rows)
    hi = esm_spot[esm_spot["high_confidence"].fillna(False).astype(bool)]
    check(len(hi) >= 80, "ESM waveform onset-proxy spot audit has at least 80 high-confidence records", rows)
    check(hi["abs_delta_s"].median() < 1.5, "ESM high-confidence onset proxies have median absolute offset below 1.5 s", rows)
    check(hi["abs_delta_s"].quantile(0.95) < 5.0, "ESM high-confidence onset proxies have q95 absolute offset below 5 s", rows)

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
    for fig in EXTENDED_FIGURES:
        path = Path(fig)
        check(path.exists() and path.stat().st_size > 0, f"{fig} exists", rows)
        im = Image.open(path)
        check(im.width >= 1000 and im.height >= 1000, f"{fig} opens as an extended audit image ({im.width}x{im.height})", rows)

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

    matched_summary_path = Path("outputs/matched_station_gain_audit_summary.md")
    matched_metrics_path = Path("work/ground_motion_balanced_station_10s/matched_station_gain_audit.csv")
    matched_compact_path = Path("work/ground_motion_balanced_station_10s/matched_station_gain_audit_summary.csv")
    matched_figure = Path("outputs/figures/ground_motion_audit/matched_station_gain_audit.png")
    check(matched_summary_path.exists() and matched_summary_path.stat().st_size > 0, "matched held-station gain audit summary exists", rows)
    check(matched_metrics_path.exists() and matched_metrics_path.stat().st_size > 0, "matched held-station gain audit metrics exist", rows)
    check(matched_compact_path.exists() and matched_compact_path.stat().st_size > 0, "matched held-station gain audit compact table exists", rows)
    check(matched_figure.exists() and matched_figure.stat().st_size > 0, "matched held-station gain audit figure exists", rows)
    matched_im = Image.open(matched_figure)
    check(matched_im.width >= 1000 and matched_im.height >= 700, f"matched held-station gain audit figure opens ({matched_im.width}x{matched_im.height})", rows)
    matched = pd.read_csv(matched_compact_path)
    source_path_scope = matched[matched["scope"] == "source_path_support"]
    matched_scope = matched[matched["scope"] == "matched_train_support"]
    check(len(source_path_scope) == 6, "matched held-station gain audit has 6 source-path support target rows", rows)
    check(source_path_scope["retained_fraction"].min() >= 0.80, "source-path support audit retains at least 80% of test rows for every target", rows)
    check((source_path_scope["mae_reduction_pct"] > 0).all(), "source-path support audit keeps positive early-waveform gains for every target", rows)
    check(len(matched_scope) == 6, "matched held-station gain audit has 6 matched target rows", rows)
    check(matched_scope["retained_fraction"].min() >= 0.70, "matched held-station gain audit retains at least 70% of test rows for every target", rows)
    check((matched_scope["mae_reduction_pct"] > 0).all(), "matched held-station gain audit keeps positive early-waveform gains for every target", rows)

    bootstrap_summary_path = Path("outputs/held_station_bootstrap_ci_summary.md")
    bootstrap_metrics_path = Path("work/ground_motion_balanced_station_10s/held_station_bootstrap_ci.csv")
    bootstrap_figure = Path("outputs/figures/ground_motion_audit/held_station_bootstrap_ci.png")
    check(bootstrap_summary_path.exists() and bootstrap_summary_path.stat().st_size > 0, "held-station bootstrap CI summary exists", rows)
    check(bootstrap_metrics_path.exists() and bootstrap_metrics_path.stat().st_size > 0, "held-station bootstrap CI metrics exist", rows)
    check(bootstrap_figure.exists() and bootstrap_figure.stat().st_size > 0, "held-station bootstrap CI figure exists", rows)
    bootstrap_im = Image.open(bootstrap_figure)
    check(bootstrap_im.width >= 1000 and bootstrap_im.height >= 700, f"held-station bootstrap CI figure opens ({bootstrap_im.width}x{bootstrap_im.height})", rows)
    bootstrap = pd.read_csv(bootstrap_metrics_path)
    check(len(bootstrap) == 6, "held-station bootstrap CI has 6 target rows", rows)
    check((bootstrap["observed_reduction_pct"] > 0).all(), "held-station bootstrap CI observed reductions are positive", rows)
    check((bootstrap["ci95_low_pct"] > 0).all(), "held-station bootstrap CI lower bounds are positive for every target", rows)
    check((bootstrap["bootstrap_p_le_zero"] <= 0.001).all(), "held-station bootstrap CI has near-zero nonpositive-gain bootstrap mass", rows)

    tail_summary_path = Path("outputs/held_station_tail_audit_summary.md")
    tail_metrics_path = Path("work/ground_motion_balanced_station_10s/held_station_tail_audit.csv")
    tail_figure = Path("outputs/figures/ground_motion_audit/held_station_tail_audit.png")
    check(tail_summary_path.exists() and tail_summary_path.stat().st_size > 0, "held-station strong-tail audit summary exists", rows)
    check(tail_metrics_path.exists() and tail_metrics_path.stat().st_size > 0, "held-station strong-tail audit metrics exist", rows)
    check(tail_figure.exists() and tail_figure.stat().st_size > 0, "held-station strong-tail audit figure exists", rows)
    tail_im = Image.open(tail_figure)
    check(tail_im.width >= 1000 and tail_im.height >= 700, f"held-station strong-tail audit figure opens ({tail_im.width}x{tail_im.height})", rows)
    tail = pd.read_csv(tail_metrics_path)
    check(len(tail) == 24, "held-station strong-tail audit has 24 rows across targets, tails, and feature sets", rows)
    tail_pivot = tail.pivot_table(
        index=["dataset", "target", "tail_quantile"],
        columns="feature_set",
        values="mae_log10_target",
        aggfunc="first",
    )
    check((tail_pivot["metadata_plus_early_waveform"] < tail_pivot["metadata_only"]).all(), "held-station strong-tail MAE improves for every target-tail subset", rows)
    tail_under = tail.pivot_table(
        index=["dataset", "target", "tail_quantile"],
        columns="feature_set",
        values="under_factor2_rate",
        aggfunc="first",
    )
    check((tail_under["metadata_plus_early_waveform"] > tail_under["metadata_only"]).any(), "held-station strong-tail audit preserves at least one underprediction boundary case", rows)

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

    for window in [2, 5]:
        aq_esm_summary = Path(f"outputs/cross_region_waveform_transfer_aq_esm_{window}s_summary.md")
        aq_esm_metrics = Path(f"work/cross_region_waveform_transfer_aq_esm_{window}s/cross_region_waveform_transfer_metrics.csv")
        aq_esm_boundary = Path(f"work/cross_region_waveform_transfer_aq_esm_{window}s/cross_region_waveform_transfer_boundary.csv")
        aq_esm_split = Path(f"work/cross_region_waveform_transfer_aq_esm_{window}s/cross_region_waveform_transfer_split_info.csv")
        aq_esm_figure = Path(f"outputs/figures/ground_motion_audit/cross_region_waveform_transfer_aq_esm_{window}s_boundary.png")
        check(aq_esm_summary.exists() and aq_esm_summary.stat().st_size > 0, f"AQ+ESM four-domain transfer {window}s summary exists", rows)
        check(aq_esm_metrics.exists() and aq_esm_metrics.stat().st_size > 0, f"AQ+ESM four-domain transfer {window}s metrics exist", rows)
        check(aq_esm_boundary.exists() and aq_esm_boundary.stat().st_size > 0, f"AQ+ESM four-domain transfer {window}s boundary table exists", rows)
        check(aq_esm_figure.exists() and aq_esm_figure.stat().st_size > 0, f"AQ+ESM four-domain transfer {window}s figure exists", rows)
        aq_esm_im = Image.open(aq_esm_figure)
        check(aq_esm_im.width >= 1000 and aq_esm_im.height >= 700, f"AQ+ESM four-domain transfer {window}s figure opens ({aq_esm_im.width}x{aq_esm_im.height})", rows)
        aq_esm_split_df = pd.read_csv(aq_esm_split)
        check(set(aq_esm_split_df["dataset"]) == {"instancegm", "knet", "aq2009gm", "esm"}, f"AQ+ESM transfer {window}s split covers all four domains", rows)
        check((aq_esm_split_df["group_overlap"] == 0).all(), f"AQ+ESM four-domain transfer {window}s split group overlap is zero", rows)
        aq_esm_boundary_df = pd.read_csv(aq_esm_boundary)
        check((aq_esm_boundary_df["source_dataset"] != aq_esm_boundary_df["test_dataset"]).all(), f"AQ+ESM four-domain transfer {window}s boundary contains only cross-domain rows", rows)
        check((aq_esm_boundary_df["mae_ratio_vs_within_target"] > 1.0).all(), f"AQ+ESM four-domain transfer {window}s rows remain worse than target-domain training", rows)

    boundary_summary = Path("outputs/nc_boundary_sensitivity_summary.md")
    conformal_path = Path("work/nc_boundary_sensitivity/conformal_boundary.csv")
    tail_path = Path("work/nc_boundary_sensitivity/tail_underprediction.csv")
    robust_path = Path("work/nc_boundary_sensitivity/seed_robustness.csv")
    check(boundary_summary.exists() and boundary_summary.stat().st_size > 0, "NC boundary sensitivity summary exists", rows)
    conformal = pd.read_csv(conformal_path)
    tail = pd.read_csv(tail_path)
    robust = pd.read_csv(robust_path)
    check(len(conformal) == 258, "NC boundary conformal table has expected rows", rows)
    check(len(tail) == 516, "NC strong-motion tail table has expected rows", rows)
    check(len(robust) == 8, "NC three-seed robustness table has expected rows", rows)
    coverage = conformal.groupby(["early_seconds", "mode"])["coverage90"].median()
    check(coverage.loc[(2.0, "target_domain")] > 0.88 and coverage.loc[(5.0, "target_domain")] > 0.88, "target-domain conformal coverage is near nominal", rows)
    check(coverage.loc[(2.0, "zero_shot_source_conformal")] < 0.55 and coverage.loc[(5.0, "zero_shot_source_conformal")] < 0.40, "source-domain conformal transfer under-covers target domains", rows)
    check(coverage.loc[(2.0, "target_offset_conformal")] > 0.88 and coverage.loc[(5.0, "target_offset_conformal")] > 0.88, "target-offset conformal transfer restores near-nominal coverage", rows)
    top5 = tail[tail["tail_quantile"].eq(0.95)].groupby(["early_seconds", "mode"])["under_factor2_rate"].median()
    check(top5.loc[(2.0, "target_domain")] > top5.loc[(5.0, "target_domain")], "5 s reduces target-domain top-tail underprediction relative to 2 s", rows)
    offset_robust = robust[robust["mode"].eq("target_offset_conformal")]
    check(((offset_robust["ratio_max"] - offset_robust["ratio_min"]) < 0.12).all(), "offset-calibrated transfer penalties are stable across three seeds", rows)

    core_summary = Path("outputs/nc_core_predictability_boundary_summary.md")
    core_table_path = Path("outputs/nc_core_predictability_boundary_table.csv")
    core_figure = Path("outputs/figures/nc_core_predictability_boundary.png")
    check(core_summary.exists() and core_summary.stat().st_size > 0, "NC core predictability-boundary summary exists", rows)
    check(core_table_path.exists() and core_table_path.stat().st_size > 0, "NC core predictability-boundary table exists", rows)
    check(core_figure.exists() and core_figure.stat().st_size > 0, "NC core predictability-boundary figure exists", rows)
    core_im = Image.open(core_figure)
    check(core_im.width >= 1000 and core_im.height >= 700, f"NC core predictability-boundary figure opens ({core_im.width}x{core_im.height})", rows)
    core = pd.read_csv(core_table_path)
    check(set(core["window_s"]) == {1, 2, 3, 5, 10}, "NC core boundary table covers 1/2/3/5/10 s windows", rows)
    check(core["main_held_station_gain_pct"].gt(0).all(), "NC core boundary table has positive main held-station gains", rows)
    check(core["aq_station_gain_pct"].gt(0).all(), "NC core boundary table has positive AQ station gains", rows)
    check(core["zero_shot_transfer_ratio"].is_monotonic_increasing, "NC core boundary zero-shot transfer penalty increases with window length", rows)
    check(core["offset_transfer_ratio"].is_monotonic_increasing, "NC core boundary offset transfer penalty increases with window length", rows)
    core_by_window = core.set_index("window_s")
    check(core_by_window.loc[5, "zero_shot_conformal_coverage"] < core_by_window.loc[2, "zero_shot_conformal_coverage"], "NC core boundary source conformal coverage worsens from 2 s to 5 s", rows)
    check(core_by_window.loc[5, "target_domain_top5_under_factor2_rate"] < core_by_window.loc[2, "target_domain_top5_under_factor2_rate"], "NC core boundary target-domain top-tail underprediction improves from 2 s to 5 s", rows)

    formal_methods = Path("outputs/nc_methods_formal_draft.md")
    uncertainty_note = Path("outputs/nc_uncertainty_boundary_note.md")
    gmm_boundary_note = Path("outputs/regional_gmm_boundary_note.md")
    next_decision = Path("outputs/nc_next_experiment_decision.md")
    figure_style_summary = Path("outputs/nc_figure_style_audit.md")
    figure_style_path = Path("outputs/nc_figure_style_audit.csv")
    figure_contact = Path("outputs/figures/nc_main_figure_contact_sheet.png")
    check(formal_methods.exists() and formal_methods.stat().st_size > 0, "formal NC Methods draft exists", rows)
    formal_text = formal_methods.read_text()
    for phrase in ["Data Sources", "Early-Window Features", "Uncertainty and Boundary Analysis", "Classical References"]:
        check(phrase in formal_text, f"formal NC Methods draft covers: {phrase}", rows)
    check(uncertainty_note.exists() and uncertainty_note.stat().st_size > 0, "NC uncertainty boundary note exists", rows)
    check("exchangeability" in uncertainty_note.read_text().lower(), "NC uncertainty boundary note states exchangeability condition", rows)
    check(gmm_boundary_note.exists() and gmm_boundary_note.stat().st_size > 0, "regional GMM boundary note exists", rows)
    check("fully specified regional" in gmm_boundary_note.read_text(), "regional GMM boundary note limits full regional GMM claims", rows)
    check(next_decision.exists() and next_decision.stat().st_size > 0, "NC next experiment decision note exists", rows)
    next_text = next_decision.read_text()
    check("spot audit is now complete" in next_text, "NC next experiment decision marks ESM waveform onset audit complete", rows)
    check("Defer" in next_text and "regional GMPE/GMM" in next_text, "NC next experiment decision defers full regional GMPE/GMM", rows)
    check(figure_style_summary.exists() and figure_style_summary.stat().st_size > 0, "NC figure style audit summary exists", rows)
    check(figure_style_path.exists() and figure_style_path.stat().st_size > 0, "NC figure style audit table exists", rows)
    figure_style = pd.read_csv(figure_style_path)
    check(len(figure_style) == 7 and set(figure_style["figure"]) == {f"Figure {idx}" for idx in range(1, 8)}, "NC figure style audit covers Figures 1-7", rows)
    check((figure_style["width_px"] >= 2000).all(), "NC figure style audit confirms all main figures exceed 2000 px width", rows)
    check(figure_contact.exists() and figure_contact.stat().st_size > 0, "NC main figure contact sheet exists", rows)
    contact_im = Image.open(figure_contact)
    check(contact_im.width >= 1000 and contact_im.height >= 700, f"NC main figure contact sheet opens ({contact_im.width}x{contact_im.height})", rows)

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

    fig5_source = pd.read_csv("outputs/figure5_residual_diagnostic_source_data.csv")
    check(len(fig5_source) == 329, "Figure 5 residual source table has 329 panel-metric rows", rows)
    check(
        set(fig5_source["panel"]) == {"A_error_reduction", "B_knet_distance", "C_instancegm_depth", "D_instancegm_early_amp"},
        "Figure 5 residual source table covers all four diagnostic panels",
        rows,
    )
    source_workbook = Path("outputs/source_data/nc_source_data_v1.xlsx")
    source_manifest = Path("outputs/source_data/nc_source_data_manifest.md")
    check(source_workbook.exists() and source_workbook.stat().st_size > 100_000, "NC source-data workbook exists", rows)
    check(source_manifest.exists() and source_manifest.stat().st_size > 0, "NC source-data manifest exists", rows)
    check(xlsx_sheet_names(source_workbook) == SOURCE_DATA_SHEETS, "NC source-data workbook has the expected 16 sheets", rows)
    manifest_text = source_manifest.read_text()
    check("Fig5_Residuals" in manifest_text and "pending" not in manifest_text.lower(), "NC source-data manifest includes Figure 5 and no pending status", rows)
    for deliverable in [
        source_manifest,
        source_workbook,
        Path("outputs/figure5_residual_diagnostic_source_data.csv"),
        Path("outputs/nc_minimum_submission_package.md"),
        Path("outputs/nc_supplementary_information_v1.md"),
    ]:
        check(not file_contains_casefold(deliverable, "co" + "dex"), f"{deliverable} has no agent-marker text", rows)

    for doc in DOCS:
        text = Path(doc).read_text()
        for idx in range(1, 7):
            check(f"figure{idx}_" in text, f"{doc} references Figure {idx}", rows)
        check("AQ2009GM" in text, f"{doc} references AQ2009GM supplementary check", rows)
        check("ESM" in text and "P-onset" in text, f"{doc} references ESM P-onset boundary", rows)
        check("esm_waveform_p_pick_spotcheck" in text, f"{doc} references ESM waveform onset-proxy spot audit", rows)
        check("matched_station_gain_audit" in text, f"{doc} references matched held-station gain audit", rows)
        check("held_station_bootstrap_ci" in text, f"{doc} references held-station bootstrap CI audit", rows)
        check("held_station_tail_audit" in text, f"{doc} references held-station strong-tail audit", rows)
        check("extended_waveform_case_audit" in text, f"{doc} references extended waveform case audit", rows)
        check("nc_core_predictability_boundary" in text, f"{doc} references Figure 7 core boundary synthesis", rows)
    article = Path("outputs/nc_article_draft_v1.md").read_text()
    for phrase in [
        "Figure 1. Cross-Dataset Waveform-Task Benchmark",
        "Figure 6. Phase-Label Transfer Audit",
        "Figure 7. Predictability-Boundary Synthesis",
        "2,460,425 manifest records",
        "35.5% for InstanceGM PGA",
        "52.6% for InstanceGM PGV",
        "49.9% for K-NET PGA",
        "0.925 conformal coverage",
        "retained feature tables contain 345,226 valid PGA/PGV records",
        "ESM provides an external European strong-motion check",
        "A Vp sensitivity audit",
        "waveform-envelope onset-proxy spot audit",
        "median absolute offset 1.223 s",
        "95% bootstrap CI lower bounds remain positive",
        "tail MAE reductions remain positive",
        "theoretical P-onset estimate",
        "2.53x for PGA and 1.58x for PGV",
        "Python 3.12.13",
    ]:
        check(phrase in article, f"article draft contains bounded claim: {phrase}", rows)

    rows.extend(
        [
            "",
            "## Current Acceptance-Probability Status",
            "",
            "The verified package supports the current NC submission story: cross-dataset early waveform information, empirical predictability-boundary table, cross-region waveform-transfer boundary, K-NET pre-peak subset auditing, held-out generalization, attenuation-shaped and OpenQuake references, K-NET Japanese GMM screening, regional-GMM readiness auditing, conformal uncertainty, residual auditing, extended waveform case auditing, phase-label auditing, full-manifest AQ2009GM feature-table validation, ESM European strong-motion compact-feature validation, ESM P-onset sensitivity auditing, ESM waveform onset-proxy spot auditing, formal Methods drafting, and figure-style auditing.",
            "",
            "The next high-impact empirical gap is no longer ESM timing sanity checking; it is either manual ESM P-pick annotation, stronger residual mechanism evidence, or a fully specified regional GMM comparison once rupture distance, site terms, and tectonic or focal-mechanism metadata are available.",
            "",
        ]
    )
    REPORT.write_text("\n".join(rows))
    print(f"wrote {REPORT}")


if __name__ == "__main__":
    main()
