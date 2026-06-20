# NC Source Data Manifest

Workbook:

- `outputs/source_data/nc_source_data_v1.xlsx`

Scope:

- Derived figure-level and supplement-level CSV tables.
- Raw waveform files are excluded.
- Figure 5 still needs a consolidated numeric source table before final submission.

| sheet | figure/table | source file | status | notes |
|---|---|---|---|---|
| Fig1_TaskMatrix | Figure 1 | `outputs/figure1_dataset_task_matrix.csv` | included | Dataset-task matrix, record counts, target availability and P-window definition summary. |
| Fig2_EarlyWindow | Figure 2 | `outputs/figure2_early_window_performance.csv` | included | Lead-time-dependent early-window performance metrics. |
| Fig3_Heldout | Figure 3 | `outputs/figure3_heldout_generalization.csv` | included | Held-event and held-station generalization metrics. |
| Fig3_BootstrapCI | Figure 3 / Supplement | `work/ground_motion_balanced_station_10s/held_station_bootstrap_ci.csv` | included | Paired bootstrap confidence intervals for held-station MAE reductions. |
| Fig3_TailAudit | Figure 3 / Supplement | `work/ground_motion_balanced_station_10s/held_station_tail_audit.csv` | included | Top-tail MAE and factor-of-two underprediction audit. |
| Fig4_ClassicalUnc | Figure 4 | `outputs/figure4_classical_uncertainty.csv` | included | Classical reference and uncertainty calibration figure data. |
| Fig4_CalSize | Figure 4 / Supplement | `work/nc_calibration_size_audit/target_calibration_size_audit.csv` | included | Target-domain calibration sample-size audit. |
| Fig5_Status | Figure 5 | `outputs/figure5_residual_waveform_audit_summary.md` | pending numeric source table | Residual waveform diagnostics currently have figure and narrative artifacts; a consolidated numeric source table remains pending. |
| Fig6_PhaseAudit | Figure 6 | `outputs/figure6_phase_label_audit.csv` | included | Phase label-domain audit data. |
| Fig7_Boundary | Figure 7 | `outputs/nc_core_predictability_boundary_table.csv` | included | Core predictability-boundary synthesis table. |
| SI_FeatureGroups | Supplement | `outputs/feature_group_ablation_table.csv` | included | Feature-group ablation across P-only, metadata, distance, site and combined feature families. |
| SI_ESM_Onset | Supplement | `outputs/esm_p_onset_sensitivity_audit.csv` | included | ESM theoretical P-onset sensitivity audit. |
| SI_ESM_Spotcheck | Supplement | `outputs/esm_waveform_p_pick_spotcheck.csv` | included | ESM waveform-envelope onset proxy spot audit. |
| SI_EarlyPeak | Supplement | `outputs/early_window_peak_capture_audit.csv` | included | Early-window peak-capture audit. |
| SI_PhaseTable | Supplement | `outputs/figures/phase_audit/phase_audit_1000_table.csv` | included | Per-dataset 1,000-record phase-audit table. |
