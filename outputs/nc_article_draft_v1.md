# Cross-regional predictability limits of strong shaking from the first seconds of P waves

Article draft v1

Evidence status: generated from verified local outputs through `outputs/nc_evidence_verification_report.md`.

## Abstract

Rapid earthquake hazard assessment depends on the information available before strong shaking is fully recorded. We build a public early-window benchmark from STEAD, InstanceGM, Iquique, and a locally converted K-NET archive to measure how final strong shaking becomes predictable from 1 s, 3 s, and 10 s post-P waveform windows. The benchmark contains 2,460,425 manifest records and 22,119 complete K-NET ZNE records with verified acceleration units. Metadata plus early waveform features improve prediction of PGA, PGV, and spectral acceleration beyond source-path-site metadata across random, held-event, and balanced held-station splits. In balanced held-station evaluation, log10 MAE decreases by 35.5% for InstanceGM PGA, 52.6% for InstanceGM PGV, and 49.9% for K-NET PGA. Bias-corrected OpenQuake and Japanese GMM screening references support the same pattern within stated metadata limits. Split-conformal intervals show target-dependent calibration under station shift, with under-coverage for InstanceGM targets and 0.925 coverage for K-NET PGA at nominal 90%. Residual and phase-label audits identify distance tails, repeated high-residual records, and label-transfer limits. These results define a reproducible benchmark for early strong-motion predictability and its uncertainty boundaries.

## Introduction

The first seconds after the P arrival carry direct observations of a developing earthquake record. These observations can encode source strength, path attenuation, site response, and amplitude growth before the full shaking history is available. Strong-motion targets such as peak ground acceleration, peak ground velocity, and spectral acceleration connect this early information to engineering and hazard workflows.

Public seismic archives now contain enough labeled waveforms to test this question across regions and sensor classes. The main challenge is provenance. Archives differ in waveform units, component conventions, phase-label definitions, source and station metadata, and ground-motion targets. A benchmark for early strong-motion predictability must keep these differences explicit while separating metadata effects, split leakage, waveform information, and uncertainty calibration.

We assemble a unified benchmark from STEAD, InstanceGM, Iquique, and K-NET. STEAD and Iquique provide phase-label transfer settings, InstanceGM provides broad ground-motion targets, and K-NET provides an independent strong-motion archive after local conversion from BSON files. We align waveforms to catalog P arrivals, extract early windows at 1 s, 3 s, and 10 s, and compare metadata-only models with metadata plus early-waveform models. We evaluate random, held-event, and balanced held-station splits, then compare against attenuation-shaped and OpenQuake ground-motion references. The result is an empirical boundary: early waveform windows improve point prediction, while held-station residuals and conformal coverage show where predictability remains limited in the current data.

## Results

### A public waveform-task benchmark

The unified manifest contains 2,460,425 records across STEAD, InstanceGM, Iquique, and K-NET. InstanceGM contributes 1,159,223 ground-motion records with PGA, PGV, and spectral acceleration targets. K-NET contributes 22,119 locally converted complete ZNE strong-motion records. The K-NET conversion maps UD to Z, NS to N, and EW to E. Local unit provenance follows NIED documentation: acceleration waveforms are in gal, equivalent to cm/s2.

This benchmark connects two audit layers. The phase-label layer checks whether P-aligned waveform extraction is stable across datasets. The strong-motion layer measures how much early post-P waveform windows improve final ground-motion targets beyond source-path-site metadata.

### Phase-label audits support P-aligned windows

A 1,000-record-per-dataset phase audit evaluated pretrained PhaseNet(STEAD) and EQTransformer(STEAD) models against catalog P and S labels. STEAD remained stable, with PhaseNet P MAE of 0.035 s and S MAE of 0.082 s. K-NET P picks were also stable, with PhaseNet P MAE of 0.056 s. K-NET S picks showed a wider tail, with q95 near 1.05 s. InstanceGM had the largest missing-pick problem, especially for S arrivals. Iquique had low P missing rates and larger S errors.

The phase audit supports use of catalog P arrivals for early-window extraction and identifies label-domain limits that are separate from ground-motion target prediction.

### Early waveform windows improve strong-motion prediction

In random splits, metadata plus early waveform features improved every main strong-motion target. At 10 s after P arrival, InstanceGM PGA MAE decreased from 0.299 to 0.207 log10 units, a 30.6% reduction. InstanceGM PGV decreased from 0.298 to 0.165, a 44.7% reduction. InstanceGM spectral acceleration also improved: 19.0% for SA03, 26.8% for SA10, and 20.9% for SA30. K-NET PGA decreased from 0.217 to 0.105, a 51.8% reduction.

