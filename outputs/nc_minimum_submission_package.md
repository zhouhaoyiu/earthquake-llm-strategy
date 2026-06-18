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
| Classical references | done | attenuation-shaped ridge, BooreEtAl2014, and K-NET Japanese GMM screening |
| Regional GMM readiness | done | field audit explains why full regional GMM claim is not yet supported |
| Uncertainty | done | station-shift calibration is target-dependent |
| Residual panels | done | audit cases and distance-tail diagnostics |
| AQ2009GM 096-100 | supplementary done | Expanded SeisBench aftershock ground-motion check with velocity waveforms and official PGA/PGV metadata targets |
| PNWAccelerometers robustness | supplementary done | SeisBench accelerometer peak-amplitude check; local HDF5 lacks waveform units |
| Reviewer risk matrix | done | likely reviewer objections mapped to evidence and claim limits |
| Evidence verification | done | generated figures, key tables, split overlap, and document references pass verifier |

Verifier:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/nc_evidence_verification_report.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/scripts/verify_nc_evidence_package.py`

Methods provenance:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/methods_provenance_table.md`

Reviewer risk matrix:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/nc_reviewer_risk_matrix.md`

Regional GMM readiness:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/regional_gmm_readiness_audit.md`

## Main Figures

### Figure 1. Dataset and task benchmark

Build from:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/figure1_dataset_task_matrix.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figure1_dataset_task_matrix_summary.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/unified_manifest_summary.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/knet_conversion_summary.md`

Panels:

1. dataset-task matrix;
2. record counts;
3. target availability;
4. P-aligned early windows.

Message:

The paper evaluates phase labels and strong-motion targets in one cross-dataset waveform benchmark.

### Figure 2. Lead-time-dependent early waveform information

Use:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/figure2_early_window_performance.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figure2_early_window_performance_summary.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit/early_window_residual_evolution_panel.png`

Message:

Early waveform features improve strong-motion inference from 1 s after P arrival, with larger gains for several targets at 3 s and 10 s.

### Figure 3. Generalization under held-out splits

Use:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/figure3_heldout_generalization.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figure3_heldout_generalization_summary.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figure3_heldout_generalization.csv`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit/balanced_station_heldout_panel.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit/balanced_station_distribution_audit_panel.png`
- held-event table from `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/heldout_ground_motion_baseline_summary.md`

Message:

Held-event and balanced held-station tests show that the early waveform gain persists after event and station separation. The distribution audit shows that the station-held tests still contain source-path-target shift, so the result should be framed as held-out robustness with explicit split provenance.

### Figure 4. Classical reference and uncertainty

Use:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/figure4_classical_uncertainty.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figure4_classical_uncertainty_summary.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figure4_classical_uncertainty.csv`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/attenuation_reference_summary.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit/openquake_reference_panel.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/conformal_uncertainty_balanced_station_summary.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/knet_japan_gmm_reference_summary.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_balanced_station_10s/knet_japan_gmm_reference.csv`

Message:

The early waveform model improves over a low-parameter attenuation-shaped reference and a bias-corrected BooreEtAl2014 reference. On K-NET PGA, it also improves over the best screened Japanese GMM candidate under stated distance, Vs30, and tectonic-class approximations. Uncertainty calibration remains target-dependent under station shift.

### Figure 5. Residual and waveform audit

Use:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/figure5_residual_waveform_audit.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figure5_residual_waveform_audit_summary.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit/ground_motion_residual_diagnostic_panel.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit/instancegm_repeated_residual_audit_panel.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit/knet_pga_worst_residual_audit_panel.png`

Message:

Residual tails expose inspectable records and remaining distance/path/site/label audit targets.

### Figure 6. Phase label-domain audit

Use:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/figure6_phase_label_audit.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figure6_phase_label_audit_summary.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figure6_phase_label_audit.csv`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/phase_audit/phase_audit_1000_panel.png`

Message:

P picks support waveform alignment and K-NET conversion quality. S-phase errors and missing-pick rates expose label-domain transfer issues.

### Supplementary Figure. PNWAccelerometers peak-amplitude robustness

Use:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit/pnw_accelerometer_peak_panel.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/pnw_accelerometer_peak_baseline_summary.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/pnw_unit_provenance_audit.md`

