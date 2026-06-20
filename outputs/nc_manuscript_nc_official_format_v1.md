# Cross regional limits on predicting strong shaking from early P waves

[Author names]

[Affiliations]

Correspondence: [corresponding author email]

## Abstract

Earthquake early warning needs reliable estimates of damaging ground motion before the strongest shaking arrives. The first seconds of primary waves carry source and path information, but the cross-regional limit of that information remains unclear in public strong-motion data. We build an event-station benchmark from public strong-motion records and test whether 1 to 10 seconds of early primary-wave motion improve later peak and spectral ground-motion prediction under held-event, held-station and regional-transfer splits. Early-waveform features reduce held-station errors for Japanese and global strong-motion targets, with positive bootstrap intervals and persistent gains in the strongest-motion tail. Direct regional transfer remains penalized, and prediction intervals calibrated in a source region under-cover target regions. Here, we show that early primary waves add reproducible strong-motion information inside calibrated domains while defining measurable transfer and uncertainty boundaries across regions.

## Introduction

Earthquake early warning is a race between information and damaging waves. The first P-wave motion reaches a station before the strongest S-wave and surface-wave shaking. That time gap is useful only if the early signal can reduce uncertainty in the ground motion that matters for engineering and emergency response.

Operational warning systems need estimates of peak ground acceleration, peak ground velocity and response-spectral ordinates at sites that may not yet have observed strong shaking. These quantities control many practical decisions: whether shaking will exceed a building or infrastructure threshold, whether an alarm should be issued, and how much uncertainty should be attached to that alarm. The physical question is simple. How much of later strong shaking is already predictable from the first seconds of the P wave, and where does that predictability stop?

The question cannot be answered from a single random train-test split. Random splits mix similar stations, events and paths between training and testing, so they can report a useful engineering model while overstating what a new station or a new region would receive. A deployable forecast must generalize across events, stations and regions; it must remain calibrated in the upper tail of damaging motion; and it must state when the early record does not contain enough information. A high average score is not enough if the largest motions are missed or if a model trained in one region gives narrow intervals in another.

Public strong-motion archives now make this boundary testable. They also make it easy to get the answer wrong. Waveform archives differ in acceleration units, component conventions, phase-pick definitions, station metadata, site terms and target definitions. A benchmark that merges such archives has to keep the provenance visible. The useful object is an event-station sample: a short early waveform, source-path information known at warning time, and a later ground-motion target measured from the same record.

The same benchmark must connect statistical performance to warning use. A prediction that improves average error can still be unsafe if it misses the largest motions or if its interval coverage collapses at a new station. The relevant scientific object is the joint behaviour of point error, tail error and interval coverage under controlled shifts. We use that joint behaviour to define a predictability boundary rather than a single best model score.

We address this by building a public-data benchmark around event-station samples. Each sample contains an early P-wave window, source-path metadata and a later strong-motion target. The main tests use InstanceGM and K-NET, with supporting transfer analyses on European Strong-Motion records and AQ2009GM. We evaluate windows of 1, 2, 3, 5 and 10 s after the P arrival. The prediction targets are peak ground acceleration (PGA), peak ground velocity (PGV) and spectral acceleration (SA) at engineering periods where available.

Here, we show that early primary-wave information defines a measurable prediction boundary. Gradient-boosted tree regressors provide stable tabular baselines, while quantile and conformal analyses measure uncertainty. External-transfer tests measure how this boundary changes across regions. The central output is an information curve: how much each additional second of P-wave information buys, how that gain changes under held-station and held-event splits, and how far calibration can be transferred.

## Results

### Public benchmark for early strong-motion prediction

The unified manifest contains 2,460,425 records after harmonizing public waveform sources and metadata. The main benchmark combines two complementary strong-motion sources. InstanceGM contributes 1,159,223 records with broad source-path diversity and multiple ground-motion targets. K-NET contributes 22,119 Japanese strong-motion records with well-controlled station metadata and a dense regional network.

The K-NET archive was converted locally from the original BSON packages. Component labels were standardized by mapping UD to vertical, NS to north and EW to east. Unit provenance follows the K-NET strong-motion convention in which acceleration is stored in gal, equivalent to centimetres per second squared. This conversion step matters because a waveform model can learn unit and component mistakes as if they were regional physics.