The signal appears before the 10 s window. At 1 s, MAE reductions are 16.0% for InstanceGM PGA, 28.1% for InstanceGM PGV, and 9.4% for K-NET PGA. At 3 s, reductions increase to 18.9%, 31.9%, and 17.9%, respectively. The 10 s window provides stronger information and a higher chance that small or nearby records have already developed target-scale amplitudes.

A peak-capture audit clarifies this interpretation. In K-NET, 69.8% of 1 s test windows and 94.7% of 10 s test windows have early horizontal peak amplitude at least 0.8 times the PGA target. InstanceGM early amplitudes and PGA targets are not on a directly comparable local scale, so direct early-to-target amplitude ratios are used only as an interpretation audit for K-NET.

The K-NET pre-peak subset audit keeps the lead-time claim grounded. Filtering records where the early horizontal peak remains below 80% of observed PGA leaves 302 records at 1 s and 255 records at 3 s. Within this subset, early waveform features reduce MAE from 0.238 to 0.205 at 1 s and from 0.239 to 0.197 at 3 s. These reductions are 13.8% and 17.9%.

### Held-event and held-station splits preserve the gain

Held-event splits exclude selected events from training. In this evaluation, the 10 s combined model improves every main target. MAE reductions are 38.8% for InstanceGM PGA, 50.4% for InstanceGM PGV, 22.5% for SA03, 24.7% for SA10, 24.9% for SA30, and 54.5% for K-NET PGA. Group overlap is zero.

Balanced held-station splits exclude selected stations from training and hold out 50 stations per main strong-motion dataset. This test also preserves the gain across all main targets. MAE reductions are 35.5% for InstanceGM PGA, 52.6% for InstanceGM PGV, 26.0% for SA03, 20.9% for SA10, 27.8% for SA30, and 49.9% for K-NET PGA. Group overlap is zero.

The held-station split contains real distribution shift. InstanceGM test records are farther and weaker than the training records: median distance increases from 44.27 km to 70.61 km, and median log10 PGA decreases from -1.68 to -2.11. K-NET train and test distributions overlap more closely for distance and PGA. These audits support a split-aware interpretation of generalization.

### Classical references and uncertainty define empirical boundaries

We fit an attenuation-shaped ridge reference using magnitude, log10 hypocentral-distance, depth, and log10 Vs30 where available. InstanceGM has Vs30 in the balanced held-station split. K-NET lacks Vs30 in the approved local package, so its reference is an attenuation-shaped baseline without site correction. The metadata plus early-waveform model improves over this reference across all balanced held-station targets, with relative MAE reductions from 17.5% to 51.6%.

We also evaluate bias-corrected OpenQuake BooreEtAl2014 as a classical reference. The comparison uses source distance as an Rjb proxy, rake fixed at 0, and Vs30 set to 760 m/s where missing. Combined early-waveform models reduce MAE relative to this reference by 36.6% for InstanceGM PGA, 59.4% for PGV, 35.4% for SA03, 36.4% for SA10, 48.0% for SA30, and 60.6% for K-NET PGA.

For K-NET PGA, a Japanese GMM screening evaluates Kanno2006, Zhao2006, and SiMidorikawa1999 variants under the available metadata. The best screened candidate is Kanno2006Shallow, with MAE 0.242 on the balanced held-station split. The metadata plus early-waveform model reaches MAE 0.111 on the same split. This screening is limited by missing Vs30, rupture-distance approximation, and tectonic-class assumptions.

The regional GMM readiness audit makes the reference boundary explicit. InstanceGM records in the balanced held-station split join back to SeisBench metadata and have complete Vs30. Focal-mechanism strings occur in 141 of 5,000 training records and 36 of 1,000 test records. K-NET has source-distance values in the current split, while the approved local package lacks Vs30, rupture-distance, and focal-mechanism fields.

Split-conformal intervals show that point-prediction gain and calibrated uncertainty diverge under station shift. At nominal 90% coverage, K-NET PGA reaches 0.925. InstanceGM PGV reaches 0.898. Other InstanceGM targets under-cover, with coverage from 0.820 to 0.876. The empirical predictability boundary is strongest for K-NET PGA and InstanceGM PGV, and weakest among the main targets for InstanceGM SA10.

### Residual audits expose remaining structure