Message:

Early-window amplitude information also appears in a separate SeisBench accelerometer dataset under held-event and held-station splits. This is a robustness check only; the local PNWAccelerometers HDF5 lacks waveform units, so the target is full-record peak horizontal waveform amplitude.

### Supplementary Figure. AQ2009GM 096-100 early velocity check

Use:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit/aq2009gm_chunks096-100_station12_panel.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/aq2009gm_chunks096-100_station12_baseline_summary.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/aq2009gm_chunks096-100_station12_baseline/aq2009gm_chunks096-100_comparison.csv`

Message:

AQ2009GM chunks 096-100 provide a separate SeisBench ground-motion check with HDF5 velocity waveforms in m/s and official metadata PGA/PGV targets. Metadata plus early velocity features reduce MAE under held-event and held-station splits. The result is a five-chunk aftershock supplement, so it should not be framed as full external strong-motion validation.

## Methods Draft

### Data

We assembled a unified waveform manifest from STEAD, InstanceGM, Iquique, and a locally converted K-NET strong-motion archive. The manifest standardizes record identifiers, dataset splits, waveform paths, component order, P and S picks, source metadata, station metadata, and available ground-motion targets.

K-NET records were converted from BSON to HDF5 with explicit component mapping `UD -> Z`, `NS -> N`, and `EW -> E`. The converted K-NET archive contains 22,119 records with complete ZNE components. K-NET `pga_gal` was mapped to `pga_cmps2` because NIED documentation states that K-NET acceleration waveforms are stored in gal and `1 gal = 1 cm/s2`.

AQ2009GM chunks 096-100 were used as a supplementary SeisBench ground-motion check. The local HDF5 files declare waveform measurement as velocity and unit as m/s. The targets are metadata fields `trace_pga_cmps2` and `trace_pgv_cmps`. The check used 30,737 valid PGA/PGV records from 5,497 events and 50 stations, with held-event and held-station splits.

### Phase audit

We evaluated pretrained SeisBench PhaseNet(STEAD) and EQTransformer(STEAD) models against catalog P and S labels. The phase audit used 1,000 records per dataset from STEAD, InstanceGM, Iquique, and K-NET. Metrics included matched picks, missing-pick rate, signed error, MAE, median absolute error, q95 absolute error, and large-error counts.

### Early waveform features

Waveforms were aligned to catalog P arrivals. Early windows were extracted at 1 s, 3 s, and 10 s after the P arrival. Features were computed from Z, N, E, horizontal, and vector amplitudes. Features included absolute maximum, RMS, standard deviation, and 95th-percentile absolute amplitude. Full-record peak features were excluded to avoid target leakage.

Peak-capture audit:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/early_window_peak_capture_audit.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/early_window_peak_capture_audit.csv`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/knet_prepeak_subset_audit.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/knet_prepeak_subset_audit.csv`

K-NET 10 s windows often contain target-scale horizontal amplitudes, so K-NET 10 s results should be framed as early strong-motion information. The 1 s and 3 s windows carry the lead-time-sensitive interpretation. In the K-NET pre-peak subset where early horizontal peak remains below 80% of observed PGA, early waveform features still reduce MAE by 13.8% at 1 s and 17.9% at 3 s. The 10 s pre-peak subset has 53 records and belongs in audit material. InstanceGM early/target amplitude ratios are not directly interpretable without unit reconciliation.

### Ground-motion targets

Targets were modeled in log10 units. InstanceGM targets included PGA, PGV, SA03, SA10, and SA30. K-NET provided PGA. K-NET PGA values were treated as cm/s2 after unit verification from NIED documentation.

AQ2009GM supplementary targets were modeled in log10 units from `trace_pga_cmps2` and `trace_pgv_cmps`. Early-window features were computed from velocity waveforms, so this supplement tests whether early velocity carries information about PGA/PGV targets within AQ2009GM chunks 096-100.

### Baselines

We compared median, metadata-only, early-waveform-only, and metadata plus early-waveform models. Metadata features included magnitude, depth, distance, station elevation, Vs30 where available, year, and sample count. The main regressor was HistGradientBoostingRegressor with the same settings across experiments.

### Held-out splits

Random splits used the original dataset split fields. Held-event splits excluded all records from selected `event_id` groups from training. Held-station splits excluded selected `station_network_code.station_code` groups from training. The balanced held-station split held out 50 stations for InstanceGM and 50 stations for K-NET, then sampled 1,000 test records while preserving station coverage. Group overlap was zero in all held-out experiments.

### OpenQuake reference

We fit a low-parameter attenuation-shaped ridge reference on the balanced held-station training features. Inputs were magnitude, log10 hypocentral-distance shape, depth, and log10 Vs30 where available. InstanceGM has Vs30 in this split; K-NET does not, so the K-NET attenuation reference is not site-corrected. The metadata plus early-waveform model had lower held-station MAE for all tested targets, with reductions from 17.5% to 51.6% relative to this reference. This is a baseline check, not a regional GMM.

We used OpenQuake hazardlib BooreEtAl2014 as a classical reference for PGA, PGV, and SA where labels were available. Model outputs were converted from natural-log units to log10 target units. Predictions received a train-set median bias correction. Because rupture geometry was unavailable, `source_distance_km` was used as an Rjb proxy, rake was set to 0, and missing Vs30 was set to 760 m/s. This comparison is a conservative reference with stated approximations.

For K-NET PGA, we also screened OpenQuake Japanese or Japan-derived GMMs: Kanno2006, Zhao2006, and SiMidorikawa1999 variants. These predictions used `source_distance_km` as an Rrup proxy, missing Vs30 defaults, and train-set median bias correction. The best candidate was Kanno2006Shallow with MAE 0.242, while the metadata plus early-waveform held-station model had MAE 0.111.

Regional GMM readiness audit shows the current boundary. InstanceGM joins back to metadata for all balanced held-station records and has complete Vs30 in this split, but focal-mechanism strings appear in only 141/5,000 train records and 36/1,000 test records. K-NET has complete source-distance values in the current split, but no Vs30, rupture-distance, or focal-mechanism fields in the approved local package.

### Uncertainty

We computed split-conformal intervals on the balanced held-station features. Training records were split into proper training and calibration subsets. The 90% interval width was set by the finite-sample conformal quantile of calibration absolute residuals. Coverage was evaluated on held-station test records.

### Residual audit

Residuals were defined as predicted log10 target minus observed log10 target. We evaluated mean residuals, median signed residuals, q90 and q95 absolute residuals, binned residual structure by source and station variables, and high-residual waveform examples.

## Claims

Use:

1. Early post-P waveform windows improve strong-motion inference beyond metadata.
2. The effect persists under held-event and balanced held-station splits.
3. The effect is visible across InstanceGM targets and K-NET PGA.
4. A bias-corrected OpenQuake reference is weaker than metadata plus early waveform features.
5. AQ2009GM 096-100 gives a supplementary SeisBench check with explicit velocity units and official PGA/PGV metadata targets.
6. Residual and conformal analyses expose remaining station-shift and target-dependent uncertainty.

Avoid:

1. Earthquake prediction.
2. Operational early-warning readiness.
3. Foundation-model superiority.
4. Physical causality from residual correlations.
5. Full superiority over a fully specified regional GMPE/GMM.
6. Full external validation from a five-chunk AQ2009GM subset.

## Remaining Work

Must do before submission:

1. Redraw all figures in one consistent publication style.
2. Update the manuscript scaffold with balanced held-station, OpenQuake, and conformal results.
3. Add exact software/data provenance to Methods.
4. Decide whether phase audit stays at 1,000/dataset or is expanded.
5. Decide whether to expand AQ2009GM beyond chunks 096-100.

Optional:

1. Expand AQ2009GM to broader coverage or add another independent strong-motion archive with clear units.
2. Replace Rjb proxy with better rupture-distance metadata if available.
3. Add a fully specified regional GMPE/GMM comparison if rupture class, rupture distance, and site terms become available.