The remaining public sources serve specific roles. STEAD and Iquique are used for phase-label transfer auditing, where the goal is to test whether pretrained pickers align early windows consistently across datasets. European Strong-Motion records provide an external European strong-motion check from local ASCII event packages. AQ2009GM provides an independent SeisBench strong-motion archive with a different event and station distribution. These supporting sources are used to test boundaries; the main ground-motion claim is anchored in the InstanceGM and K-NET held-out evaluations.

For each event-station record we construct early P-wave windows of 1, 2, 3, 5 and 10 s. The feature table stores waveform amplitude, envelope, energy and frequency summaries, together with source-path variables such as magnitude and distance. Target variables are log-transformed PGA, PGV and SA values. The split design keeps event or station groups disjoint between training and testing. The held-station split is the main generalization test because it asks whether early-waveform information helps at sites not used for training.

The baseline model uses source-path information without the early waveform. The early-waveform model adds the P-window features. This comparison estimates the information supplied by the observed early motion beyond what is already available from magnitude and distance proxies. Classical attenuation-style references and regional ground-motion models are included as additional checks where their required input variables are available.

The phase-label audit checks whether the P-window alignment itself is plausible. In a 1,000-record-per-dataset audit, PhaseNet P picks remain stable for STEAD and K-NET, with P-pick mean absolute errors of 0.035 s and 0.056 s. S picks show stronger dataset dependence, especially for InstanceGM. We use this result to keep the benchmark focused: P-window extraction is credible for the main early-window task, while broad phase-label transfer is treated as a separate limitation.

Every main split is checked for group leakage. Held-event tests require zero event overlap, and held-station tests require zero station overlap between training and test sets. The split distributions are also inspected because zero overlap alone does not guarantee a hard test. InstanceGM held-station test records are farther and weaker than the training records, with median distance increasing from 44.27 km to 70.61 km and median log10 PGA decreasing from -1.68 to -2.11. K-NET train and test distributions overlap more closely. This difference helps interpret why some targets retain larger gains than others.

### Early P waves add information beyond metadata

At 10 s, early-waveform features reduce held-station mean absolute error across all balanced targets. The reductions are 35.5% for InstanceGM PGA, 52.6% for InstanceGM PGV, 26.0% for InstanceGM SA at 0.3 s, 20.9% for InstanceGM SA at 1.0 s, 27.8% for InstanceGM SA at 3.0 s and 49.9% for K-NET PGA. These are held-station tests with zero station overlap between train and test partitions.

The same pattern appears in random-split checks, where the test distribution is closer to the training distribution. InstanceGM PGA error decreases from 0.299 to 0.207 log units, InstanceGM PGV from 0.298 to 0.165, and K-NET PGA from 0.217 to 0.105. These random-split values are not the main claim, because they can benefit from station and path similarity. They show the upper end of the achievable information gain under easier conditions.

The window-length curve shows that the first seconds already carry useful information. In K-NET PGA, the held-station error reduction is 11.3% at 1 s, 23.3% at 5 s and 49.9% at 10 s. In InstanceGM PGV, the reduction is 40.1% at 1 s, 45.4% at 5 s and 52.6% at 10 s. PGA gains grow more strongly with window length, while PGV gains appear earlier and then saturate. This difference is consistent with the two targets emphasizing different parts of the early waveform and later shaking process.

InstanceGM PGA shows the same monotone information curve with smaller absolute gain: 23.9% at 1 s, 31.2% at 5 s and 35.5% at 10 s. The result separates two pieces of the early-warning problem. Some targets benefit from the first second because the early amplitude and envelope already constrain the later motion. Other targets need longer windows because the damaging peak arrives later or because the spectral target integrates more of the waveform evolution.

Held-event tests give a complementary view. At 10 s, the early-waveform model improves every main target after excluding selected events from training. The reductions are 38.8% for InstanceGM PGA, 50.4% for InstanceGM PGV and 54.5% for K-NET PGA, with positive gains for the spectral-acceleration targets. These held-event results test new earthquakes inside a known station distribution. Held-station tests are harder for deployment because the target sites themselves are unseen.

