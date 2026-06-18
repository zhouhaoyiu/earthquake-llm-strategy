# Cross-regional predictability limits of strong shaking from the first seconds of P waves

Date: 2026-06-18

Status: current NC manuscript scaffold after the 2026-06-19 reframing. The paper is now a public benchmark, predictability-limit, and uncertainty-calibration study. The empirical evidence includes random splits, held-event splits, balanced held-station splits, an empirical predictability-boundary table, OpenQuake reference comparisons, conformal intervals, station-split distribution audits, phase-label audits, a supplementary AQ2009GM 096-100 PGA/PGV check, and a supplementary PNW accelerometer peak-amplitude check.

## Abstract

The first seconds after a P-wave arrival are central to earthquake early warning, but their practical information content for final strong shaking remains poorly bounded across public data sets. We assemble a unified benchmark from STEAD, InstanceGM, Iquique, and a locally converted K-NET strong-motion archive to measure how predictability changes with 1 s, 3 s, and 10 s post-P windows. The benchmark contains 2.46 million manifest records and 22,119 complete K-NET ZNE records with verified acceleration units. We evaluate metadata-only and metadata plus early-waveform models for PGA, PGV, and spectral acceleration, then test the gain under random, held-event, and balanced held-station splits. Early waveform information improves strong-motion inference beyond source-path-site metadata across all main tested targets. In balanced held-station evaluation, the combined model reduces log10 MAE by 35.5% for InstanceGM PGA, 52.6% for InstanceGM PGV, and 49.9% for K-NET PGA. Classical reference comparisons using attenuation-shaped models, bias-corrected OpenQuake BooreEtAl2014, and screened Japanese GMMs support the same pattern within stated metadata limits. Split-conformal intervals show that point-prediction gains do not guarantee calibrated uncertainty under station shift, with target-dependent under-coverage for InstanceGM. Residual and phase-label audits expose remaining distance tails, repeated high-residual records, and label-domain transfer limits. These results define a reproducible public benchmark for early strong-motion predictability and its uncertainty boundaries.

## Significance Statement

Earthquake early warning depends on how much final shaking can be inferred before damaging waves fully develop. This study turns that question into a public benchmark. It measures the information gained from the first seconds after P arrival, tests whether the gain survives event and station holdout, and reports where uncertainty remains miscalibrated. The result supports rapid hazard research and benchmark development; operational warning use requires latency, real-time, and prospective validation.

## Introduction

The first seconds after the P arrival contain direct observations of the developing ground motion. These observations can reflect source strength, path attenuation, site response, and amplitude growth before the full shaking record is available. Strong-motion targets such as PGA, PGV, and spectral acceleration connect these early observations to engineering and hazard workflows.

Cross-dataset evaluation is essential for this problem. Seismic archives differ in instrumentation, magnitude-distance coverage, waveform units, phase-label conventions, and target definitions. A model that performs well in one archive can still rely on dataset-specific structure. A useful benchmark must separate early waveform information from metadata effects, split artifacts, label-domain problems, and residual tails.

We build a unified benchmark from STEAD, InstanceGM, Iquique, and K-NET. The benchmark links phase-label transfer with strong-motion inference. We evaluate early waveform features at 1 s, 3 s, and 10 s after the catalog P arrival. We compare metadata-only and metadata plus early-waveform models, test held-event and balanced held-station generalization, compare against a classical OpenQuake reference, and inspect residual and uncertainty structure.

## Results

### A unified waveform-task benchmark

The unified manifest contains 2,460,425 records. STEAD contributes large-scale phase and detection labels. InstanceGM contributes 1,159,223 ground-motion records with PGA, PGV, and spectral acceleration targets. Iquique contributes a regional phase-transfer setting. K-NET contributes 22,119 locally converted complete ZNE strong-motion records.

K-NET was converted from BSON into HDF5 and CSV manifests using explicit component mapping: UD to Z, NS to N, and EW to E. Official NIED documentation supports the local mapping from K-NET acceleration values in gal to cm/s2. The manuscript should report the conversion path and the unit verification as data provenance.

### Phase audits check label-domain transfer

A 1,000-record-per-dataset phase audit evaluated pretrained PhaseNet(STEAD) and EQTransformer(STEAD) models against catalog P and S labels. STEAD remained stable, with PhaseNet P MAE of 0.035 s and S MAE of 0.082 s. K-NET P picks were also stable, with PhaseNet P MAE of 0.056 s, while K-NET S picks showed a wider tail with q95 around 1.05 s. InstanceGM showed the largest missing-pick problem, especially for S arrivals. Iquique had low P missing rates and larger S errors.

