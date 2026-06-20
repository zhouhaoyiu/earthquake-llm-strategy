# NC Minimum Submission Package

Date: 2026-06-18

## Target

Nature Communications submission route:

**Cross-regional predictability limits of strong shaking from the first seconds of P waves**

## Core Claim

Public strong-motion archives can be organized into a reproducible benchmark for measuring how much final strong shaking is predictable from the first seconds after P arrival. Early post-P waveform windows contain hazard-relevant information beyond source-path-site metadata, and the remaining uncertainty is target-, split-, and region-dependent. This signal persists under random splits, held-event splits, balanced held-station splits, and bias-corrected classical reference comparisons.

## Evidence Stack

| layer | status | use in paper |
|---|---|---|
| Unified data | done | STEAD, InstanceGM, Iquique, K-NET; 2.46M manifest records |
| K-NET conversion | done | 22,119 complete ZNE records; gal -> cm/s2 verified from NIED docs |
| Phase audit | done at 1,000/dataset | label-domain audit; P stable, S/domain issues visible |
| Random split | done | baseline early-window signal |
| K-NET pre-peak subset audit | done | 1 s and 3 s K-NET gains remain when early horizontal peak is below 80% of observed PGA |
| Held-event | done | rules out ordinary event leakage |
| Balanced held-station | done | station-transfer evidence across 50 held-out stations per strong-motion dataset |
| Held-station 1/2/3/5/10 scan | done | direct information-gain curve for the first 5 seconds and the 10 s reference |
| Matched held-station gain audit | done | source-path support matching shows positive early-waveform gains are not only a station-test distribution artifact |
| Held-station bootstrap CI audit | done | paired bootstrap shows balanced held-station gains are stable to test-record resampling |
| Held-station strong-tail audit | done | top 10% and top 5% target rows show tail MAE gains while preserving factor-2 underprediction as a boundary |
| Classical references | done | attenuation-shaped ridge, BooreEtAl2014, and K-NET Japanese GMM screening |
| Regional GMM readiness | done | field audit explains why full regional GMM claim is not yet supported |
| Uncertainty | done | station-shift calibration is target-dependent |
| Target calibration sample size | done | 50-100 target-domain calibration rows recover near-nominal cross-region conformal coverage in the 2 s and 5 s audit |
| Predictability boundary | done | 10 s random performance, held-event and held-station residual floors, robust held-out gains, and conformal coverage gaps |
| Cross-region transfer boundary | done | early-waveform-only transfer across InstanceGM, K-NET, and AQ2009GM quantifies regional and measurement-system penalties |
| Core boundary synthesis | done | one four-panel map linking information gain, transfer penalty, uncertainty failure, and tail underprediction |
| Residual panels | done | main-text residual diagnostics plus extended waveform audit cases |
| AQ2009GM full-manifest streaming | supplementary done | SeisBench aftershock ground-motion check over all 254 local manifest chunks with velocity waveforms and official PGA/PGV metadata targets |
| ESM European strong-motion supplement | done | local ASCII package check with PGA/PGV targets, held-out baseline, four-domain transfer, and theoretical P-onset boundary |
| ESM P-onset sensitivity | done | Vp 5.5/6.0/6.5 km/s timing audit; retained-window validity above 0.994 across 1/2/3/5/10 s |
| ESM waveform P-onset spot audit | done | 200-record waveform-envelope onset-proxy check; high-confidence median absolute offset 1.223 s and q95 3.960 s |
| PNWAccelerometers robustness | supplementary done | SeisBench accelerometer peak-amplitude check; local HDF5 lacks waveform units |
| Formal Methods draft | done | submission Methods skeleton for data, features, targets, splits, models, references, uncertainty, and residual audits |
| Uncertainty boundary note | done | exchangeability condition and source-domain conformal transfer boundary |
| Regional GMM boundary note | done | separates classical-reference screening from a fully specified regional GMPE/GMM comparison |
| Main figure redraw and style audit | done | Figures 1-6 redrawn from verified tables or audit panels; Figure 5 split into main residual diagnostics and extended waveform cases; Figure 1-7 dimension audit and contact sheet updated |
| Next experiment decision | done | ESM waveform-level onset-proxy spot audit complete; defer full regional GMPE/GMM until required metadata are available |
| Reviewer risk matrix | done | likely reviewer objections mapped to evidence and claim limits |
| Evidence verification | done | generated figures, key tables, split overlap, and document references pass verifier |