Residual diagnostics identify structured tails after early waveform information is added. K-NET PGA retains a distance-dependent residual tail. InstanceGM contains repeated high-residual records across PGA, PGV, and spectral acceleration targets. These records provide inspectable targets for waveform quality, target definitions, local site effects, path effects, and metadata consistency.

The residual panels show P-aligned ZNE waveforms, observed targets, predictions, and residuals for selected high-residual cases. This audit layer turns the remaining error into a documented failure set for follow-up data curation and physical interpretation.

### Supplementary cross-dataset checks

PNWAccelerometers provides a supplementary accelerometer check. The local HDF5 records component order ENZ and lacks waveform units. The target is full-record peak horizontal waveform amplitude. Across 5,981 earthquake records, metadata plus early waveform features reduce held-station MAE by 33.4% at 1 s and 45.7% at 3 s. The 10 s reduction exceeds 90%, consistent with peak capture in small or nearby events. Official PGA use requires unit documentation.

AQ2009GM chunks 096-100 provide a separate SeisBench ground-motion check with explicit units. The HDF5 files declare velocity waveforms in m/s with ZNE component order, and the metadata provides `trace_pga_cmps2` and `trace_pgv_cmps` targets. The valid subset contains 30,737 PGA/PGV records from 5,497 events and 50 stations. Metadata plus early velocity features reduce log10 MAE for PGA and PGV under held-event and held-station splits. At 3 s, event-held reductions are 46.5% for PGA and 53.2% for PGV. Station-held reductions are 72.5% for PGA and 76.6% across 3,500 test records from 11 held-out station groups. This five-chunk aftershock subset is supplementary evidence.

## Discussion

This study turns early strong-motion predictability into a measured benchmark. Public waveform archives support a reproducible workflow that links data provenance, P-aligned early windows, held-out evaluation, classical references, uncertainty calibration, and residual auditing. Across the main strong-motion targets, early waveform features add information beyond source-path-site metadata. The gain survives held-event and balanced held-station tests with zero group overlap.

The strongest main evidence is K-NET PGA and InstanceGM PGV. K-NET PGA has a 49.9% robust held-out gain and 0.925 conformal coverage at nominal 90%. InstanceGM PGV has a 50.4% robust held-out gain and near-nominal coverage at 0.898. InstanceGM spectral acceleration targets improve as well, with lower robust held-out gains and stronger under-coverage. These target-level differences are the predictability boundary measured by the current benchmark.

The classical reference layer supports the scientific interpretation while keeping the metadata limits visible. Bias-corrected OpenQuake and Japanese GMM screening references are useful comparators under the available fields. A fully specified regional GMM comparison needs stronger rupture-distance, site, and focal-mechanism metadata than the current local package provides.

The uncertainty results are central to the paper. Point prediction improves for every main target, while conformal coverage remains target-dependent under station shift. This pattern supports reporting early waveform information and uncertainty boundaries together. Residual audits then identify the cases that still fail after metadata and early waveform features are combined.

Operational early-warning deployment requires latency, telemetry, prospective validation, and real-time decision rules. Physical attribution of residual structures requires richer site, rupture, and path metadata. The present contribution is a public, reproducible measurement of early strong-motion information and its current empirical limits.

## Methods

### Data sources and manifest

The unified manifest standardizes record identifiers, dataset names, waveform paths, component order, P and S picks, source metadata, station metadata, and ground-motion targets. STEAD, InstanceGM, Iquique, AQ2009GM, and PNWAccelerometers are accessed through SeisBench. K-NET is converted locally from the approved BSON package into HDF5 waveforms and CSV metadata.

K-NET conversion maps UD, NS, and EW components to Z, N, and E. Complete records require all three components. K-NET acceleration targets use cm/s2 after verifying that NIED acceleration waveforms are in gal.

### Early-window features

Waveforms are aligned to catalog P arrivals. Early windows are extracted at 1 s, 3 s, and 10 s after P arrival. Features include component absolute maximum, RMS, standard deviation, 95th-percentile absolute amplitude, horizontal maximum, vector maximum, and vector RMS. Full-record peak features are excluded from the main models.

The early-window peak-capture audit compares early horizontal maximum amplitude with full-record PGA targets in generated test feature tables. The K-NET pre-peak subset audit filters records by the ratio of early horizontal peak to observed PGA at thresholds of 0.5, 0.8, and 1.0, then recomputes metadata-only and metadata plus early-waveform errors.

### Regression models

