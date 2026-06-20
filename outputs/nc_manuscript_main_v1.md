# Cross regional limits on predicting strong shaking from early P waves

[Author names]

[Affiliations]

Correspondence: [corresponding author email]

## Abstract

Earthquake early warning must estimate damaging ground motion before the strongest shaking reaches exposed sites. The first seconds of P waves carry source and path information, yet their usable limit for cross-regional strong-motion prediction remains poorly quantified with public data. We build an event-station benchmark from public strong-motion records and test how much the first 1, 2, 3, 5 and 10 s after the P arrival reduce uncertainty in peak ground acceleration, peak ground velocity and spectral acceleration. Across 2,460,425 manifest records, held-station tests show consistent error reductions for early-waveform models compared with source-path baselines, including 35.5% for InstanceGM peak acceleration, 52.6% for InstanceGM peak velocity and 49.9% for K-NET peak acceleration at 10 s. Paired bootstrap intervals remain positive across six targets. The gain persists within source-path support and in the strongest 5% of test motions, while some tail underprediction remains. Cross-regional transfer from Japan to Europe and Australia degrades sharply without target calibration, and conformal intervals trained in the source region under-cover the target region. These results define a measurable predictability boundary for early P-wave strong-shaking forecasts.

## Introduction

Earthquake early warning is a race between information and damaging waves. The first P-wave motion reaches a station before the strongest S-wave and surface-wave shaking. That time gap is useful only if the early signal can reduce uncertainty in the ground motion that matters for engineering and emergency response.

Operational warning systems need estimates of peak ground acceleration, peak ground velocity and response-spectral ordinates at sites that may not yet have observed strong shaking. These quantities control many practical decisions: whether shaking will exceed a building or infrastructure threshold, whether an alarm should be issued, and how much uncertainty should be attached to that alarm. The physical question is simple. How much of later strong shaking is already predictable from the first seconds of the P wave, and where does that predictability stop?

Most machine-learning studies of earthquake waveforms report improved prediction accuracy inside a dataset. That evidence is useful, but it does not by itself define the boundary needed for early warning. A deployable forecast must generalize across events, stations and regions; it must remain calibrated in the upper tail of damaging motion; and it must state when the early record does not contain enough information. A high average score is not enough if the largest motions are missed or if a model trained in one region gives narrow intervals in another.

We address this by building a public-data benchmark around event-station samples. Each sample contains an early P-wave window, source-path metadata and a later strong-motion target. The main tests use InstanceGM and K-NET, with supporting transfer analyses on European Strong-Motion records and AQ2009GM. We evaluate windows of 1, 2, 3, 5 and 10 s after the P arrival. The prediction targets are peak ground acceleration (PGA), peak ground velocity (PGV) and spectral acceleration (SA) at engineering periods where available.

The study is designed around a boundary, not a model leaderboard. We use gradient-boosted tree regressors as the primary model because they are stable, inspectable and strong on tabular waveform features. We add quantile and conformal analyses to measure uncertainty. We include a light external-transfer setup to measure what fails when a model is moved from one region to another. The central result is an information curve: how much each additional second of P-wave information buys, how that gain changes under held-station and held-event splits, and how far calibration can be transferred.

## Results

### A public benchmark for early strong-motion predictability

The unified manifest contains 2,460,425 records after harmonizing public waveform sources and metadata. The main benchmark combines two complementary strong-motion sources. InstanceGM contributes 1,159,223 records with broad source-path diversity and multiple ground-motion targets. K-NET contributes 22,119 Japanese strong-motion records with well-controlled station metadata and a dense regional network.

For each event-station record we construct early P-wave windows of 1, 2, 3, 5 and 10 s. The feature table stores waveform amplitude, envelope, energy and frequency summaries, together with source-path variables such as magnitude and distance. Target variables are log-transformed PGA, PGV and SA values. The split design keeps event or station groups disjoint between training and testing. The held-station split is the main generalization test because it asks whether early-waveform information helps at sites not used for training.

The baseline model uses source-path information without the early waveform. The early-waveform model adds the P-window features. This comparison estimates the information supplied by the observed early motion beyond what is already available from magnitude and distance proxies. Classical attenuation-style references and regional ground-motion models are included as additional checks where their required input variables are available.

### Early P waves add stable information beyond source-path metadata

At 10 s, early-waveform features reduce held-station mean absolute error across all balanced targets. The reductions are 35.5% for InstanceGM PGA, 52.6% for InstanceGM PGV, 26.0% for InstanceGM SA at 0.3 s, 20.9% for InstanceGM SA at 1.0 s, 27.8% for InstanceGM SA at 3.0 s and 49.9% for K-NET PGA. These are held-station tests with zero station overlap between train and test partitions.

