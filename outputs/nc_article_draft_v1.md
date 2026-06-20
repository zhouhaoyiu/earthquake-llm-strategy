# Cross-regional predictability limits of strong shaking from the first seconds of P waves

Article draft v2. Evidence status: generated from verified local outputs through `outputs/nc_evidence_verification_report.md`.

## Abstract

Earthquake early warning depends on how much final shaking can be inferred from the first seconds after P arrival. We build a public early-window benchmark from STEAD, InstanceGM, Iquique, and a locally converted K-NET archive, then add AQ2009GM full-manifest chunk-streaming and local ESM compact features as independent ground-motion checks. The benchmark contains 2,460,425 manifest records and 22,119 complete K-NET ZNE records with verified acceleration units. Metadata plus early waveform features improve PGA, PGV, and spectral-acceleration prediction across random, held-event, and balanced held-station splits. In balanced held-station evaluation, log10 MAE decreases by 35.5% for InstanceGM PGA, 52.6% for InstanceGM PGV, and 49.9% for K-NET PGA. Bias-corrected OpenQuake and Japanese GMM screening references support the same pattern within stated metadata limits. Split-conformal intervals show target-dependent calibration under station shift. Four-domain early-waveform-only transfer gives a direct predictability boundary: median zero-shot MAE penalties rise from 2.25x at 1 s to 4.27x at 10 s relative to target-domain training. These results define a reproducible benchmark for early strong-motion predictability and its uncertainty boundaries.

## Introduction

The first seconds after the P arrival carry observations of the developing ground-motion record. These observations can encode source strength, path attenuation, site response, and amplitude growth before the full shaking history is available. PGA, PGV, and spectral acceleration connect this early information to engineering and hazard workflows.

Public seismic archives are now large enough to test early strong-motion predictability across regions and sensor systems. The problem is provenance. Archives differ in waveform units, component conventions, phase-label definitions, source and station metadata, and ground-motion targets. A useful benchmark must keep those differences visible while separating metadata effects, split leakage, waveform information, and uncertainty calibration.

We assemble a unified benchmark from STEAD, InstanceGM, Iquique, and K-NET. STEAD and Iquique provide phase-label transfer settings. InstanceGM provides broad ground-motion targets. K-NET provides an independent strong-motion archive after local BSON conversion. We align records to catalog P arrivals, extract early-window features, compare metadata-only and waveform-informed models, test held-event and held-station generalization, compare against classical references, and measure cross-region transfer across InstanceGM, K-NET, AQ2009GM, and ESM.

## Results

### A Public Waveform-Task Benchmark

The unified manifest contains 2,460,425 records. InstanceGM contributes 1,159,223 ground-motion records with PGA, PGV, and spectral-acceleration targets. K-NET contributes 22,119 locally converted complete ZNE strong-motion records. K-NET conversion maps UD to Z, NS to N, and EW to E. Local unit provenance follows NIED documentation: acceleration waveforms are in gal, equivalent to cm/s2.

The phase-label layer checks P-aligned waveform extraction. In a 1,000-record-per-dataset audit, PhaseNet P picks remain stable for STEAD and K-NET, with P MAE of 0.035 s and 0.056 s. S picks show larger dataset-dependent errors, especially for InstanceGM. This separates P-window alignment from broader phase-label transfer limits.

### Early Waveform Windows Add Strong-Motion Information

In random splits, metadata plus early waveform features improve every main strong-motion target. At 10 s after P arrival, InstanceGM PGA MAE decreases from 0.299 to 0.207 log10 units, InstanceGM PGV decreases from 0.298 to 0.165, and K-NET PGA decreases from 0.217 to 0.105.

The signal appears before 10 s. Balanced held-station scans at 1, 2, 3, 5, and 10 s show positive gains for every main target. InstanceGM PGA improves from 23.9% at 1 s to 31.2% at 5 s and 35.5% at 10 s. InstanceGM PGV improves from 40.1% at 1 s to 45.4% at 5 s and 52.6% at 10 s. K-NET PGA improves from 11.3% at 1 s to 23.3% at 5 s and 49.9% at 10 s.

Peak-capture audits constrain the interpretation. In K-NET, 69.8% of 1 s test windows and 94.7% of 10 s test windows have early horizontal peak amplitude at least 0.8 times the PGA target. A K-NET pre-peak subset keeps records where early horizontal peak remains below 80% of observed PGA. In that subset, early waveform features still reduce MAE by 13.8% at 1 s and 17.9% at 3 s.

### Held-Out Splits Preserve the Gain

Held-event splits exclude selected events from training. At 10 s, the combined model improves every main target, with MAE reductions of 38.8% for InstanceGM PGA, 50.4% for InstanceGM PGV, and 54.5% for K-NET PGA.