Verifier:

- `outputs/nc_evidence_verification_report.md`
- `work/scripts/verify_nc_evidence_package.py`

Methods provenance:

- `outputs/methods_provenance_table.md`

Article draft:

- `outputs/nc_article_draft_v1.md`

Reviewer risk matrix:

- `outputs/nc_reviewer_risk_matrix.md`

Regional GMM readiness:

- `outputs/regional_gmm_readiness_audit.md`
- `outputs/regional_gmm_boundary_note.md`

Formal Methods and boundary notes:

- `outputs/nc_methods_formal_draft.md`
- `outputs/nc_uncertainty_boundary_note.md`
- `outputs/esm_p_onset_sensitivity_audit.md`

Figure style audit:

- `outputs/nc_figure_style_audit.md`
- `outputs/figures/nc_main_figure_contact_sheet.png`

Predictability boundary:

- `outputs/predictability_boundary_summary.md`
- `outputs/predictability_boundary_table.csv`
- `outputs/nc_core_predictability_boundary_summary.md`
- `outputs/nc_core_predictability_boundary_table.csv`
- `outputs/figures/nc_core_predictability_boundary.png`
- `outputs/cross_region_waveform_transfer_summary.md`
- `outputs/cross_region_waveform_transfer_window_scan_summary.md`

## Main Figures

### Figure 1. Dataset and task benchmark

Build from:

- `outputs/figures/figure1_dataset_task_matrix.png`
- `outputs/figure1_dataset_task_matrix_summary.md`
- `outputs/unified_manifest_summary.md`
- `outputs/knet_conversion_summary.md`

Panels:

1. dataset-task matrix;
2. record counts;
3. target availability;
4. P-aligned early windows.

Message:

The paper evaluates phase labels and strong-motion targets in one cross-dataset waveform benchmark.

### Figure 2. Lead-time-dependent early waveform information

Use:

- `outputs/figures/figure2_early_window_performance.png`
- `outputs/figure2_early_window_performance_summary.md`
- `outputs/figures/ground_motion_audit/early_window_residual_evolution_panel.png`

Message:

Early waveform features improve strong-motion inference from 1 s after P arrival, with larger gains for several targets at 3 s and 10 s.

Extended 1/2/3/5/10 scan:

- `outputs/held_station_window_scan_summary.md`
- `outputs/figures/ground_motion_audit/held_station_window_scan.png`

Message:

The held-station scan gives the direct 1-5 s information-gain curve. K-NET PGA rises from 11.3% at 1 s to 23.3% at 5 s, then 49.9% at 10 s. InstanceGM PGV is already strong at 1 s and increases from 40.1% to 45.4% at 5 s.

### Figure 3. Generalization under held-out splits

Use:

- `outputs/figures/figure3_heldout_generalization.png`
- `outputs/figure3_heldout_generalization_summary.md`
- `outputs/figure3_heldout_generalization.csv`
- `outputs/figures/ground_motion_audit/balanced_station_heldout_panel.png`
- `outputs/figures/ground_motion_audit/balanced_station_distribution_audit_panel.png`
- `outputs/figures/ground_motion_audit/matched_station_gain_audit.png`
- `outputs/figures/ground_motion_audit/held_station_bootstrap_ci.png`
- `outputs/figures/ground_motion_audit/held_station_tail_audit.png`
- held-event table from `outputs/heldout_ground_motion_baseline_summary.md`

Message:

Held-event and balanced held-station tests show that the early waveform gain persists after event and station separation. The distribution audit shows that the station-held tests still contain source-path-target shift, so the result should be framed as held-out robustness with explicit split provenance.

The matched held-station gain audit first trims test records to train 5-95% support for magnitude and distance only. These source-path support subsets retain 82.4-83.9% of test records and remain positive for every target, with the weakest reduction at 20.1% for InstanceGM SA10. A stricter target-matched support check also remains positive, with the weakest reduction at 17.2%. The target-matched check is post-hoc because it uses target amplitude.