The result is not restricted to a favorable support subset chosen by target amplitude. A source-path support audit keeps test records whose magnitude and distance fall within the central training range. This audit retains 82.4 to 83.9% of held-station test rows. Within that source-path support, all six targets keep positive early-waveform gains, from 20.1% to 54.5%. This matters because a target-matched audit alone could hide amplitude-selection effects. The source-path audit shows that the gain is still present when the check is based only on variables known before the target is observed.

The stronger PGV gains are physically plausible because PGV is more connected to sustained low-frequency motion than PGA. The PGA gain grows later in K-NET, where short early windows often contain incomplete high-frequency acceleration information. Spectral acceleration sits between these behaviours. The benchmark does not assign a single universal lead time. It reports a target-specific curve, which is the quantity a warning system would need when choosing alarm thresholds.

Peak-capture audits define another possible shortcut. In K-NET, 69.8% of 1 s test windows and 94.7% of 10 s test windows have early horizontal peak amplitude at least 0.8 times the later PGA target. A model could then benefit by seeing part of the eventual peak. We therefore audit a K-NET pre-peak subset where the early horizontal peak remains below 80% of the observed PGA. Early-waveform features still reduce MAE by 13.8% at 1 s and 17.9% at 3 s in that subset. The gain is smaller, but it remains present before the early window directly captures the target-scale peak.

### Gains remain positive under bootstrap and strong-tail audits

We tested whether the held-station gains could be explained by sampling noise. A paired bootstrap over held-station test records gives positive 95% confidence intervals for all six balanced targets. The smallest lower bound is 16.9% for InstanceGM SA at 1.0 s. K-NET PGA has a 49.9% mean reduction with a 95% interval of 46.6% to 53.1%. Across these targets, the empirical probability of a nonpositive gain is 0.000 under the bootstrap procedure.

The bootstrap is paired at the record level. Each resampled test set contains the same rows for the metadata-only and early-waveform models, so the interval measures the gain from adding the early waveform under the same events, stations and targets. This matters because the absolute errors differ across targets. The paired statistic asks whether the early-waveform model improves the same prediction problem, not whether two independently sampled errors happen to differ.

The largest motions are more important for warning than the center of the distribution. We audit the strongest 5% of test records for each target. Early-waveform features reduce top-tail mean absolute error for every target, with reductions from 18.9% for InstanceGM SA at 1.0 s to 66.0% for K-NET PGA. This supports a real strong-motion gain in the damaging tail.

The tail audit also identifies an unresolved boundary. Factor-of-two underprediction generally improves with early-waveform features, but InstanceGM SA at 3.0 s shows a small worsening in the top-tail underprediction rate. The result does not overturn the positive tail error reduction. It shows that reducing average tail error is not the same as eliminating missed high shaking. For early warning, this distinction is central: a method can be informative and still leave an irreducible high-consequence uncertainty region.

Residual diagnostics locate part of this boundary. K-NET PGA retains a distance-dependent residual tail after the early waveform is added. InstanceGM contains repeated high-residual records across PGA, PGV and spectral-acceleration targets. These cases are not discarded; they are separated into a residual-audit layer. The benchmark therefore reports both the information gain and the records where early P motion leaves large unexplained error.

### Early-waveform gain remains against classical references

Classical source-path baselines are strong reference points because they encode decades of empirical ground-motion knowledge. We include attenuation-style references and regional ground-motion equations where their input variables are available. Early-waveform models still reduce error relative to those references. Across the balanced targets, attenuation-reference reductions range from 17.5% to 51.6%. In K-NET, a Japanese ground-motion-model reference gives a best PGA error of 0.242 log units, while the early-waveform model reaches 0.111 log units in the corresponding test.

The OpenQuake BooreEtAl2014 reference gives another classical check under limited metadata. It uses available source distance as a proxy for rupture distance, fixes rake where focal mechanism is missing and assigns a standard reference site condition when Vs30 is absent. Under these limitations, the early-waveform model reduces MAE relative to the bias-corrected OpenQuake reference by 36.6% for InstanceGM PGA, 59.4% for InstanceGM PGV, 35.4% for SA at 0.3 s, 36.4% for SA at 1.0 s, 48.0% for SA at 3.0 s and 60.6% for K-NET PGA.

The K-NET regional screening evaluates Kanno2006, Zhao2006 and SiMidorikawa1999 variants. The best screened candidate is Kanno2006Shallow with MAE 0.242 log units on the balanced held-station split. The early-waveform model reaches 0.111 log units in the corresponding test. This is a screening comparison because the public local tables do not yet provide all rupture, site and mechanism terms required for a fully specified regional ground-motion-model study.