The same pattern appears in random-split checks, where the test distribution is closer to the training distribution. InstanceGM PGA error decreases from 0.299 to 0.207 log units, InstanceGM PGV from 0.298 to 0.165, and K-NET PGA from 0.217 to 0.105. These random-split values are not the main claim, because they can benefit from station and path similarity. They show the upper end of the achievable information gain under easier conditions.

The window-length curve shows that the first seconds already carry useful information. In K-NET PGA, the held-station error reduction is 11.3% at 1 s, 23.3% at 5 s and 49.9% at 10 s. In InstanceGM PGV, the reduction is 40.1% at 1 s, 45.4% at 5 s and 52.6% at 10 s. PGA gains grow more strongly with window length, while PGV gains appear earlier and then saturate. This difference is consistent with the two targets emphasizing different parts of the early waveform and later shaking process.

The result is not restricted to a favorable support subset chosen by target amplitude. A source-path support audit keeps test records whose magnitude and distance fall within the central training range. This audit retains 82.4 to 83.9% of held-station test rows. Within that source-path support, all six targets keep positive early-waveform gains, from 20.1% to 54.5%. This matters because a target-matched audit alone could hide amplitude-selection effects. The source-path audit shows that the gain is still present when the check is based only on variables known before the target is observed.

### Gains remain positive under bootstrap and strong-tail audits

We tested whether the held-station gains could be explained by sampling noise. A paired bootstrap over held-station test records gives positive 95% confidence intervals for all six balanced targets. The smallest lower bound is 16.9% for InstanceGM SA at 1.0 s. K-NET PGA has a 49.9% mean reduction with a 95% interval of 46.6% to 53.1%. Across these targets, the empirical probability of a nonpositive gain is 0.000 under the bootstrap procedure.

The largest motions are more important for warning than the center of the distribution. We audit the strongest 5% of test records for each target. Early-waveform features reduce top-tail mean absolute error for every target, with reductions from 18.9% for InstanceGM SA at 1.0 s to 66.0% for K-NET PGA. This supports a real strong-motion gain in the damaging tail.

The tail audit also identifies an unresolved boundary. Factor-of-two underprediction generally improves with early-waveform features, but InstanceGM SA at 3.0 s shows a small worsening in the top-tail underprediction rate. The result does not overturn the positive tail error reduction. It shows that reducing average tail error is not the same as eliminating missed high shaking. For early warning, this distinction is central: a method can be informative and still leave an irreducible high-consequence uncertainty region.

### Classical ground-motion references do not remove the early-waveform gain

Classical source-path baselines are strong reference points because they encode decades of empirical ground-motion knowledge. We include attenuation-style references and regional ground-motion equations where their input variables are available. Early-waveform models still reduce error relative to those references. Across the balanced targets, attenuation-reference reductions range from 17.5% to 51.6%. In K-NET, a Japanese ground-motion-model reference gives a best PGA error of 0.242 log units, while the early-waveform model reaches 0.111 log units in the corresponding test.

These checks keep the interpretation narrow. The early waveform is not replacing physics or source-path modeling. It supplies additional, measured information about the current event-station path. The benchmark quantifies that additional information under controlled splits.

### Uncertainty intervals reveal a transfer boundary

Point prediction gains are only useful if their uncertainty can be trusted. We evaluate 90% prediction intervals using target-domain conformal calibration and source-domain transfer calibration. Target-domain conformal intervals are close to nominal coverage in the main held-station tests: K-NET PGA reaches 0.925 coverage, InstanceGM PGV reaches 0.898, and the other main targets range from 0.820 to 0.876. These values show that reasonable coverage is achievable when calibration data come from the same target domain.

The same conformal procedure fails under direct regional transfer. When intervals calibrated in the source domain are applied to the target domain, coverage drops strongly. In the 2 s and 5 s transfer tests, source-domain conformal coverage is 0.468 and 0.298, giving coverage gaps of 0.432 and 0.602 relative to nominal 0.90. Target-offset calibration restores coverage near the intended level with median interval width 2.177 log10 units. The boundary is clear: source-region residuals do not provide reliable target-region uncertainty without target-region calibration.

The transfer error curves show the same effect. In zero-shot Japan-to-Europe transfer, median error ratios increase from 2.25 at 1 s to 4.27 at 10 s. Target-offset calibration reduces the ratios but does not remove the penalty, with ratios from 1.40 at 1 s to 2.46 at 10 s. On the ESM external set, the best 10 s target-offset transfer still leaves error ratios of 2.53 for PGA and 1.58 for PGV. More early waveform information improves in-domain prediction, yet it can also amplify learned regional differences when moved without calibration.

### External datasets support the same boundary

The European Strong-Motion processing currently includes 951 downloaded event archives, producing 134,250 event-station rows from 861 events and 1,568 stations. The external Europe tests confirm that cross-regional transfer is harder than in-domain held-station prediction. P-arrival sensitivity checks show median shifts of 2.517 s under delayed picks and 2.130 s under advanced picks. For 86 high-confidence records, the median offset is 1.223 s and the 95th percentile is 3.960 s. These values justify treating pick uncertainty as part of the transfer error budget.