The paired bootstrap audit uses the same balanced held-station test rows and resamples records to quantify MAE-reduction stability. All six main targets keep positive 95% CI lower bounds; the weakest lower bound is 16.9% for InstanceGM SA10. Current files: `outputs/held_station_bootstrap_ci_summary.md` and `work/ground_motion_balanced_station_10s/held_station_bootstrap_ci.csv`.

The held-station strong-tail audit evaluates the top 10% and top 5% target rows. In the top 5% subsets, tail MAE reductions remain positive for every main target, from 18.9% for InstanceGM SA10 to 66.0% for K-NET PGA. Factor-2 underprediction improves for most targets but worsens slightly for InstanceGM SA30, so the manuscript should present this as a tail-error boundary rather than a solved tail-risk problem. Current files: `outputs/held_station_tail_audit_summary.md` and `work/ground_motion_balanced_station_10s/held_station_tail_audit.csv`.

### Figure 4. Classical reference and uncertainty

Use:

- `outputs/figures/figure4_classical_uncertainty.png`
- `outputs/figure4_classical_uncertainty_summary.md`
- `outputs/figure4_classical_uncertainty.csv`
- `outputs/attenuation_reference_summary.md`
- `outputs/figures/ground_motion_audit/openquake_reference_panel.png`
- `outputs/conformal_uncertainty_balanced_station_summary.md`
- `outputs/nc_calibration_size_audit_summary.md`
- `outputs/figures/ground_motion_audit/nc_calibration_size_audit.png`
- `outputs/knet_japan_gmm_reference_summary.md`
- `work/ground_motion_balanced_station_10s/knet_japan_gmm_reference.csv`

Message:

The early waveform model improves over a low-parameter attenuation-shaped reference and a bias-corrected BooreEtAl2014 reference. On K-NET PGA, it also improves over the best screened Japanese GMM candidate under stated distance, Vs30, and tectonic-class approximations. Uncertainty calibration remains target-dependent under station shift.

The calibration-size audit keeps the source model fixed and varies only target-domain calibration rows for target-offset conformal intervals. Source-domain conformal coverage remains poor at 2 s and 5 s, while target-domain offset calibration recovers near-nominal coverage. In the tested grid, 50 target-domain calibration rows satisfy the IQR stability criterion and 100 rows put both windows near 0.90 median coverage.

### Figure 5. Residual diagnostics

Use:

- `outputs/figures/figure5_residual_waveform_audit.png`
- `outputs/figure5_residual_waveform_audit_summary.md`
- `outputs/figures/ground_motion_audit/ground_motion_residual_diagnostic_panel.png`

Message:

Residual tails expose inspectable records and remaining distance/path/site/label audit targets.

Extended waveform case audit:

- `outputs/figures/extended_waveform_case_audit.png`
- `outputs/figures/ground_motion_audit/instancegm_repeated_residual_audit_panel.png`
- `outputs/figures/ground_motion_audit/knet_pga_worst_residual_audit_panel.png`

Message:

Repeated InstanceGM high-residual records and K-NET PGA waveform cases are audit examples. They support inspectability and should stay outside the main-text residual diagnostic figure.

### Figure 6. Phase label-domain audit

Use:

- `outputs/figures/figure6_phase_label_audit.png`
- `outputs/figure6_phase_label_audit_summary.md`
- `outputs/figure6_phase_label_audit.csv`
- `outputs/figures/phase_audit/phase_audit_1000_panel.png`

Message:

P picks support waveform alignment and K-NET conversion quality. S-phase errors and missing-pick rates expose label-domain transfer issues.

### Figure 7. Predictability-boundary synthesis

Use:

- `outputs/figures/nc_core_predictability_boundary.png`
- `outputs/nc_core_predictability_boundary_summary.md`
- `outputs/nc_core_predictability_boundary_table.csv`

Message:

This figure is the main boundary map. It shows that within-domain early-window gains are positive, cross-region transfer penalties increase from 1 s to 10 s, source-domain conformal intervals under-cover target domains at 2 s and 5 s, and strong-motion tail underprediction remains visible after 5 s.

### Supplementary Figure. PNWAccelerometers peak-amplitude robustness

Use:

- `outputs/figures/ground_motion_audit/pnw_accelerometer_peak_panel.png`
- `outputs/pnw_accelerometer_peak_baseline_summary.md`
- `outputs/pnw_unit_provenance_audit.md`

Message:

Early-window amplitude information also appears in a separate SeisBench accelerometer dataset under held-event and held-station splits. This is a robustness check only; the local PNWAccelerometers HDF5 lacks waveform units, so the target is full-record peak horizontal waveform amplitude.

### Supplementary Figure. AQ2009GM full-manifest chunk-streaming early velocity check

Use:

- `outputs/figures/ground_motion_audit/aq2009gm_full_stream_panel.png`
- `outputs/figures/ground_motion_audit/aq2009gm_full_stream_2s5s_panel.png`
- `outputs/aq2009gm_full_stream_validation_summary.md`
- `outputs/aq2009gm_full_stream_validation_2s5s_summary.md`
- `work/aq2009gm_full_stream_validation/aq2009gm_full_stream_comparison.csv`
- `work/aq2009gm_full_stream_validation_2s5s/aq2009gm_full_stream_comparison.csv`

Message:

AQ2009GM provides a separate SeisBench ground-motion check with official metadata PGA/PGV targets. The validation streams all 254 chunks listed in the local SeisBench AQ2009GM manifest, extracts compact early-window features, and deletes raw chunk files. Metadata plus early velocity features reduce MAE under held-event, held-station, and held-time splits. The retained evidence is full-manifest chunk-streaming feature-table validation after raw chunk deletion.

### Supplementary Figure. Cross-region early-waveform transfer boundary

Use:

- `outputs/figures/ground_motion_audit/cross_region_waveform_transfer_boundary.png`
- `outputs/figures/ground_motion_audit/cross_region_waveform_transfer_window_scan.png`
- `outputs/figures/ground_motion_audit/cross_region_waveform_transfer_aq_esm_2s_boundary.png`
- `outputs/figures/ground_motion_audit/cross_region_waveform_transfer_aq_esm_5s_boundary.png`
- `outputs/cross_region_waveform_transfer_summary.md`
- `outputs/cross_region_waveform_transfer_window_scan_summary.md`
- `outputs/cross_region_waveform_transfer_aq_esm_2s_summary.md`
- `outputs/cross_region_waveform_transfer_aq_esm_5s_summary.md`

Message:

Early-waveform-only transfer across InstanceGM, K-NET, AQ2009GM, and ESM is consistently worse than target-domain training. In the four-domain synthesis, median zero-shot MAE penalty increases from 2.25x at 1 s to 4.27x at 10 s, and target-train offset calibration reduces but does not remove the penalty. This figure anchors the cross-region predictability-boundary claim.

## Methods Draft

### Data

We assembled a unified waveform manifest from STEAD, InstanceGM, Iquique, and a locally converted K-NET strong-motion archive. Supplementary strong-motion checks use AQ2009GM through SeisBench chunk streaming and ESM through local ASCII zip packages. The manifest standardizes record identifiers, dataset splits, waveform paths, component order, P and S picks, source metadata, station metadata, and available ground-motion targets.

K-NET records were converted from BSON to HDF5 with explicit component mapping `UD -> Z`, `NS -> N`, and `EW -> E`. The converted K-NET archive contains 22,119 records with complete ZNE components. K-NET `pga_gal` was mapped to `pga_cmps2` because NIED documentation states that K-NET acceleration waveforms are stored in gal and `1 gal = 1 cm/s2`.

AQ2009GM was used as a supplementary SeisBench ground-motion check through full-manifest chunk streaming. The script reads the local SeisBench chunk manifest, downloads one chunk at a time, extracts early-window velocity features, metadata fields `trace_pga_cmps2` and `trace_pgv_cmps`, event identifiers, and station identifiers, and deletes raw chunk files. The check used 345,226 valid PGA/PGV records from 60,310 events and 66 stations, with held-event, held-station, and held-time splits.

ESM was used as a local European strong-motion supplement. The feature builder reads local ASCII zip packages, pairs acceleration and velocity streams by event and station, computes full-record PGA/PGV targets, and keeps the original zip files unchanged. ESM windows use a theoretical P-onset estimate because the local headers do not provide explicit P arrivals.