Balanced held-station splits exclude selected stations from training and hold out 50 stations per main strong-motion dataset. The gain persists across all main targets. MAE reductions are 35.5% for InstanceGM PGA, 52.6% for InstanceGM PGV, 26.0% for SA03, 20.9% for SA10, 27.8% for SA30, and 49.9% for K-NET PGA. Group overlap is zero.

The held-station split contains real distribution shift. InstanceGM test records are farther and weaker than the training records: median distance increases from 44.27 km to 70.61 km, and median log10 PGA decreases from -1.68 to -2.11. K-NET train and test distributions overlap more closely for distance and PGA. The split audit supports a measured generalization claim, not a distribution-matched transfer claim.

### Classical References and Uncertainty Define Boundaries

An attenuation-shaped ridge reference uses magnitude, log10 hypocentral-distance, depth, and log10 Vs30 where available. The metadata plus early-waveform model improves over this reference across all balanced held-station targets, with relative MAE reductions from 17.5% to 51.6%.

Bias-corrected OpenQuake BooreEtAl2014 gives a classical reference under limited metadata. It uses source distance as an Rjb proxy, rake fixed at 0, and Vs30 set to 760 m/s where missing. Combined early-waveform models reduce MAE relative to this reference by 36.6% for InstanceGM PGA, 59.4% for PGV, 35.4% for SA03, 36.4% for SA10, 48.0% for SA30, and 60.6% for K-NET PGA.

K-NET Japanese GMM screening evaluates Kanno2006, Zhao2006, and SiMidorikawa1999 variants. The best screened candidate is Kanno2006Shallow, with MAE 0.242 on the balanced held-station split. The metadata plus early-waveform model reaches MAE 0.111. This is a screening comparison. A fully specified regional GMPE/GMM comparison needs curated rupture distance, site terms, and tectonic or focal-mechanism metadata.

Split-conformal intervals show target-dependent calibration under station shift. At nominal 90% coverage, K-NET PGA reaches 0.925 and InstanceGM PGV reaches 0.898. Other InstanceGM targets under-cover, with coverage from 0.820 to 0.876. Source-domain conformal intervals under-cover target domains in cross-region transfer, with median 90% coverage of 0.468 at 2 s and 0.298 at 5 s. Target-offset conformal calibration restores coverage to about 0.90 with wider intervals.

### Residual and Supplementary Audits Locate Failure Modes

Residual diagnostics show remaining structure after early waveform information is added. K-NET PGA retains a distance-dependent residual tail. InstanceGM contains repeated high-residual records across PGA, PGV, and spectral-acceleration targets. The main Figure 5 now presents residual diagnostics; waveform case panels are kept as an extended audit figure.

AQ2009GM provides a separate SeisBench ground-motion check with official metadata targets. Full-manifest chunk streaming covers all 254 local AQ2009GM chunks, extracts compact early-window velocity features and PGA/PGV targets, and deletes raw HDF5 and metadata files after feature extraction. The retained feature tables contain 345,226 valid PGA/PGV records from 60,310 events and 66 stations. At 5 s, metadata plus early velocity features reduce held-station MAE by 55.8% for PGA and 71.9% for PGV.

ESM provides an external European strong-motion check from local ASCII zip packages. The compact feature table covers 951 zip files, 134,250 early-window rows, 861 events, and 1,568 stations. Local ESM headers do not provide explicit P arrivals, so windows use a theoretical P-onset estimate. A Vp sensitivity audit shows that changing Vp from 6.0 to 5.5 km/s delays onset by a median 2.517 s, and changing it to 6.5 km/s advances onset by a median 2.130 s. Retained-window validity remains above 0.994 across tested windows. ESM supports external-domain validation and transfer analysis; catalog-P lead-time claims stay tied to datasets with explicit P labels.

### Cross-Region Transfer Measures the Predictability Boundary

Early-waveform-only transfer uses waveform features and excludes distance, magnitude, site variables, event identifiers, and station identifiers. The within-domain baseline trains and tests inside the target domain. The zero-shot setting trains on a source domain and evaluates on the target-domain test split. Offset-calibrated transfer applies one scalar correction estimated from the target-domain training split.

All cross-domain rows have higher MAE than target-domain training. In the four-domain synthesis across InstanceGM, K-NET, AQ2009GM, and ESM, median zero-shot penalties are 2.25x at 1 s, 2.65x at 2 s, 2.98x at 3 s, 3.38x at 5 s, and 4.27x at 10 s. Target-train offset calibration reduces these medians to 1.40x, 1.55x, 1.67x, 1.85x, and 2.46x. External transfer into ESM remains penalized at 10 s after offset calibration: the best external-to-ESM ratio is 2.53x for PGA and 1.58x for PGV.

This pattern defines the central boundary. Early waveform information is useful inside curated domains. Direct transfer across regions and measurement systems remains penalized, and uncertainty intervals calibrated in the source domain do not transport reliably to the target domain.