AQ2009GM provides an additional regional check with 345,226 extracted rows, 60,310 events and 66 stations in the current processed feature tables. In 5 s held-station tests, AQ2009GM shows 55.8% PGA and 71.9% PGV reductions from early-waveform features. These results are encouraging, but they should be treated as supporting evidence until the full streaming extraction and cleanup are complete.

Together, the external datasets point to the same conclusion. Early P waves contain measurable information for later strong shaking. The information is strongest when training, calibration and test data share a regional distribution. Cross-regional use requires target calibration, and even calibrated transfer keeps a sizable penalty.

## Discussion

This study defines a public-data boundary for early P-wave strong-motion prediction. The first seconds after P arrival consistently reduce held-station error in PGA, PGV and SA targets. The result survives paired bootstrap tests, source-path support checks and strong-tail audits. The gains are not limited to random splits or to the center of the target distribution.

The boundary is equally important. Direct uncertainty transfer fails across regions, and zero-shot prediction from Japan to Europe or Australia carries large error penalties. Target-offset calibration repairs much of the interval coverage, but it does not recover in-domain accuracy. This means that a regional early-warning model should not export its uncertainty intervals unchanged to another tectonic and instrumental setting.

The tail results also set a practical limit. Early-waveform features reduce tail error, yet some high-period spectral-acceleration underprediction remains. The first seconds of P motion can be informative without being sufficient for all damaging-motion cases. This is the part of the result that matters most for risk communication. A useful warning model should report when it is outside its reliable information regime.

The benchmark supports three operational implications. First, early waveform observations should be used alongside source-path metadata, because they add station-specific information before the strongest shaking. Second, uncertainty calibration must be regional. Third, evaluation should include held-station splits and strong-tail audits, because random-split averages can hide the failures that matter during damaging earthquakes.

Several limitations remain. Public datasets differ in instrumentation, metadata completeness, picking accuracy and target definitions. Some external datasets are still partially processed. The current models use compact engineered features and gradient-boosted trees; a waveform neural network may improve some targets, but it would not remove the need for held-out splits and regional calibration. The present evidence is strongest for the measured benchmark and should not be generalized to all operational networks without local testing.

The main value of the benchmark is that it turns a broad early-warning question into a measurable curve. Each region can be tested by the same protocol: construct event-station samples, split by held events and stations, measure the information gain from 1 to 10 s of P waves, and calibrate intervals on target-domain residuals. That protocol gives a direct way to decide where early P-wave prediction is useful, where it is uncertain, and where a warning system needs more than the early waveform can provide.

## Methods

### Data sources and sample construction

We used public strong-motion datasets that provide waveform records and event-station metadata. The main benchmark uses InstanceGM and K-NET. Supporting analyses use European Strong-Motion records and AQ2009GM. Each event-station record was converted to a common manifest with dataset name, event identifier, station identifier, component information, sampling metadata, P-arrival reference, source-path variables and target ground-motion values.

For each record, early waveform windows were cut from the P arrival with lengths of 1, 2, 3, 5 and 10 s. Windows with insufficient samples or missing target variables were excluded from the corresponding target-specific table. The target variables were log-transformed PGA, PGV and available SA ordinates. The benchmark stores derived feature tables so that most experiments can be reproduced without retaining the full raw waveform files locally.

### Early-window features

The primary feature representation uses compact waveform summaries from the early P-window. These include amplitude statistics, absolute and squared amplitude summaries, cumulative energy, envelope summaries, component-wise ratios and simple frequency-domain summaries. The feature design is intentionally simple. It avoids using target-window information and keeps the comparison focused on how much information is already present in the early P motion.

Metadata features include magnitude and distance where available. Station or regional labels are used only in experiments that explicitly test whether such information changes transfer or uncertainty behavior. The baseline model uses source-path metadata without early-window waveform features. The early-waveform model adds the P-window feature set.

### Splits and models

We used grouped splits to avoid leakage. The held-station split keeps station identifiers disjoint between training and test sets. Held-event checks keep event identifiers disjoint. Random splits are reported as easier reference tests, not as the main evidence. Split audits verify zero group overlap for the main held-out tests.

The main regressors are histogram gradient boosting and XGBoost-style tree ensembles depending on the experiment table. Hyperparameters are kept conservative and fixed across related targets where possible. Model comparison is not the main aim. The benchmark uses stable models to estimate the information added by the early waveform under the same split and target definition.

Performance is reported as mean absolute error in log target units and as relative reduction compared with the source-path baseline. For a target \(y\), baseline prediction \(\hat{y}_b\) and early-waveform prediction \(\hat{y}_w\), the relative error reduction is