This audit supports the P-aligned waveform extraction used in the strong-motion experiments. It also identifies label-domain limits that should be kept separate from ground-motion performance.

### Early waveform windows improve strong-motion inference

Metadata plus early waveform features improved all tested strong-motion targets in the random split. At 10 s after P arrival, InstanceGM PGA MAE decreased from 0.299 to 0.207 log10 units, a 30.6% reduction. InstanceGM PGV decreased from 0.298 to 0.165, a 44.7% reduction. InstanceGM spectral acceleration also improved, with reductions of 19.0% for SA03, 26.8% for SA10, and 20.9% for SA30. K-NET PGA decreased from 0.217 to 0.105, a 51.8% reduction.

The effect is visible before the 10 s window. Across the 1 s, 3 s, and 10 s experiments, early waveform features improve mean errors and several tail-error metrics. The 1 s results are important for lead-time interpretation. The 10 s results measure stronger waveform information, with a greater chance that the target peak has already begun to develop in small or nearby events.

A peak-capture audit supports this wording. In K-NET, 10 s windows often contain target-scale horizontal amplitudes: 94.7% of test records have early horizontal peak amplitude at least 0.8 times the PGA target. The 1 s K-NET window also contains target-scale amplitudes in many records, with 69.8% above the same threshold. InstanceGM early amplitudes and PGA targets are not on a directly comparable local scale, so direct early/target amplitude ratios are not used for that dataset. These results keep the lead-time interpretation tied to the 1 s and 3 s experiments while treating the 10 s window as a stronger early strong-motion information test.

A K-NET pre-peak subset audit strengthens the 1 s and 3 s interpretation. The audit filters records where the early horizontal peak remains below 80% of observed PGA. In this subset, early waveform features reduce MAE from 0.238 to 0.205 at 1 s across 302 records and from 0.239 to 0.197 at 3 s across 255 records. The corresponding reductions are 13.8% and 17.9%. The 10 s pre-peak subset has 53 records, so it is used as an audit result.

### Held-out splits support generalization

Held-event evaluation excludes all records from selected events during training. In this split, the 10 s combined model improved every InstanceGM target and K-NET PGA. MAE reductions were 38.8% for InstanceGM PGA, 50.4% for InstanceGM PGV, 22.5% for SA03, 24.7% for SA10, 24.9% for SA30, and 54.5% for K-NET PGA.

Balanced held-station evaluation excludes selected stations during training and preserves coverage over 50 held-out stations for InstanceGM and 50 for K-NET. In this split, the combined model again improved every tested target. MAE reductions were 35.5% for InstanceGM PGA, 52.6% for InstanceGM PGV, 26.0% for SA03, 20.9% for SA10, 27.8% for SA30, and 49.9% for K-NET PGA. Group overlap was zero.

The split distribution audit shows that the held-station tests retain real shift. InstanceGM test records are farther and weaker than the training records: median distance increases from 44.27 km to 70.61 km, and median log10 PGA decreases from -1.68 to -2.11. K-NET train and test distributions overlap closely for distance and PGA, with overlap above 0.91. The station-held results should be framed as robust under source-path-target shift. Avoid distribution-matched transfer wording.

### OpenQuake reference and uncertainty reveal remaining limits

We fit a low-parameter attenuation-shaped ridge reference using magnitude, a log10 hypocentral-distance shape, depth, and log10 Vs30 where available. InstanceGM has Vs30 in this split. K-NET lacks Vs30, so the K-NET attenuation reference is an attenuation-shaped baseline without site correction. The metadata plus early-waveform model improved over this reference across all balanced held-station targets, with relative MAE reductions from 17.5% to 51.6%. This check shows waveform gain beyond a flexible metadata baseline.

We used OpenQuake hazardlib BooreEtAl2014 as a classical reference for PGA, PGV, and spectral acceleration where targets were available. The comparison uses train-set median bias correction. It also uses source distance as an Rjb proxy, rake fixed at 0, and Vs30 set to 760 m/s where missing. These approximations make the reference useful for context with limited rupture geometry.

The combined early-waveform model outperformed this bias-corrected reference across tested targets. Relative to BooreEtAl2014, combined MAE decreased by 36.6% for InstanceGM PGA, 59.4% for PGV, 35.4% for SA03, 36.4% for SA10, 48.0% for SA30, and 60.6% for K-NET PGA.