These checks keep the interpretation narrow. The early waveform supplies measured information about the current event-station path beyond the source-path variables used by the baseline and classical references. It does not remove the need for regional ground-motion modelling. The current evidence supports an added-information claim, with a clear boundary around metadata completeness.

### Uncertainty intervals reveal a transfer boundary

Point prediction gains are only useful if their uncertainty can be trusted. We evaluate 90% prediction intervals using target-domain conformal calibration and source-domain transfer calibration. Target-domain conformal intervals are close to nominal coverage in the main held-station tests: K-NET PGA reaches 0.925 coverage, InstanceGM PGV reaches 0.898, and the other main targets range from 0.820 to 0.876. These values show that reasonable coverage is achievable when calibration data come from the same target domain.

The same conformal procedure fails under direct regional transfer. When intervals calibrated in the source domain are applied to the target domain, coverage drops strongly. In the 2 s and 5 s transfer tests, source-domain conformal coverage is 0.468 and 0.298, giving coverage gaps of 0.432 and 0.602 relative to nominal 0.90. Target-offset calibration restores coverage near the intended level with median interval width 2.177 log10 units. The boundary is clear: source-region residuals do not provide reliable target-region uncertainty without target-region calibration.

The transfer error curves show the same effect. In zero-shot Japan-to-Europe transfer, median error ratios increase from 2.25 at 1 s to 4.27 at 10 s. Target-offset calibration reduces the ratios but does not remove the penalty, with ratios from 1.40 at 1 s to 2.46 at 10 s. On the ESM external set, the best 10 s target-offset transfer still leaves error ratios of 2.53 for PGA and 1.58 for PGV. More early waveform information improves in-domain prediction, yet it can also amplify learned regional differences when moved without calibration.

This transfer pattern explains why uncertainty is part of the main result. If the calibration residuals are exchangeable between the calibration and test samples, conformal intervals can produce reliable coverage with few modelling assumptions. Regional transfer breaks that exchangeability. A source-domain residual distribution can be too narrow, biased or shaped by a different network. Target-offset calibration repairs much of the coverage by using target-domain residual information, but the resulting intervals remain wide. The practical message is direct: a warning model can carry early waveform information across regions only with target-region calibration and explicit interval widening.

The interval width is part of the boundary. A method can restore nominal coverage by making intervals so wide that the prediction loses warning value. The target-offset calibration result is useful because it shows both sides of the tradeoff: coverage returns to about 0.90, while the median interval width reaches 2.177 log10 units. That width is a signal, not a formatting nuisance. It says that cross-region uncertainty remains large even after simple target-domain correction.

### External datasets support the same boundary

The European Strong-Motion processing currently includes 951 downloaded event archives, producing 134,250 event-station rows from 861 events and 1,568 stations. The external Europe tests confirm that cross-regional transfer is harder than in-domain held-station prediction. P-arrival sensitivity checks show median shifts of 2.517 s under delayed picks and 2.130 s under advanced picks. For 86 high-confidence records, the median offset is 1.223 s and the 95th percentile is 3.960 s. These values justify treating pick uncertainty as part of the transfer error budget.

European Strong-Motion records also test a different P-arrival regime. The local ASCII headers used here do not provide explicit catalog P picks for all records, so the compact feature tables use a theoretical P-onset estimate. A velocity sensitivity audit changes the assumed P velocity from 6.0 to 5.5 and 6.5 km/s. Retained-window validity remains above 0.994 across tested windows, while timing shifts reach multi-second medians. This makes ESM useful as an external-domain check and transfer target. It also limits any claim that depends on exact catalog P arrivals.

AQ2009GM provides an additional regional check with 345,226 extracted rows, 60,310 events and 66 stations in the current processed feature tables. The streaming validation covers all 254 local manifest chunks and retains compact feature tables rather than the raw chunk files. In 5 s held-station tests, AQ2009GM shows 55.8% PGA and 71.9% PGV reductions from early-waveform features. These results support the same early-information pattern in a separate archive.