\[
100 \times \frac{\mathrm{MAE}(y,\hat{y}_b)-\mathrm{MAE}(y,\hat{y}_w)}{\mathrm{MAE}(y,\hat{y}_b)}.
\]

Positive values mean that early-waveform features improve the prediction under the same split.

### Support, bootstrap and tail audits

The source-path support audit restricts held-station test rows to magnitude and distance ranges supported by the training data. The range uses the central training support and does not condition on the observed target amplitude. This audit separates source-path interpolation from target-matched post-hoc checks.

Uncertainty in relative error reduction was estimated with paired bootstrap resampling of test records. Each bootstrap draw resamples records with replacement and recomputes the paired baseline and early-waveform errors. Confidence intervals are empirical quantiles of the bootstrap distribution.

Strong-tail audits focus on the top 5% of target amplitudes in each held-station test. We report tail mean absolute error reduction and factor-of-two underprediction rates. This separates ordinary average-error gains from high-consequence underprediction behavior.

### Uncertainty and transfer evaluation

Prediction intervals were evaluated with conformal calibration. Target-domain conformal intervals use calibration residuals from the same target domain. Source-domain transfer intervals use residuals from the source region and apply them to the target region. Target-offset calibration adds a small target-domain residual correction.

Cross-regional transfer tests train models in one region and evaluate in another. We report error ratios relative to target-domain models or target baselines. The Japan-to-Europe and Japan-to-Australia analyses measure how early-waveform information, source-path metadata and calibration behave when the waveform distribution and network conditions change.

### Software and reproducibility

All scripts were run locally in the project environment. Derived tables, figures and audit summaries are stored in the repository under the `work` and `outputs` trees. Raw waveform data remain external and should be obtained from their public providers. Before submission, the code repository should be rebuilt or archived without internal development history and with exact data-access instructions.

## Data availability

This study uses public strong-motion data sources, including InstanceGM, K-NET, European Strong-Motion records and AQ2009GM. Derived feature tables and split manifests will be released with the final repository or an archival deposit. Raw waveform redistribution will follow the terms of the original data providers. The current draft does not yet contain final repository DOIs or provider-specific access statements.

## Code availability

Analysis code, figure-generation scripts and verification scripts are available in the local project repository. A clean public release will be prepared before submission, with internal development history removed and with commands for regenerating the tables and figures used in the manuscript.

## Acknowledgements

[To be completed.]

## Author contributions

[To be completed.]

## Competing interests

The authors declare no competing interests. [Confirm before submission.]

## Figure legends

**Figure 1 | Public strong-motion benchmark and prediction task.** Overview of the event-station construction, early P-wave windows and target ground-motion variables. Each sample uses a fixed P-window length and predicts later PGA, PGV or SA. The figure should show the data sources, grouped splits and the separation between source-path metadata and early-waveform features.

**Figure 2 | Information gain from 1 to 10 s of P waves.** Held-station relative error reductions for PGA, PGV and SA targets as a function of P-window length. Curves should emphasize the different saturation behavior of PGA and PGV and should mark 1, 2, 3, 5 and 10 s windows.

**Figure 3 | Held-station robustness and bootstrap confidence.** Error reductions for the six balanced held-station targets with paired bootstrap confidence intervals. The figure should include the zero-gain reference line and should show that all interval lower bounds are positive.

**Figure 4 | Source-path support and strong-tail behavior.** Comparison of held-station gains in the source-path support subset and in the strongest 5% of target motions. The tail panel should also indicate factor-of-two underprediction changes, including the remaining SA at 3.0 s limitation.

**Figure 5 | Comparison with source-path and classical ground-motion references.** Model errors for source-path baselines, classical references and early-waveform models. The figure should show that early-waveform information remains useful when compared with empirical ground-motion references.

**Figure 6 | Cross-regional transfer error boundary.** Japan-to-Europe and Japan-to-Australia transfer ratios across P-window lengths. Separate zero-shot and target-offset calibrated results. The figure should show that transfer penalties increase without target calibration.

**Figure 7 | Predictability-boundary synthesis.** Within-domain information gain, cross-region transfer penalty, conformal coverage gap with interval width, and strong-motion tail underprediction. The uncertainty panel reports `0.90 - observed coverage`, so direct source-domain under-coverage appears as a positive gap.

**Figure 8 | External dataset support.** Summary of ESM and AQ2009GM supporting tests, including processed sample counts, station/event coverage and external held-station gains. This figure should clearly label AQ2009GM as current processed-feature evidence if the full stream is not complete.

## References

References must be completed from the literature manager before submission. Do not fabricate bibliographic entries. Required groups include earthquake early warning, P-wave ground-motion prediction, ground-motion models, conformal prediction, K-NET, InstanceGM, European Strong-Motion records and AQ2009GM.