For K-NET PGA, we also screened Japanese and Japan-derived OpenQuake GMMs, including Kanno2006, Zhao2006, and SiMidorikawa1999 variants. The best screened candidate was Kanno2006Shallow, with MAE 0.242 on the balanced held-station split. The metadata plus early-waveform model had MAE 0.111 on the same split. This screening comparison remains limited by missing Vs30, rupture-distance approximation, and unclassified tectonic setting.

A regional GMM readiness audit makes this limitation explicit. InstanceGM balanced held-station records join back to the SeisBench metadata and have complete Vs30 in this split, but focal-mechanism strings occur in only 141 of 5,000 training records and 36 of 1,000 test records. K-NET has source-distance values in the current split, but the approved local package does not include Vs30, rupture-distance, or focal-mechanism fields. The manuscript should describe the current reference layer as screening and baseline comparison.

Split-conformal intervals on the balanced held-station split show target-dependent calibration. Nominal 90% coverage is close for InstanceGM PGV at 0.898 and above nominal for K-NET PGA at 0.925. Other InstanceGM targets under-cover, with coverage from 0.820 to 0.876. The point-prediction gain and the calibration risk should be reported together.

### Residual audits identify inspectable tails

The 10 s combined model reduces mean and tail residuals, then leaves structured cases for inspection. K-NET PGA retains a distance-dependent residual tail. InstanceGM has repeated high-residual records across PGA, PGV, and spectral acceleration. These repeated records are audit targets for waveform quality, target definitions, local site effects, path effects, and metadata consistency.

Waveform-level panels should present selected high-residual cases with P-aligned ZNE waveforms, observed targets, predictions, and residuals. These panels support auditability. Physical attribution should remain cautious until stronger site, rupture, and path metadata are available.

### PNW accelerometer peak-amplitude robustness

PNWAccelerometers provides a supplementary SeisBench accelerometer check. The local HDF5 records component order ENZ and lacks waveform units. The target is full-record peak horizontal waveform amplitude. Publication-ready PGA use requires unit documentation.

Using 5,981 earthquake records, the 1 s and 3 s early-window results support the same early-amplitude pattern under held-event and held-station splits. In held-station evaluation, metadata plus early waveform features reduce MAE by 33.4% at 1 s and 45.7% at 3 s. The 10 s reduction exceeds 90%, which likely reflects small or nearby events where the peak is captured within the window. This result belongs in robustness or supplement material unless waveform units are documented.

### AQ2009GM 096-100 PGA/PGV supplement

AQ2009GM chunks 096-100 provide a supplementary SeisBench ground-motion check with explicit local waveform units. The HDF5 files declare velocity waveforms in m/s with ZNE component order, and the metadata includes official `trace_pga_cmps2` and `trace_pgv_cmps` targets. The valid subset contains 30,737 PGA/PGV records from 5,497 events and 50 stations.

Metadata plus early velocity features reduce log10 MAE for PGA and PGV under held-event and held-station splits. At 3 s, event-held reductions are 46.5% for PGA and 53.2% for PGV. Station-held reductions at 3 s are 72.5% for PGA and 76.6% for PGV across 3,500 test records from 11 held-out station groups. This supplement strengthens the cross-SeisBench evidence layer. The dataset slice is still an AQ2009GM aftershock subset, so the result should remain a supplementary check unless broader coverage is added.

## Discussion

The experiments support a narrow, defensible claim: early post-P waveform windows contain strong-motion information beyond source-path-site metadata, and this information persists across held-event and balanced held-station evaluations. The strongest main evidence comes from InstanceGM PGV, InstanceGM PGA, and K-NET PGA. Spectral acceleration targets also improve, with target-dependent transfer and calibration.

The empirical boundary table should be used to report limits directly. K-NET PGA and InstanceGM PGV have the strongest robust held-out gains. InstanceGM SA10 is the weakest robust held-out gain among the main targets. InstanceGM targets show conformal under-coverage at nominal 90%, so the paper should present uncertainty as a measured station-shift limit.

Residual auditing is part of the scientific contribution. The benchmark does more than report an accuracy gain. It shows where errors remain after early waveform information is added. K-NET distance tails and repeated InstanceGM outliers give concrete records and regimes for follow-up. The conformal results add a calibration layer and show that station shift remains a real risk.

Operational early-warning readiness requires latency, real-time, and prospective validation. Physical attribution of residual structures requires stronger site, rupture, and path metadata. The OpenQuake comparison is a first classical reference, limited by distance and rupture approximations. A fully specified regional GMM, better rupture-distance metadata, or another independent strong-motion dataset with clear units would raise the submission strength.

## Methods Overview

### Data