### Phase audit

We evaluated pretrained SeisBench PhaseNet(STEAD) and EQTransformer(STEAD) models against catalog P and S labels. The phase audit used 1,000 records per dataset from STEAD, InstanceGM, Iquique, and K-NET. Metrics included matched picks, missing-pick rate, signed error, MAE, median absolute error, q95 absolute error, and large-error counts.

### Early waveform features

Waveforms were aligned to catalog P arrivals where catalog picks are available. Early windows were extracted at 1, 2, 3, 5, and 10 s where retained feature tables are available. The main random-split figures use 1, 3, and 10 s; the held-station scan, AQ2009GM, ESM, and transfer synthesis include 2 and 5 s. Features were computed from Z, N, E, horizontal, and vector amplitudes. Features included absolute maximum, RMS, standard deviation, and 95th-percentile absolute amplitude. Full-record peak features were excluded to avoid target leakage.

Peak-capture audit:

- `outputs/early_window_peak_capture_audit.md`
- `outputs/early_window_peak_capture_audit.csv`
- `outputs/knet_prepeak_subset_audit.md`
- `outputs/knet_prepeak_subset_audit.csv`

K-NET 10 s windows often contain target-scale horizontal amplitudes, so K-NET 10 s results should be framed as early strong-motion information. The 1 s and 3 s windows carry the lead-time-sensitive interpretation. In the K-NET pre-peak subset where early horizontal peak remains below 80% of observed PGA, early waveform features still reduce MAE by 13.8% at 1 s and 17.9% at 3 s. The 10 s pre-peak subset has 53 records and belongs in audit material. InstanceGM early/target amplitude ratios need unit reconciliation before direct interpretation.

ESM P-onset sensitivity:

- `outputs/esm_p_onset_sensitivity_audit.md`
- `outputs/esm_p_onset_sensitivity_audit.csv`

Vp 5.5 km/s delays the theoretical onset by a median 2.517 s relative to 6.0 km/s; Vp 6.5 km/s advances it by a median 2.130 s. Retained-window validity remains above 0.994 across all tested windows and velocities. ESM should be written as an external supplement and transfer-domain check, with explicit theoretical-P wording.

ESM waveform-level onset-proxy spot audit:

- `outputs/esm_waveform_p_pick_spotcheck.md`
- `outputs/esm_waveform_p_pick_spotcheck.csv`
- `outputs/figures/ground_motion_audit/esm_waveform_p_pick_spotcheck.png`

The spot audit samples 200 ESM event-station records across distance and PGA quantiles. It detects automated waveform-envelope onset proxies in 105 records, with 86 high-confidence detections. In the high-confidence subset, the median absolute offset from the theoretical 6 km/s onset is 1.223 s, q90 is 3.338 s, q95 is 3.960 s, and 98.8% are within 5 s. This is a waveform timing sanity check, not a manual or catalog P-pick validation.

### Ground-motion targets

Targets were modeled in log10 units. InstanceGM targets included PGA, PGV, SA03, SA10, and SA30. K-NET provided PGA. K-NET PGA values were treated as cm/s2 after unit verification from NIED documentation.

AQ2009GM supplementary targets were modeled in log10 units from `trace_pga_cmps2` and `trace_pgv_cmps`. Early-window features were computed from streamed velocity waveforms, so this supplement tests whether early velocity carries information about PGA/PGV targets across the local AQ2009GM chunk manifest.

ESM supplementary targets were modeled in log10 units from full-record PGA and PGV computed from local ACC.AP and VEL.AP streams.

### Baselines

We compared median, metadata-only, early-waveform-only, and metadata plus early-waveform models. Metadata features included magnitude, depth, distance, station elevation, Vs30 where available, year, and sample count. The main regressor was HistGradientBoostingRegressor with the same settings across experiments.

### Held-out splits

Random splits used the original dataset split fields. Held-event splits excluded all records from selected `event_id` groups from training. Held-station splits excluded selected `station_network_code.station_code` groups from training. The balanced held-station split held out 50 stations for InstanceGM and 50 stations for K-NET, then sampled 1,000 test records while preserving station coverage. Group overlap was zero in all held-out experiments.