The four-domain transfer synthesis combines InstanceGM, K-NET, AQ2009GM and ESM. The transfer model uses early-waveform features and excludes magnitude, distance, site variables, event identifiers and station identifiers. This design measures the waveform-domain boundary directly. All cross-domain rows have higher MAE than target-domain training. Median zero-shot penalties rise from 2.25 times target-domain error at 1 s to 4.27 times at 10 s. Offset calibration reduces the penalty but leaves ratios above one at every window.

Together, the external datasets point to the same conclusion. Early P waves contain measurable information for later strong shaking. The information is strongest when training, calibration and test data share a regional distribution. Cross-regional use requires target calibration, and even calibrated transfer keeps a sizable penalty.

This is the main difference between in-domain prediction and regional portability. Longer windows add information inside the target domain, but the same extra information can encode region-specific path, site and instrument behaviour. The increasing zero-shot penalty with window length supports that interpretation. The result argues for local calibration before deployment, not for discarding early-waveform information.

## Discussion

This study defines a public-data boundary for early P-wave strong-motion prediction. The first seconds after P arrival consistently reduce held-station error in PGA, PGV and SA targets. The result survives paired bootstrap tests, source-path support checks and strong-tail audits. The gains are not limited to random splits or to the center of the target distribution.

The boundary is equally important. Direct uncertainty transfer fails across regions, and zero-shot prediction from Japan to Europe or Australia carries large error penalties. Target-offset calibration repairs much of the interval coverage, but it does not recover in-domain accuracy. This means that a regional early-warning model should not export its uncertainty intervals unchanged to another tectonic and instrumental setting.

The tail results also set a practical limit. Early-waveform features reduce tail error, yet some high-period spectral-acceleration underprediction remains. The first seconds of P motion can be informative without being sufficient for all damaging-motion cases. This is the part of the result that matters most for risk communication. A useful warning model should report when it is outside its reliable information regime.

The result also clarifies the role of model complexity. The main claim does not require a large waveform neural network. Compact early-window features and tree regressors are enough to show the information curve, the held-station gain and the transfer penalty. A neural model may improve some targets, especially where waveform shape contains phase and duration information beyond the compact summaries. Such a model would still need the same held-station, strong-tail and regional-calibration tests.

The benchmark supports three operational implications. First, early waveform observations should be used alongside source-path metadata, because they add station-specific information before the strongest shaking. Second, uncertainty calibration must be regional. Third, evaluation should include held-station splits and strong-tail audits, because random-split averages can hide the failures that matter during damaging earthquakes.

For an operational system, these implications translate into a simple validation checklist. A candidate model should show positive gain over source-path metadata on held stations, retain positive gain in the strongest-motion tail, report interval coverage on a target-domain calibration set, and disclose its cross-region penalty before it is moved to another network. The checklist is intentionally model-agnostic. It can be applied to gradient-boosted trees, convolutional networks, transformers or physics-informed hybrids.

Several limitations remain. Public datasets differ in instrumentation, metadata completeness, picking accuracy and target definitions. ESM currently uses a theoretical P-onset estimate, so ESM supports regional-transfer evidence more strongly than catalog-P lead-time evidence. The current classical comparisons are constrained by rupture-distance, site-term and mechanism availability. Prospective warning performance also requires latency, telemetry, real-time picking and decision thresholds that are outside this offline benchmark.

These limitations are part of the proposed benchmark rather than loose ends to hide. They define which evidence can be claimed now and which evidence needs new data. The strongest present claim is the measured information boundary in public strong-motion records. The next claim, operational performance, would require prospective tests in a live warning environment with network latency and target-region calibration.

The current results also separate two common claims. Early P waves are informative for later strong motion in the tested public datasets. That does not mean that every damaging motion is predictable from the first seconds alone. The unresolved tail and the cross-region interval widening show where the early signal runs out. A useful warning system should expose that limit to downstream decision rules.

The main value of the benchmark is that it turns a broad early-warning question into a measurable curve. Each region can be tested by the same protocol: construct event-station samples, split by held events and stations, measure the information gain from 1 to 10 s of P waves, and calibrate intervals on target-domain residuals. That protocol gives a direct way to decide where early P-wave prediction is useful, where it is uncertain, and where a warning system needs more than the early waveform can provide.

## Methods

### Data sources and sample construction