The unified manifest standardizes record identifiers, dataset splits, waveform paths, component order, P and S picks, source metadata, station metadata, and ground-motion targets. K-NET records were converted from local BSON files into HDF5 waveforms and CSV metadata. K-NET PGA is treated as cm/s2 after NIED unit verification that acceleration waveforms are in gal and 1 gal equals 1 cm/s2.

AQ2009GM chunks 096-100 were evaluated as a supplementary SeisBench ground-motion check outside the unified manifest. The waveform HDF5 files declare measurement velocity and unit m/s. The targets are `trace_pga_cmps2` and `trace_pgv_cmps` from metadata. The check used fixed held-event and held-station splits with zero group overlap.

### Early-window features

Waveforms were aligned to catalog P arrivals. Early windows were extracted at 1 s, 3 s, and 10 s after P arrival. Features included component absolute maximum, RMS, standard deviation, 95th-percentile absolute amplitude, horizontal maximum, vector maximum, and vector RMS. Full-record peak features were excluded from the main ground-motion models.

The early-window peak-capture audit compares `h_early_absmax` with full-record PGA targets in the generated test feature tables. The comparison is used as an interpretation audit. It is not used as a training feature.

The K-NET pre-peak subset audit applies thresholds of 0.5, 0.8, and 1.0 to the ratio between early horizontal peak and observed PGA, then recomputes metadata-only and metadata plus early-waveform errors on the retained records. The 0.8 threshold is the main interpretation check.

### Ground-motion regression

Targets were modeled in log10 units. The main regressor was HistGradientBoostingRegressor with fixed hyperparameters across experiments. Feature sets included median, metadata-only, early-waveform-only, and metadata plus early-waveform models. Metadata features included magnitude, depth, distance, station elevation, Vs30 where available, year, and sample count.

### Held-out evaluation

Held-event splits exclude event groups from training. Held-station splits exclude station groups from training. The balanced held-station split holds out 50 stations per strong-motion dataset and samples 1,000 test records while preserving station coverage. Split-info files record train/test group counts and zero group overlap.

### Classical reference

The attenuation-shaped reference uses Ridge regression on magnitude, log10 hypocentral-distance, depth, and log10 Vs30 where available. It is fitted only on balanced held-station training records and evaluated on the held-station test records. The K-NET split lacks Vs30, so the K-NET reference should be described as an attenuation-shaped baseline without site correction.

The OpenQuake comparison uses BooreEtAl2014 with train-set median bias correction. Source distance is used as an Rjb proxy, rake is fixed at 0, and missing Vs30 is set to 760 m/s. The K-NET Japanese GMM screening uses source distance as an Rrup proxy, missing Vs30 defaults, and train-set median bias correction. These assumptions should be stated in the Methods and figure caption.

The regional GMM readiness audit joins InstanceGM held-station feature records back to SeisBench metadata through `record_id` and `trace_name`, then checks Vs30, focal-mechanism, epicentral-distance, and hypocentral-distance availability. K-NET readiness is checked from the approved local feature tables.

### Uncertainty and residual analysis

Split-conformal intervals use a proper-training and calibration split within the balanced held-station training features. Residuals are defined as predicted log10 target minus observed log10 target. Residual audits evaluate binned behavior by magnitude, distance, depth, station variables, and early waveform amplitude, then select high-residual records for waveform-level panels.

## Data and Code Availability Draft

The benchmark uses public waveform archives. STEAD, InstanceGM, Iquique, AQ2009GM, and PNWAccelerometers are accessed through SeisBench. K-NET waveforms are public data from NIED and were converted locally from the approved BSON package into HDF5 with explicit component mapping. The paper should not redistribute raw waveforms unless each source license permits it. The reproducible release should include the unified manifest schema, train-test split files, feature tables where licensing allows, figure tables, and all analysis scripts.

Minimum release files:

- `work/scripts/build_unified_manifest.py`
- `work/scripts/convert_knet_bson.py`
- `work/scripts/run_ground_motion_baseline.py`
- `work/scripts/run_ground_motion_heldout_baseline.py`
- `work/scripts/audit_early_window_peak_capture.py`
- `work/scripts/audit_knet_prepeak_subset.py`
- `work/scripts/run_attenuation_reference.py`
- `work/scripts/run_openquake_pga_reference.py`
- `work/scripts/run_knet_japan_gmm_reference.py`
- `work/scripts/run_conformal_intervals.py`
- `work/scripts/analyze_ground_motion_residuals.py`
- `work/scripts/run_aq2009gm_chunk_baseline.py`
- `work/scripts/run_pnw_accelerometer_peak_baseline.py`
- `work/scripts/verify_nc_evidence_package.py`