### Cross-region transfer

Cross-region transfer used early waveform features only. It excluded distance, magnitude, site variables, event identifiers, and station identifiers. The zero-shot setting trained on one source domain and evaluated on a held-out target-domain test split. The offset-calibrated setting estimated one scalar correction on the target-domain training split before target test evaluation.

### OpenQuake reference

We fit a low-parameter attenuation-shaped ridge reference on the balanced held-station training features. Inputs were magnitude, log10 hypocentral-distance shape, depth, and log10 Vs30 where available. InstanceGM has Vs30 in this split; K-NET lacks Vs30 in the approved local package, so the K-NET attenuation reference lacks site correction. The metadata plus early-waveform model had lower held-station MAE for all tested targets, with reductions from 17.5% to 51.6% relative to this reference. This is a baseline check.

We used OpenQuake hazardlib BooreEtAl2014 as a classical reference for PGA, PGV, and SA where labels were available. Model outputs were converted from natural-log units to log10 target units. Predictions received a train-set median bias correction. Because rupture geometry was unavailable, `source_distance_km` was used as an Rjb proxy, rake was set to 0, and missing Vs30 was set to 760 m/s. This comparison is a conservative reference with stated approximations.

For K-NET PGA, we also screened OpenQuake Japanese or Japan-derived GMMs: Kanno2006, Zhao2006, and SiMidorikawa1999 variants. These predictions used `source_distance_km` as an Rrup proxy, missing Vs30 defaults, and train-set median bias correction. The best candidate was Kanno2006Shallow with MAE 0.242, while the metadata plus early-waveform held-station model had MAE 0.111.

Regional GMM readiness audit shows the current boundary. InstanceGM joins back to metadata for all balanced held-station records and has complete Vs30 in this split, but focal-mechanism strings appear in only 141/5,000 train records and 36/1,000 test records. K-NET has complete source-distance values in the current split, but no Vs30, rupture-distance, or focal-mechanism fields in the approved local package.

### Uncertainty

We computed split-conformal intervals on the balanced held-station features. Training records were split into proper training and calibration subsets. The 90% interval width was set by the finite-sample conformal quantile of calibration absolute residuals. Coverage was evaluated on held-station test records. The uncertainty boundary note states the exchangeability condition and separates target-domain calibration from source-domain conformal transfer.

### Residual audit

Residuals were defined as predicted log10 target minus observed log10 target. We evaluated mean residuals, median signed residuals, q90 and q95 absolute residuals, binned residual structure by source and station variables, and high-residual waveform examples.

## Claims

Use:

1. Early post-P waveform windows improve strong-motion inference beyond metadata.
2. The effect persists under held-event and balanced held-station splits.
3. The effect is visible across InstanceGM targets and K-NET PGA.
4. A bias-corrected OpenQuake reference is weaker than metadata plus early waveform features.
5. AQ2009GM full-manifest chunk-streaming gives a supplementary SeisBench check with official PGA/PGV metadata targets.
6. Cross-region early-waveform transfer quantifies regional and measurement-system predictability penalties.
7. Residual and conformal analyses expose remaining station-shift and target-dependent uncertainty.
8. ESM provides an external European strong-motion domain with a quantified theoretical P-onset boundary.

Avoid:

1. Earthquake prediction.
2. Operational early-warning readiness.
3. Foundation-model superiority.
4. Physical causality from residual correlations.
5. Full superiority over a fully specified regional GMPE/GMM.
6. Local retention of the full raw AQ2009GM archive.
7. Catalog/manual P-pick claims for ESM.

## Remaining Work

Must do before submission:

1. Do a page-level readability check for the redrawn figures, especially Figure 5 and the extended waveform case audit.
2. Audit manuscript wording against the claim boundaries in `outputs/nc_evidence_packet_zh.md`.
3. Decide whether phase audit stays at 1,000/dataset or is expanded.
4. Decide whether PNWAccelerometers stays in supplement or receives documented unit support.

Optional:

1. Add another independent strong-motion archive with clear units.
2. Replace Rjb proxy with better rupture-distance metadata if available.
3. Add a fully specified regional GMPE/GMM comparison if rupture class, rupture distance, and site terms become available.