We used public strong-motion datasets that provide waveform records and event-station metadata. The main benchmark uses InstanceGM and K-NET. Supporting analyses use European Strong-Motion records and AQ2009GM. Each event-station record was converted to a common manifest with dataset name, event identifier, station identifier, component information, sampling metadata, P-arrival reference, source-path variables and target ground-motion values.

The K-NET archive was converted from local BSON files. Complete records require three components and usable event-station metadata. The conversion stores variable-length waveform arrays in ZNE order and preserves sample boundaries for each record. K-NET acceleration is treated as gal, equivalent to centimetres per second squared. This convention is used only after unit provenance checks.

AQ2009GM was processed through chunk streaming. Each manifest chunk was downloaded or read, compact early-window features and PGA/PGV targets were extracted, and raw HDF5 and metadata chunk files were removed after the derived features were written. The retained inventory contains 254 chunks with zero extraction errors and 345,226 valid PGA/PGV records.

European Strong-Motion records were processed from local ASCII zip packages. The compact feature extraction reads the original packages without modifying them. Because explicit P picks are not available for all local ESM headers, the retained windows use a theoretical P-onset estimate from epicentral distance and an assumed P velocity. Timing sensitivity and waveform-envelope spot checks quantify the uncertainty introduced by this choice.

For each record, early waveform windows were cut from the P arrival with lengths of 1, 2, 3, 5 and 10 s. Windows with insufficient samples or missing target variables were excluded from the corresponding target-specific table. The target variables were log-transformed PGA, PGV and available SA ordinates. The benchmark stores derived feature tables so that most experiments can be reproduced without retaining the full raw waveform files locally.

### Early-window features

The primary feature representation uses compact waveform summaries from the early P-window. These include amplitude statistics, absolute and squared amplitude summaries, cumulative energy, envelope summaries, component-wise ratios and simple frequency-domain summaries. The feature design is intentionally simple. It avoids using target-window information and keeps the comparison focused on how much information is already present in the early P motion.

For the full-manifest AQ2009GM validation, the compact features are velocity-based and paired with official PGA/PGV metadata targets. For ESM, the features include component absolute maximum, root mean square, standard deviation, 95th-percentile absolute amplitude, horizontal maximum, vector maximum and vector root mean square. Full-record peak features are excluded from predictive feature sets.

Metadata features include magnitude and distance where available. Station or regional labels are used only in experiments that explicitly test whether such information changes transfer or uncertainty behavior. The baseline model uses source-path metadata without early-window waveform features. The early-waveform model adds the P-window feature set.

### Splits and models

We used grouped splits to avoid leakage. The held-station split keeps station identifiers disjoint between training and test sets. Held-event checks keep event identifiers disjoint. Random splits are reported as easier reference tests, not as the main evidence. Split audits verify zero group overlap for the main held-out tests.

The main regressors are histogram gradient boosting and XGBoost-style tree ensembles depending on the experiment table. Hyperparameters are kept conservative and fixed across related targets where possible. Model comparison is not the main aim. The benchmark uses stable models to estimate the information added by the early waveform under the same split and target definition.

Random splits use seed 19. Held-event and held-station strong-motion splits use seed 31, with a fixed offset for station holdout. AQ2009GM uses seed 43. ESM uses seed 71. PNWAccelerometers uses seed 83. Phase-audit sampling uses seed 7. Conformal intervals use seed 17. Boundary sensitivity repeats seeds 17, 59 and 101.

Performance is reported as mean absolute error in log target units and as relative reduction compared with the source-path baseline. Relative error reduction is 100 times the baseline MAE minus the early-waveform MAE, divided by the baseline MAE. Positive values mean that early-waveform features improve the prediction under the same split.

### Support, bootstrap and tail audits

The source-path support audit restricts held-station test rows to magnitude and distance ranges supported by the training data. The range uses the central training support and does not condition on the observed target amplitude. This audit separates source-path interpolation from target-matched post-hoc checks.

Uncertainty in relative error reduction was estimated with paired bootstrap resampling of test records. Each bootstrap draw resamples records with replacement and recomputes the paired baseline and early-waveform errors. Confidence intervals are empirical quantiles of the bootstrap distribution.

Strong-tail audits focus on the top 5% of target amplitudes in each held-station test. We report tail mean absolute error reduction and factor-of-two underprediction rates. This separates ordinary average-error gains from high-consequence underprediction behavior.