Minimum evidence tables:

- `work/unified_manifest/unified_manifest.csv.gz`
- `outputs/figure2_early_window_performance.csv`
- `outputs/figure3_heldout_generalization.csv`
- `outputs/figure4_classical_uncertainty.csv`
- `outputs/figure6_phase_label_audit.csv`
- `outputs/early_window_peak_capture_audit.csv`
- `outputs/knet_prepeak_subset_audit.csv`
- `work/ground_motion_balanced_station_10s/conformal_intervals.csv`
- `work/aq2009gm_chunks096-100_station12_baseline/aq2009gm_chunks096-100_comparison.csv`

## Figure Captions Draft

### Figure 1. Cross-dataset waveform-task benchmark

Dataset-task matrix showing STEAD, InstanceGM, Iquique, K-NET, and PNWAccelerometers supplement status. Panels summarize record counts, available phase labels, available strong-motion targets, and provenance notes. Current file: `outputs/figures/figure1_dataset_task_matrix.png`.

### Figure 2. Early-window strong-motion information

Performance across 1 s, 3 s, and 10 s post-P windows. Panels show MAE reduction, q95 residual reduction, combined-model MAE, and combined-model R2. Current file: `outputs/figures/figure2_early_window_performance.png`.

### Figure 3. Held-out generalization and split distribution

Held-event and balanced held-station performance for InstanceGM and K-NET. The distribution audit shows magnitude, distance, and PGA train/test coverage, including the farther and weaker InstanceGM station-held test set. Current file: `outputs/figures/figure3_heldout_generalization.png`.

### Figure 4. Classical reference and uncertainty

Bias-corrected OpenQuake BooreEtAl2014 comparison and split-conformal interval results. The figure pairs point-prediction improvement with station-shift calibration limits. Current file: `outputs/figures/figure4_classical_uncertainty.png`.

### Figure 5. Residual and waveform audit

Residual diagnostics and high-residual waveform examples. Panels show distance-dependent K-NET PGA tails and repeated InstanceGM residual cases across targets. Current file: `outputs/figures/figure5_residual_waveform_audit.png`.

### Figure 6. Phase-label transfer audit

Cross-dataset P and S picking errors, q95 tails, and missing-pick rates from pretrained PhaseNet and EQTransformer models. The figure supports P alignment and shows dataset-dependent S-phase limits. Current file: `outputs/figures/figure6_phase_label_audit.png`.

### Supplementary Figure. PNW accelerometer peak-amplitude check

Held-event and held-station peak-amplitude results for PNWAccelerometers at 1 s, 3 s, and 10 s. The caption should state that local waveform units are not encoded. The target is peak horizontal waveform amplitude. Official PGA use requires unit documentation.

### Supplementary Figure. AQ2009GM 096-100 early velocity check

Held-event and held-station PGA/PGV results for AQ2009GM chunks 096-100 at 1 s, 3 s, and 10 s. The caption should state that waveforms are velocity in m/s, targets are metadata PGA/PGV, and the result is a five-chunk aftershock supplement. Current file: `outputs/figures/ground_motion_audit/aq2009gm_chunks096-100_station12_panel.png`.

## Claim Boundaries

Use these claims:

1. Early post-P waveform features improve strong-motion inference beyond source-path-site metadata.
2. The gain persists under held-event and balanced held-station splits.
3. OpenQuake BooreEtAl2014 gives a useful first classical reference with stated approximations.
4. Residual and conformal analyses expose remaining station-shift and target-dependent risk.
5. Phase-picking audits support P alignment and expose dataset-dependent label transfer.
6. AQ2009GM 096-100 provides a supplementary check with explicit velocity units and official PGA/PGV metadata targets.

Keep these limits explicit:

1. No earthquake prediction claim.
2. No operational early-warning claim.
3. No foundation-model superiority claim.
4. No physical causality claim from residual correlations alone.
5. No claim of full superiority over a fully specified regional GMPE/GMM.
6. No official PGA claim for PNWAccelerometers without unit documentation.
7. No full external-validation claim from a five-chunk AQ2009GM subset.

## Remaining Work Before Submission

1. Redraw main figures in one consistent journal style.
2. Add exact software, data, split, and random-seed provenance to Methods.
3. Decide whether AQ2009GM expands beyond chunks 096-100.
4. Decide whether PNWAccelerometers stays in supplement or receives documented unit support.
5. Add a stronger independent strong-motion dataset or fully specified regional GMPE/GMM comparison if rupture class, rupture distance, and site terms become available.
6. Audit manuscript language to keep claims direct and evidence-bounded.
