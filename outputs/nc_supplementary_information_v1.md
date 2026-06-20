# Supplementary Information

## Cross regional limits on predicting strong shaking from early P waves

[Author names]

This Supplementary Information file supports the Article draft. It is a structure and evidence map, not the final submitted SI. Final tables, references and data links should be locked after the manuscript figures are frozen.

## Supplementary Note 1. Dataset inventory and harmonization

Purpose: document the public datasets, record counts, metadata fields and exclusion rules used to build the event-station benchmark.

Current evidence files:

- `outputs/unified_manifest_summary.md`
- `outputs/knet_conversion_summary.md`
- `outputs/figure1_dataset_task_matrix_summary.md`
- `outputs/methods_provenance_table.md`

Key values to report:

- Unified manifest: 2,460,425 records.
- InstanceGM: 1,159,223 records in the main strong-motion benchmark.
- K-NET: 22,119 complete ZNE records.
- ESM supporting set: 134,250 event-station rows from 861 events and 1,568 stations.
- AQ2009GM processed feature evidence: 345,226 rows from 60,310 events and 66 stations.

## Supplementary Note 2. Early P-window feature construction

Purpose: define the 1, 2, 3, 5 and 10 s P-window extraction, feature families, target variables and log transformations.

Items to include:

- P-arrival reference used for each dataset.
- Sampling checks and missing-window exclusion.
- Feature families: amplitude, absolute amplitude, squared amplitude, cumulative energy, envelope, component ratios and simple frequency summaries.
- Target definitions: PGA, PGV and SA ordinates.

## Supplementary Note 3. Split definitions and leakage checks

Purpose: show that the main comparisons use grouped splits and that the claimed held-out tests have zero group overlap.

Current evidence files:

- `outputs/heldout_ground_motion_baseline_summary.md`
- `outputs/held_station_window_scan_summary.md`
- `outputs/figure3_heldout_generalization_summary.md`
- `work/scripts/verify_nc_evidence_package.py`

Items to include:

- Held-event split definition.
- Held-station split definition.
- Balanced held-station construction.
- Split-overlap audit table.

## Supplementary Note 4. Window-length information gain

Purpose: provide full target-level metrics for 1, 2, 3, 5 and 10 s windows.

Current evidence files:

- `outputs/held_station_window_scan_summary.md`
- `outputs/figures/ground_motion_audit/held_station_window_scan.png`

Key values to report:

- K-NET PGA held-station reduction: 11.3% at 1 s, 23.3% at 5 s and 49.9% at 10 s.
- InstanceGM PGV held-station reduction: 40.1% at 1 s, 45.4% at 5 s and 52.6% at 10 s.

## Supplementary Note 4a. Feature-group ablation

Purpose: separate the contributions of early P-window features, source-path metadata, distance and site information.

Current evidence files:

- `outputs/feature_group_ablation_summary.md`
- `outputs/feature_group_ablation_table.csv`
- `outputs/figures/ground_motion_audit/feature_group_ablation.png`

Key values to report:

- In InstanceGM/K-NET held-station tests, P-only information improves over a median baseline at every tested window, with median reductions rising from 29.6% at 1 s to 43.7% at 10 s.
- Adding P-window features to metadata improves over metadata-only at every tested window, with median reductions from 20.2% at 1 s to 31.6% at 10 s.
- In ESM held-station tests, distance gives a large additional gain over P-only features at short windows, while site metadata gives a smaller split- and window-dependent increment.
- In AQ2009GM, metadata plus P-window features reduce held-station error by 38.0% at 2 s and 63.8% at 5 s.

## Supplementary Note 5. Support, bootstrap and tail audits

Purpose: separate robust information gain from distribution artifacts and high-tail failure modes.

Current evidence files:

- `outputs/matched_station_gain_audit_summary.md`
- `outputs/held_station_bootstrap_ci_summary.md`
- `outputs/held_station_tail_audit_summary.md`
- `work/ground_motion_balanced_station_10s/held_station_bootstrap_ci.csv`
- `work/ground_motion_balanced_station_10s/held_station_tail_audit.csv`

Key values to report:

- Source-path support subsets retain 82.4-83.9% of held-station test rows.
- Source-path support gains remain positive for all six main targets, from 20.1% to 54.5%.
- Paired bootstrap confidence intervals have positive lower bounds across all six targets.
- The weakest bootstrap lower bound is 16.9% for InstanceGM SA at 1.0 s.
- Top 5% target-row tail MAE reductions range from 18.9% to 66.0%.
- InstanceGM SA at 3.0 s keeps a factor-of-two underprediction limitation in the top tail.

## Supplementary Note 6. Classical references and regional GMM boundary