Ground-motion targets are modeled in log10 units. The main regressor is HistGradientBoostingRegressor with fixed settings across experiments. Feature sets include median-only, metadata-only, early-waveform-only, and metadata plus early-waveform models. Metadata features include magnitude, depth, distance, station elevation, Vs30 where available, year, and sample count.

### Split design

Random splits provide the first information-gain measurement. Held-event splits exclude event groups from training. Held-station splits exclude station groups from training. The balanced held-station split holds out 50 stations per main strong-motion dataset and samples 1,000 test records while preserving station coverage. Split-info files record train groups, test groups, and group overlap.

### Classical references

The attenuation-shaped reference uses Ridge regression on magnitude, log10 hypocentral distance, depth, and log10 Vs30 where available. It is fitted on balanced held-station training records and evaluated on held-station test records. The K-NET reference lacks site correction because Vs30 is absent from the approved local feature tables.

OpenQuake BooreEtAl2014 is evaluated with train-set median bias correction. Source distance is used as an Rjb proxy, rake is fixed at 0, and missing Vs30 is set to 760 m/s. K-NET Japanese GMM screening uses source distance as an Rrup proxy, missing Vs30 defaults, and train-set median bias correction.

### Uncertainty and residual analysis

Split-conformal intervals use a proper-training and calibration split inside the balanced held-station training records. Reported coverage is evaluated on held-station test records. Residuals are predicted log10 target minus observed log10 target. Residual audits evaluate binned behavior by magnitude, distance, depth, station variables, and early waveform amplitude, then select high-residual records for waveform-level panels.

### Supplementary datasets

PNWAccelerometers is used as an accelerometer peak-amplitude supplement. Its local HDF5 files encode component order and lack waveform unit metadata, so its target is treated as peak horizontal waveform amplitude.

AQ2009GM chunks 096-100 are used as a SeisBench PGA/PGV supplement. Local HDF5 metadata declares velocity waveforms in m/s. Targets are `trace_pga_cmps2` and `trace_pgv_cmps`. Held-event and held-station splits have zero group overlap.

## Data and Code Availability

The benchmark uses public waveform archives. STEAD, InstanceGM, Iquique, AQ2009GM, and PNWAccelerometers are accessed through SeisBench. K-NET waveforms are public data from NIED and were converted locally from the approved BSON package into HDF5 with explicit component mapping. Raw waveform redistribution should follow the license and access rules of each source archive.

The reproducible release should include the unified manifest schema, split files, generated figure tables, methods scripts, evidence verifier, and derived feature tables where licenses allow. The current local evidence package is verified by `work/scripts/verify_nc_evidence_package.py`.

## Figure Legends

### Figure 1. Cross-dataset waveform-task benchmark

Dataset-task matrix for STEAD, InstanceGM, Iquique, K-NET, and supplementary PNWAccelerometers. Panels summarize record counts, available phase labels, strong-motion targets, and provenance notes.

### Figure 2. Lead-time-dependent early waveform information

Performance across 1 s, 3 s, and 10 s post-P windows. Panels show MAE reduction, q95 residual reduction, combined-model MAE, and combined-model R2 for InstanceGM and K-NET targets.

### Figure 3. Held-out generalization and split distribution

Held-event and balanced held-station performance for InstanceGM and K-NET. Distribution panels summarize magnitude, distance, and PGA train-test coverage for the held-station split.

### Figure 4. Classical reference and uncertainty

Bias-corrected OpenQuake BooreEtAl2014 comparison and split-conformal interval results. Panels pair point-prediction improvement with station-shift calibration limits.

### Figure 5. Residual and waveform audit

Residual diagnostics and high-residual waveform examples. Panels show distance-dependent K-NET PGA tails and repeated InstanceGM residual cases across PGA, PGV, and spectral acceleration.

### Figure 6. Phase-label transfer audit

Cross-dataset P and S picking errors, q95 tails, and missing-pick rates from pretrained PhaseNet and EQTransformer models. The audit supports P alignment and identifies dataset-dependent S-phase limits.

### Supplementary Figure 1. PNW accelerometer peak-amplitude check

Held-event and held-station peak-amplitude results for PNWAccelerometers at 1 s, 3 s, and 10 s. The target is peak horizontal waveform amplitude.

### Supplementary Figure 2. AQ2009GM 096-100 early velocity check

Held-event and held-station PGA/PGV results for AQ2009GM chunks 096-100 at 1 s, 3 s, and 10 s. Waveforms are velocity in m/s, targets are metadata PGA/PGV, and the result is a five-chunk aftershock supplement.