The pre-peak audit is performed on K-NET PGA. It compares the early horizontal peak amplitude with the final PGA target and retains records below a chosen ratio threshold. The main threshold is 0.8. This audit tests whether early-window gains remain when the early window has not already captured target-scale horizontal acceleration.

### Uncertainty and transfer evaluation

Prediction intervals were evaluated with conformal calibration. Target-domain conformal intervals use calibration residuals from the same target domain. Source-domain transfer intervals use residuals from the source region and apply them to the target region. Target-offset calibration adds a small target-domain residual correction.

Cross-regional transfer tests train models in one region and evaluate in another. We report error ratios relative to target-domain models or target baselines. The Japan-to-Europe and Japan-to-Australia analyses measure how early-waveform information, source-path metadata and calibration behave when the waveform distribution and network conditions change.

The transfer-boundary model intentionally removes magnitude, distance, site variables, event identifiers and station identifiers. This isolates early-waveform-domain transfer. Within-domain target models provide the reference error. Zero-shot transfer trains on a source dataset and evaluates on the target test split. Target-offset transfer applies one scalar correction estimated from the target training split.

### Software and reproducibility

All scripts were run locally in the project environment. The verified run used Python 3.12.13 with numpy 2.4.4, pandas 3.0.2, scikit-learn 1.8.0, matplotlib 3.10.8, Pillow 12.2.0, h5py 3.16.0, SeisBench 0.11.5 and OpenQuake engine 3.25.1. Derived tables, figures and audit summaries are stored in the repository under the `work` and `outputs` trees. Raw waveform data remain external and should be obtained from their public providers. Before submission, the code repository should be rebuilt or archived without internal development history and with exact data-access instructions.

## Data Availability

This study uses public strong-motion data sources, including InstanceGM, K-NET, European Strong-Motion records and AQ2009GM. Derived feature tables and split manifests will be released with the final repository or an archival deposit. Raw waveform redistribution will follow the terms of the original data providers. The current draft does not yet contain final repository DOIs or provider-specific access statements.

## Code Availability

Analysis code, figure-generation scripts and verification scripts are available in the local project repository. A clean public release will be prepared before submission, with internal development history removed and with commands for regenerating the tables and figures used in the manuscript.

## References

References must be completed from the literature manager before submission. Do not fabricate bibliographic entries. Required groups include earthquake early warning, P-wave ground-motion prediction, ground-motion models, conformal prediction, K-NET, InstanceGM, European Strong-Motion records and AQ2009GM.

## Acknowledgements

[To be completed.]

## Author Contributions

[To be completed.]

## Competing Interests

The authors declare no competing interests. [Confirm before submission.]

## Figures

**Figure 1 | Cross-dataset waveform-task benchmark.** Dataset-task matrix for STEAD, InstanceGM, Iquique, K-NET and supplementary PNWAccelerometers. Panels summarize record counts, task availability and target availability.

**Figure 2 | Lead-time-dependent early waveform information.** Performance across 1 s, 3 s and 10 s post-P windows. Panels show MAE reduction, q95 residual reduction, combined-model MAE and combined-model R2.

**Figure 3 | Held-out generalization and split distribution.** Held-event and balanced held-station performance for InstanceGM and K-NET. Distribution panels summarize magnitude, distance and PGA train-test coverage.

**Figure 4 | Classical reference and uncertainty.** Bias-corrected OpenQuake BooreEtAl2014 comparison and split-conformal interval results. Panels pair point-prediction improvement with station-shift calibration limits.

**Figure 5 | Residual diagnostics.** Residual diagnostics for the combined strong-motion models. Waveform case audits are reported as an extended figure.

**Figure 6 | Phase-label transfer audit.** Cross-dataset P- and S-pick errors, q95 tails and missing-pick rates from pretrained PhaseNet and EQTransformer models.

**Figure 7 | Predictability-boundary synthesis.** Within-domain information gain, cross-region transfer penalty, conformal coverage gap with interval width, and strong-motion tail underprediction. The uncertainty panel reports `0.90 - observed coverage`, so direct source-domain under-coverage appears as a positive gap.

**Extended Data Figure | Waveform case audit.** Repeated InstanceGM high-residual records and K-NET PGA high-residual waveform cases.