Purpose: document attenuation-style references, Boore-style screening and K-NET Japanese GMM checks without claiming a fully specified regional GMPE comparison where metadata are incomplete.

Current evidence files:

- `outputs/attenuation_reference_summary.md`
- `outputs/knet_japan_gmm_reference_summary.md`
- `outputs/regional_gmm_readiness_audit.md`
- `outputs/regional_gmm_boundary_note.md`

## Supplementary Note 7. Uncertainty calibration

Purpose: provide conformal coverage, coverage-gap, and interval-width metrics.

Current evidence files:

- `outputs/conformal_uncertainty_balanced_station_summary.md`
- `outputs/nc_uncertainty_boundary_note.md`
- `outputs/nc_core_predictability_boundary_summary.md`
- `outputs/nc_calibration_size_audit_summary.md`
- `work/nc_calibration_size_audit/target_calibration_size_audit.csv`

Key values to report:

- K-NET PGA target-domain conformal coverage: 0.925.
- InstanceGM PGV target-domain conformal coverage: 0.898.
- Other main target-domain coverages: 0.820-0.876.
- Source-domain conformal transfer coverage: 0.468 at 2 s and 0.298 at 5 s, equivalent to 0.432 and 0.602 coverage gaps to nominal 0.90.
- Target-domain offset conformal calibration recovers median coverage near 0.90 at 2 s and 5 s, with median interval width 2.177 log10 units.
- In the calibration-size audit, 50 target-domain calibration records meet the tested IQR stability criterion, and 100 records place both windows close to 0.90 median coverage.

## Supplementary Note 8. Cross-regional transfer

Purpose: report zero-shot and target-offset transfer penalties across InstanceGM, K-NET, ESM and AQ2009GM.

Current evidence files:

- `outputs/cross_region_waveform_transfer_summary.md`
- `outputs/cross_region_waveform_transfer_window_scan_summary.md`
- `outputs/esm_p_onset_sensitivity_audit.md`
- `outputs/esm_waveform_onset_spot_audit_summary.md`

Key values to report:

- Zero-shot Japan-to-Europe median error ratios: 2.25, 2.65, 2.98, 3.38 and 4.27 for 1, 2, 3, 5 and 10 s.
- Target-offset ratios: 1.40, 1.55, 1.67, 1.85 and 2.46 for 1, 2, 3, 5 and 10 s.
- ESM 10 s target-offset external ratios: 2.53 for PGA and 1.58 for PGV.
- ESM P-arrival sensitivity median shifts: 2.517 s delayed and 2.130 s advanced.
- High-confidence ESM onset audit: median offset 1.223 s and 95th percentile 3.960 s.

## Supplementary Figures

- Supplementary Fig. 1: dataset-task matrix and target availability.
- Supplementary Fig. 2: held-station 1/2/3/5/10 window scan.
- Supplementary Fig. 3: feature-group ablation.
- Supplementary Fig. 4: source-path support audit.
- Supplementary Fig. 5: paired bootstrap confidence intervals.
- Supplementary Fig. 6: strong-tail MAE and factor-of-two underprediction audit.
- Supplementary Fig. 7: classical reference comparison.
- Supplementary Fig. 8: uncertainty transfer boundary.
- Supplementary Fig. 9: target-domain calibration sample-size audit.
- Supplementary Fig. 10: ESM and AQ2009GM supporting transfer evidence.

## Supplementary Tables

- Supplementary Table 1: dataset inventory.
- Supplementary Table 2: feature definitions.
- Supplementary Table 3: split definitions and overlap checks.
- Supplementary Table 4: held-station window-scan metrics.
- Supplementary Table 5: feature-group ablation metrics.
- Supplementary Table 6: bootstrap confidence intervals.
- Supplementary Table 7: strong-tail audit metrics.
- Supplementary Table 8: conformal coverage metrics.
- Supplementary Table 9: target-domain calibration sample-size metrics.
- Supplementary Table 10: cross-regional transfer ratios.

## Source data plan

Nature Communications may request source data files for graphs. A first source-data workbook has been generated at `outputs/source_data/nc_source_data_v1.xlsx`, with a machine-readable manifest at `outputs/source_data/nc_source_data_manifest.md`.

The workbook contains one README sheet plus figure- or supplement-level sheets for Figures 1, 2, 3, 4, 5, 6 and 7, the calibration-size audit, feature-group ablation, ESM timing audits, early-window peak-capture audit and the phase-audit table. Figure 5 uses a consolidated residual-diagnostic source table at `outputs/figure5_residual_diagnostic_source_data.csv`.

Do not include raw waveform files in the source-data file. Provide provider links and derived feature-table release instructions instead.