## Discussion

This study turns early strong-motion predictability into a public measurement problem. Across InstanceGM and K-NET, early waveform features add information beyond source-path-site metadata. The gain survives held-event and balanced held-station tests with zero group overlap. AQ2009GM and ESM add independent checks with explicit provenance limits.

The strongest main evidence is K-NET PGA and InstanceGM PGV. K-NET PGA has a 49.9% robust held-out gain and 0.925 conformal coverage at nominal 90%. InstanceGM PGV has a 52.6% held-station gain and near-nominal coverage at 0.898. Spectral-acceleration targets improve with lower robust gains and stronger under-coverage.

The paper should report point prediction and uncertainty together. Better MAE does not imply calibrated warning intervals under station or regional shift. Source-domain conformal calibration under-covers target domains, and target-offset calibration restores coverage by widening intervals. The empirical boundary is the result.

Operational early-warning deployment requires latency, telemetry, prospective validation, and real-time decision rules. Physical attribution of residual structures requires richer site, rupture, and path metadata. The present contribution is a reproducible benchmark of early strong-motion information and its current empirical limits.

## Methods Summary

The benchmark uses SeisBench archives for STEAD, InstanceGM, Iquique, AQ2009GM, and PNWAccelerometers, a local K-NET BSON conversion, and local ESM ASCII zip packages. K-NET conversion maps UD/NS/EW to Z/N/E and uses NIED unit provenance for gal-to-cm/s2 acceleration. ESM compact features are generated without modifying the original zip files.

Early-window features are extracted at 1, 2, 3, 5, and 10 s where retained feature tables are available. Features include component absolute maximum, RMS, standard deviation, 95th-percentile absolute amplitude, horizontal maximum, vector maximum, and vector RMS. Full-record peak features are excluded from predictive feature sets.

Targets are modeled in log10 units. The main regressor is `HistGradientBoostingRegressor`. Random splits use seed 19. Held-event and held-station strong-motion splits use seed 31, with a +101 offset for station holdout. AQ2009GM uses seed 43. ESM uses seed 71. PNWAccelerometers uses seed 83. Phase-audit sampling uses seed 7. Conformal intervals use seed 17. Boundary sensitivity repeats seeds 17, 59, and 101.

Analyses were run in the local `zhy` environment with Python 3.12.13, numpy 2.4.4, pandas 3.0.2, scikit-learn 1.8.0, matplotlib 3.10.8, Pillow 12.2.0, h5py 3.16.0, SeisBench 0.11.5, and OpenQuake engine 3.25.1.

## Data and Code Availability

Raw waveform redistribution should follow each source archive license. SeisBench caches are read from `/Users/yojironoda/.seisbench/datasets`. K-NET is read from `/Users/yojironoda/Downloads/s7rk7bj3zn-1/knet_1530`. ESM zip packages are read from `/Users/yojironoda/Documents/New project 2/outputs/strong_motion_downloads/欧洲_ESM`. The reproducible release should include scripts, split files, figure tables, verifier output, and derived feature tables where licensing allows.

## Figure Legends

### Figure 1. Cross-Dataset Waveform-Task Benchmark

Dataset-task matrix for STEAD, InstanceGM, Iquique, K-NET, and supplementary PNWAccelerometers. Panels summarize record counts and task availability.

### Figure 2. Lead-Time-Dependent Early Waveform Information

Performance across 1 s, 3 s, and 10 s post-P windows. Panels show MAE reduction, q95 residual reduction, combined-model MAE, and combined-model R2.

### Figure 3. Held-Out Generalization and Split Distribution

Held-event and balanced held-station performance for InstanceGM and K-NET. Distribution panels summarize magnitude, distance, and PGA train-test coverage.

### Figure 4. Classical Reference and Uncertainty

Bias-corrected OpenQuake BooreEtAl2014 comparison and split-conformal interval results. Panels pair point-prediction improvement with station-shift calibration limits.

### Figure 5. Residual Diagnostics

Residual diagnostics for the combined strong-motion models. Waveform case audits are reported as an extended figure.

### Figure 6. Phase-Label Transfer Audit

Cross-dataset P and S picking errors, q95 tails, and missing-pick rates from pretrained PhaseNet and EQTransformer models.

### Figure 7. Predictability-Boundary Synthesis

Four-axis summary of within-domain information gain, cross-region transfer penalty, conformal coverage loss, and strong-motion tail underprediction.

### Extended Data Figure. Waveform Case Audit

Repeated InstanceGM high-residual records and K-NET PGA high-residual waveform cases.

### Supplementary Table. ESM P-Onset Sensitivity

Theoretical P-onset sensitivity for Vp 5.5, 6.0, and 6.5 km/s in the retained ESM compact feature table.
