# A public-data boundary for forecasting strong shaking from early P waves

Zhou Haoyu\textsuperscript{1} and Qiang Ma\textsuperscript{1,*}

\textsuperscript{1} Institute of Engineering Mechanics, China Earthquake Administration, Harbin, China.

\textsuperscript{*}Correspondence: Qiang Ma, maqiang@iem.ac.cn. Author email: zhouhaoyiu@gmail.com. ORCID: Zhou Haoyu, 0009-0003-8817-1209; Qiang Ma, 0000-0002-9768-5223.

## Abstract

Earthquake early warning depends on the first seconds of the P wave. Those seconds can reveal source, path and site response, but the cross-regional limit for forecasting damaging ground motion is unclear. We build a public event-station benchmark for PGA, PGV and spectral acceleration using 1, 2, 3, 5 and 10 s windows after P arrival. Across 2,460,425 manifest records, early-waveform features reduce held-station error relative to source-path baselines, including 35.5% for InstanceGM PGA, 52.6% for InstanceGM PGV and 49.9% for K-NET PGA at 10 s. Gains remain positive in paired bootstrap tests, within source-path support and in the strongest 5% of motions. Regional transfer exposes the boundary: source-region conformal intervals under-cover target regions, and target-domain calibration restores coverage with wide intervals. Together, these tests define an empirical curve linking P-window length, tail risk and regional calibration.

## Introduction

Earthquake early warning must estimate damaging shaking before the strongest motion reaches a site [1,2]. The first seconds after the P arrival are the earliest waveform evidence available at that station. Their usable information is limited by source growth, propagation path, site response and calibration to the target region.

A warning model can improve average predictions and still fail where the stakes are highest. It can miss the strongest motions, lose coverage at unseen stations or carry overconfident intervals into a different region. The central question is where early P-wave information helps and where that help stops.

This boundary is difficult to see from a single benchmark number. Average error, warning-tail error, held-station generalization and regional transfer answer different questions. A model can score well on the first and fail on the others. We treat these quantities as separate evidence layers and require the same early-window claim to pass across them.

Random train-test splits do not answer that question. They mix related stations, events and paths between training and testing, so local similarity can look like predictability. Held-event, held-station and regional-transfer splits test the cases a deployed system faces: an unfamiliar earthquake, an unseen site or a different network.

Public strong-motion archives make this test possible at event-station scale [3-8]. They also require strict provenance: waveform units, component directions, P-arrival definitions, station metadata and target definitions differ across archives. We use the event-station record as the common unit, pairing a short P-window and warning-time metadata with the later ground-motion target at the same station.

We build this benchmark from InstanceGM and K-NET, with European Strong-Motion records, AQ2009GM and CWA used for external checks. Each sample contains a 1, 2, 3, 5 or 10 s window after P arrival, source-path metadata and a later PGA, PGV or SA target where available.

The target is an offline information limit. Telemetry, alert logic and human response enter later stages of early-warning design. Here the prediction unit is the record observed at one station, and the reported quantity is the improvement available before the later strong-motion target is known.

The analysis estimates an information boundary for early P-wave prediction. Stable tree regressors measure the point-error gain from adding early waveform features. Bootstrap, top-tail and residual-persistence audits test whether the gain survives high-consequence cases. Conformal and regional-transfer tests measure how much uncertainty can be moved across domains.

## Results

### Public benchmark for early strong-motion prediction

We analyse each record as an event-station prediction sample, which keeps the evidence tied to a data source, target, split and calibration domain. The unified manifest contains 2,460,425 records after harmonizing public waveform sources and metadata. InstanceGM contributes 1,159,223 records with broad source-path diversity and multiple ground-motion targets. K-NET contributes 22,119 Japanese strong-motion records with controlled station metadata and a dense regional network.

The K-NET archive was converted locally from the original BSON packages. Component labels were standardized by mapping UD to vertical, NS to north and EW to east. Unit provenance follows the K-NET strong-motion convention in which acceleration is stored in gal, equivalent to centimetres per second squared. This conversion step matters because a waveform model can learn unit and component mistakes as if they were regional physics.

The remaining public sources serve specific roles. STEAD and Iquique are used for phase-label transfer auditing, where the goal is to test whether pretrained pickers align early windows consistently across datasets. European Strong-Motion records provide an external European strong-motion check from local ASCII event packages. AQ2009GM provides an independent SeisBench strong-motion archive with a different event and station distribution. CWA provides a Taiwan official PGA/PGV metadata-target check from the 2011 public benchmark year. PNWAccelerometers is used only as an accelerometer peak-amplitude robustness check because the local cache lacks waveform units and official PGA/PGV targets. These supporting sources are used to test boundaries; the main ground-motion claim is anchored in the InstanceGM and K-NET held-out evaluations.

For each event-station record we construct early P-wave windows of 1, 2, 3, 5 and 10 s. The feature table stores waveform amplitude, envelope, energy and frequency summaries, together with source-path variables such as magnitude and distance. Target variables are log-transformed PGA, PGV and SA values. The split design keeps event or station groups disjoint between training and testing. The held-station split is the main generalization test because it asks whether early-waveform information helps at sites not used for training.

The baseline model uses source-path information without the early waveform. The early-waveform model adds the P-window features. This comparison estimates the information supplied by the observed early motion beyond what is already available from magnitude and distance proxies. Classical attenuation-style references and regional ground-motion models are included as additional checks where their required input variables are available [11-18].

The phase-label audit checks whether the P-window alignment itself is plausible. In a 1,000-record-per-dataset audit, PhaseNet P picks remain stable for STEAD and K-NET, with P-pick mean absolute errors of 0.035 s and 0.056 s [9]. S picks show stronger dataset dependence, especially for InstanceGM. We use this result to keep the benchmark focused: P-window extraction is credible for the main early-window task, while broad phase-label transfer is treated as a separate limitation.

Every main split is checked for group leakage. Held-event tests require zero event overlap, and held-station tests require zero station overlap between training and test sets. The split distributions are also inspected because zero overlap alone does not guarantee a hard test. InstanceGM held-station test records are farther and weaker than the training records, with median distance increasing from 44.27 km to 70.61 km and median log10 PGA decreasing from -1.68 to -2.11. K-NET train and test distributions overlap more closely. This difference helps interpret why some targets retain larger gains than others.

The benchmark is organized as a claim ladder. The first layer asks whether early waveform features improve held-out strong-motion prediction. The second asks whether that improvement survives resampling, support matching and strong-tail audits. The third asks whether uncertainty intervals remain calibrated when moved across regions. The fourth asks whether independent public archives keep the same pattern. This organization keeps the main claim tied to observed evidence instead of model preference.

### Early P waves add information beyond metadata

Early P waves provide a reproducible error reduction beyond source-path metadata, with the largest held-station gains in PGV and K-NET PGA. At 10 s, early-waveform features reduce held-station mean absolute error across all balanced targets. The reductions are 35.5% for InstanceGM PGA, 52.6% for InstanceGM PGV, 26.0% for InstanceGM SA at 0.3 s, 20.9% for InstanceGM SA at 1.0 s, 27.8% for InstanceGM SA at 3.0 s and 49.9% for K-NET PGA. These are held-station tests with zero station overlap between train and test partitions.

The same pattern appears in random-split checks, where the test distribution is closer to the training distribution. InstanceGM PGA error decreases from 0.299 to 0.207 log units, InstanceGM PGV from 0.298 to 0.165, and K-NET PGA from 0.217 to 0.105. These random-split values are easier reference tests because they can benefit from station and path similarity. They show the upper end of the achievable information gain under easier conditions.

The window-length curve shows that the first seconds already constrain later shaking. In K-NET PGA, the held-station error reduction is 11.3% at 1 s, 23.3% at 5 s and 49.9% at 10 s. In InstanceGM PGV, the reduction is 40.1% at 1 s, 45.4% at 5 s and 52.6% at 10 s. PGA gains grow more strongly with window length, while PGV gains appear earlier and then saturate. This difference is consistent with the two targets emphasizing different parts of the early waveform and later shaking process.

InstanceGM PGA shows the same monotone information curve with smaller absolute gain: 23.9% at 1 s, 31.2% at 5 s and 35.5% at 10 s. Some targets benefit from the first second because the early amplitude and envelope already constrain the later motion. Other targets need longer windows because the damaging peak arrives later or because the spectral target integrates more of the waveform evolution.

Held-event tests give a complementary view. At 10 s, the early-waveform model improves every main target after excluding selected events from training. The reductions are 38.8% for InstanceGM PGA, 50.4% for InstanceGM PGV and 54.5% for K-NET PGA, with positive gains for the spectral-acceleration targets. These held-event results test unfamiliar earthquakes inside a known station distribution. Held-station tests are harder for deployment because the target sites themselves are unseen.

The gain is not restricted to a favorable support subset chosen by target amplitude. A source-path support audit keeps test records whose magnitude and distance fall within the central training range, retaining 82.4 to 83.9% of held-station test rows. Within that source-path support, all six targets keep positive early-waveform gains, from 20.1% to 54.5%. A target-matched audit alone could hide amplitude-selection effects; the source-path audit shows that the gain remains when the check is based only on variables known before the target is observed.

The stronger PGV gains are physically plausible because PGV is more connected to sustained low-frequency motion than PGA. The PGA gain grows later in K-NET, where short early windows often contain incomplete high-frequency acceleration information. Spectral acceleration sits between these behaviours. The protocol does not assign a single universal lead time. It reports a target-specific curve, which is the quantity a warning system would need when choosing alarm thresholds.

Peak-capture audits define another possible shortcut. In K-NET, 69.8% of 1 s test windows and 94.7% of 10 s test windows have early horizontal peak amplitude at least 0.8 times the later PGA target. A model could then benefit by seeing part of the eventual peak. We audit a K-NET pre-peak subset where the early horizontal peak remains below 80% of the observed PGA. Early-waveform features still reduce MAE by 13.8% at 1 s and 17.9% at 3 s in that subset. The gain is smaller, but it remains present before the early window directly captures the target-scale peak.

### Gains remain positive under bootstrap and strong-tail audits

The early-waveform gain remains positive under paired resampling and in the strongest-motion tail. A paired bootstrap over held-station test records gives positive 95% confidence intervals for all six balanced targets. The smallest lower bound is 16.9% for InstanceGM SA at 1.0 s. K-NET PGA has a 49.9% mean reduction with a 95% interval of 46.6% to 53.1%. Across these targets, the empirical probability of a nonpositive gain is 0.000 under the bootstrap procedure.

The bootstrap is paired at the record level. Each resampled test set contains the same rows for the metadata-only and early-waveform models, so the interval measures the gain from adding the early waveform under the same events, stations and targets. Because absolute errors differ across targets, the paired statistic asks whether the early-waveform model improves the same prediction problem, not whether two independently sampled errors happen to differ.

The largest motions are more important for warning than the center of the distribution. We audit the strongest 5% of test records for each target. Early-waveform features reduce top-tail mean absolute error for every target, with reductions from 18.9% for InstanceGM SA at 1.0 s to 66.0% for K-NET PGA. This supports a real strong-motion gain in the damaging tail.

The tail audit also identifies an unresolved boundary. Factor-of-two underprediction generally improves with early-waveform features, but InstanceGM SA at 3.0 s shows a small worsening in the top-tail underprediction rate. This does not overturn the positive tail error reduction. It shows that reducing average tail error is not the same as eliminating missed high shaking. For early warning, this distinction is central: a method can be informative and still leave an irreducible high-consequence uncertainty region.

Residual diagnostics locate part of this boundary. K-NET PGA retains a distance-dependent residual tail after the early waveform is added. InstanceGM contains repeated high-residual records across PGA, PGV and spectral-acceleration targets. These cases are not discarded; they are separated into a residual-audit layer. The analysis reports both the information gain and the records where early P motion leaves large unexplained error.

A residual-persistence audit separates errors that are solved by longer windows from errors that remain at 10 s. In InstanceGM, 50.0% to 68.0% of the 10 s top-tail residuals are already in the top 5% at both 1 s and 3 s, and the residual sign is stable in at least 95.8% of those 10 s tail records. K-NET PGA behaves differently: only 20.0% of the 10 s top-tail residuals persist across all three windows, while 74.0% of the 1 s top-tail residuals leave the top 5% by 10 s. The remaining K-NET PGA 10 s tail is farther than the full K-NET PGA test set by 36.7 km in median source distance. The pattern separates lead-time-limited errors from residual cases that remain after the available P-window information has been used.

A residual-mechanism audit shows that the remaining large residuals are structured in covariate space (Extended Data Fig. 2). For K-NET PGA, the largest 5% of 10 s residuals shift toward longer distance, with median distance 87.8 km compared with 51.1 km for all held-station K-NET PGA records, an IQR-scaled shift of 0.80. In InstanceGM, the largest residuals concentrate in different corners depending on the target: PGV and SA at 3.0 s shift most strongly in target amplitude, while PGA and SA at 1.0 s shift most strongly in early-window amplitude. The resulting mechanism map separates path-attenuation, strong-motion-tail and early-amplitude boundaries. Across the six target series, 50% to 64% of the largest residuals are underpredictions. These correlations do not identify a single cause, but they show that the residual boundary has physical and sampling structure.

### Early-waveform gain remains against classical references

Early waveform observations outperform available classical source-path references under the same metadata limits. We include attenuation-style references and regional ground-motion equations where their input variables are available. Across the balanced targets, attenuation-reference reductions range from 17.5% to 51.6%. In K-NET, a Japanese ground-motion-model reference gives a best PGA error of 0.242 log units, while the early-waveform model reaches 0.111 log units in the corresponding test.

The OpenQuake BooreEtAl2014 reference gives another classical check under limited metadata. It uses available source distance as a proxy for rupture distance, fixes rake where focal mechanism is missing and assigns a standard reference site condition when Vs30 is absent. Under these limitations, the early-waveform model reduces MAE relative to the bias-corrected OpenQuake reference by 36.6% for InstanceGM PGA, 59.4% for InstanceGM PGV, 35.4% for SA at 0.3 s, 36.4% for SA at 1.0 s, 48.0% for SA at 3.0 s and 60.6% for K-NET PGA.

The K-NET regional screening evaluates Kanno2006, Zhao2006 and SiMidorikawa1999 variants. The best screened candidate is Kanno2006Shallow with MAE 0.242 log units on the balanced held-station split. The early-waveform model reaches 0.111 log units in the corresponding test. This is a screening comparison because the public local tables do not yet provide all rupture, site and mechanism terms required for a fully specified regional ground-motion-model study.

European Strong-Motion records provide a second regional screening layer with stronger site metadata. On the same ESM held-station rows, after excluding records without source magnitude and applying train-set median bias correction, the best screened OpenQuake regional GMM is still less accurate than the early P-window model. At 2 s, the early P+distance+site model reduces MAE relative to the best regional GMM by 34.8% for PGA and 23.8% for PGV. At 5 s, the reductions are 48.3% and 30.2%. At 10 s, they are 43.1% and 30.4%. This comparison tests the added-information result against Akkar2014, Bindi2014, Cauzzi2015 and Boore2014 candidates.

These checks keep the interpretation narrow. The early waveform supplies measured information about the current event-station path beyond the source-path variables used by the baseline and classical references. It does not remove the need for regional ground-motion modelling. The current evidence supports an added-information claim, with a clear boundary around metadata completeness.

### Uncertainty intervals reveal a transfer boundary

Regional transfer exposes the uncertainty boundary more sharply than the in-domain point-error tests. We evaluate 90% prediction intervals using target-domain conformal calibration and source-domain transfer calibration [19,20]. Target-domain conformal intervals are close to nominal coverage in the main held-station tests: K-NET PGA reaches 0.925 coverage, InstanceGM PGV reaches 0.898, and the other main targets range from 0.820 to 0.876. These values show that reasonable coverage is achievable when calibration data come from the same target domain.

The same conformal procedure fails under direct regional transfer. When intervals calibrated in the source domain are applied to the target domain, coverage drops strongly. In the 2 s and 5 s transfer tests, source-domain conformal coverage is 0.468 and 0.298, giving coverage gaps of 0.432 and 0.602 relative to nominal 0.90. Target-offset calibration restores coverage near the intended level with median interval width 2.177 log10 units. The boundary is clear: source-region residuals do not provide reliable target-region uncertainty without target-region calibration.

The transfer error curves show the same effect. In zero-shot Japan-to-Europe transfer, median error ratios increase from 2.25 at 1 s to 4.27 at 10 s. Target-offset calibration reduces the ratios but does not remove the penalty, with ratios from 1.40 at 1 s to 2.46 at 10 s. On the ESM external set, the best 10 s target-offset transfer still leaves error ratios of 2.53 for PGA and 1.58 for PGV. More early waveform information improves in-domain prediction, yet it can also amplify learned regional differences when moved without calibration.

The transfer pattern makes uncertainty central to the evidence. If the calibration residuals are exchangeable between the calibration and test samples, conformal intervals can produce reliable coverage with few modelling assumptions. Regional transfer breaks that exchangeability. A source-domain residual distribution can be too narrow, biased or shaped by a different network. Target-offset calibration repairs much of the coverage by using target-domain residual information, but the resulting intervals remain wide. The practical message is direct: a warning model can carry early waveform information across regions only with target-region calibration and explicit interval widening.

The interval width is part of the boundary. A method can restore nominal coverage by making intervals so wide that the prediction loses warning value. Target-offset calibration shows both sides of the tradeoff: coverage returns to about 0.90, while the median interval width reaches 2.177 log10 units. That width is a signal, not a formatting nuisance. It says that cross-region uncertainty remains large even after simple target-domain correction.

### External datasets support the same boundary

Independent AQ2009GM, CWA and European checks reproduce the same boundary: in-domain early-waveform gains persist, while cross-region transfer stays penalized. The European Strong-Motion processing currently includes 951 downloaded event archives, producing 134,250 event-station rows from 861 events and 1,568 stations. The external Europe tests confirm that cross-regional transfer is harder than in-domain held-station prediction. P-arrival sensitivity checks show median shifts of 2.517 s under delayed picks and 2.130 s under advanced picks. For 86 high-confidence records, the median offset is 1.223 s and the 95th percentile is 3.960 s. These values justify treating pick uncertainty as part of the transfer error budget.

European Strong-Motion records also test a different P-arrival regime. The local ASCII headers used here do not provide explicit catalog P picks for all records, so the compact feature tables use a theoretical P-onset estimate. A velocity sensitivity audit changes the assumed P velocity from 6.0 to 5.5 and 6.5 km/s. Retained-window validity remains above 0.994 across tested windows, while timing shifts reach multi-second medians. This positions ESM as an external-domain check and transfer target. It also limits any claim that depends on exact catalog P arrivals.

AQ2009GM provides an additional regional check with 345,226 extracted rows, 60,310 events and 66 stations in the current processed feature tables. The streaming validation covers all 254 local manifest chunks, retains compact feature tables and removes raw chunk files after extraction. In 5 s held-station tests, AQ2009GM shows 55.8% PGA and 71.9% PGV reductions from early-waveform features. These results support the same early-information pattern in a separate archive.

CWA adds an official Taiwan PGA/PGV check from the public 2011 benchmark year. The retained feature table contains 5,882 eligible records from 775 events and 705 stations. In held-station tests with 120 held stations, early-waveform features reduce metadata-only MAE by 14.6% for PGA and 17.7% for PGV at 2 s, and by 29.9% for PGA and 40.3% for PGV at 5 s. The raw CWA HDF5, metadata and downloaded tar archive were removed after the derived feature table was written.

The four-domain transfer synthesis combines InstanceGM, K-NET, AQ2009GM and ESM. The transfer model uses early-waveform features and excludes magnitude, distance, site variables, event identifiers and station identifiers. This design measures the waveform-domain boundary directly. All cross-domain rows have higher MAE than target-domain training. Median zero-shot penalties rise from 2.25 times target-domain error at 1 s to 4.27 times at 10 s. Offset calibration reduces the penalty but leaves ratios above one at every window.

Together, the external datasets point to the same conclusion. Early P waves contain measurable information for later strong shaking. The information is strongest when training, calibration and test data share a regional distribution. Cross-regional use requires target calibration, and even calibrated transfer keeps a sizable penalty.

This is the difference between in-domain prediction and regional portability. Longer windows add information inside the target domain, but the same extra information can encode region-specific path, site and instrument behaviour. The increasing zero-shot penalty with window length supports that interpretation. The evidence argues for local calibration before deployment.

## Discussion

The first seconds after P arrival consistently reduce held-station error in PGA, PGV and SA targets across the tested public strong-motion records. The gains survive paired bootstrap tests, source-path support checks, strong-tail audits and residual-persistence checks. The evidence supports an information-boundary claim, not a claim that all damaging shaking is predictable from the first P seconds.

The boundary should be read per target and per region. PGA, PGV and SA respond differently to added P-window length, and regional transfer changes both point error and interval width. A single aggregate skill score would hide these dependencies. This protocol reports curves across window length, split type and calibration regime so that each region can see whether the added early waveform information is large enough for the warning quantity it uses, and where residual risk remains too large.

The boundary is equally important. Direct uncertainty transfer fails across regions, and zero-shot prediction from Japan to Europe or Australia carries large error penalties. Target-offset calibration repairs much of the interval coverage, but it does not recover in-domain accuracy. A regional early-warning model should not export its uncertainty intervals unchanged to another tectonic and instrumental setting.

The tail results also set a practical limit. Early-waveform features reduce tail error, yet some high-period spectral-acceleration underprediction remains. The first seconds of P motion can be informative without being sufficient for all damaging-motion cases. This is the part of the result that matters most for risk communication. A warning model should report when it is outside its reliable information regime.

The analysis also clarifies the role of model complexity. The claim does not require a large waveform neural network. Compact early-window features and tree regressors are enough to show the information curve, the held-station gain and the transfer penalty. A neural model may improve some targets, especially where waveform shape contains phase and duration information beyond the compact summaries. Such a model would still need the same held-station, strong-tail and regional-calibration tests.

The evidence supports three operational implications. First, early waveform observations should be used alongside source-path metadata, because they add station-specific information before the strongest shaking. Second, uncertainty calibration must be regional. Third, evaluation should include held-station splits and strong-tail audits, because random-split averages can hide the failures that matter during damaging earthquakes.

For an operational system, these implications translate into a simple validation checklist. A candidate model should show positive gain over source-path metadata on held stations, retain positive gain in the strongest-motion tail, report interval coverage on a target-domain calibration set, and disclose its cross-region penalty before it is moved to another network. The checklist is intentionally model-agnostic. It can be applied to gradient-boosted trees, convolutional networks, transformers or physics-informed hybrids.

The scientific contribution is the boundary itself. The data show measurable early-waveform information, a target-specific lead-time curve, persistent high-residual cases and a regional calibration cost. These four observations make the result useful beyond the present models: any stronger waveform model should move the curve, shrink the residual set or reduce the calibration cost under the same held-station and transfer tests.

Several limitations remain. Public datasets differ in instrumentation, metadata completeness, picking accuracy and target definitions. ESM currently uses a theoretical P-onset estimate, so ESM supports regional-transfer evidence more strongly than catalog-P lead-time evidence. The current classical comparisons are constrained by rupture-distance, site-term and mechanism availability. Prospective warning performance also requires latency, telemetry, real-time picking and decision thresholds that are outside this offline benchmark.

These limitations define the proposed benchmark. They show which evidence can be claimed now and which evidence needs additional data. The strongest present claim is the measured information boundary in public strong-motion records. The next claim, operational performance, would require prospective tests in a live warning environment with network latency and target-region calibration.

The current results also separate two common claims. Early P waves are informative for later strong motion in the tested public datasets. That does not mean that every damaging motion is predictable from the first seconds alone. The unresolved tail and the cross-region interval widening show where the early signal runs out. A warning system should expose that limit to downstream decision rules.

The protocol turns a broad early-warning question into a measurable curve. Each region can be tested by the same steps: construct event-station samples, split by held events and stations, measure the information gain from 1 to 10 s of P waves, and calibrate intervals on target-domain residuals. The curve gives a direct way to decide where early P-wave prediction helps practical local decision thresholds, where it is uncertain, and where a warning system needs more than the early waveform can provide.

## Methods

### Data sources and sample construction

We used public strong-motion datasets that provide waveform records and event-station metadata. The main benchmark uses InstanceGM and K-NET. Supporting analyses use European Strong-Motion records, AQ2009GM and CWA. PNWAccelerometers is retained as a supplementary accelerometer peak-amplitude check only. Each event-station record was converted to a common manifest with dataset name, event identifier, station identifier, component information, sampling metadata, P-arrival reference, source-path variables and target ground-motion values.

Rows enter a target-specific experiment only when the waveform pointer is readable and at least one requested ground-motion target is positive and finite. The feature builders preserve the original event and station identifiers so that all grouped splits can be audited after feature extraction. For the main waveform tables, very long records were capped by the configured sample-count filter to keep local feature generation tractable and to avoid mixing full-record duration effects with early-window information.

The K-NET archive was converted from local BSON files. Complete records require three components and usable event-station metadata. The conversion stores variable-length waveform arrays in ZNE order and preserves sample boundaries for each record. K-NET acceleration is treated as gal, equivalent to centimetres per second squared. This convention is used only after unit provenance checks.

AQ2009GM was processed through chunk streaming. Each manifest chunk was downloaded or read, compact early-window features and PGA/PGV targets were extracted, and raw HDF5 and metadata chunk files were removed after the derived features were written. The retained inventory contains 254 chunks with zero extraction errors and 345,226 valid PGA/PGV records.

CWA was processed as a one-year official PGA/PGV supplement. The 2011 records were extracted from the public SeisBench CWA archive, compact 2 s and 5 s post-P waveform features were computed, and the raw HDF5, metadata and tar archive were deleted after the feature table was written. The retained table contains 5,882 valid PGA/PGV records with zero waveform read errors.

European Strong-Motion records were processed from local ASCII zip packages. The compact feature extraction reads the original packages without modifying them. Because explicit P picks are not available for all local ESM headers, the retained windows use a theoretical P-onset estimate from epicentral distance and an assumed P velocity. Timing sensitivity and waveform-envelope spot checks quantify the uncertainty introduced by this choice.

For each record, early waveform windows were cut from the P arrival with lengths of 1, 2, 3, 5 and 10 s. Windows with insufficient samples or missing target variables were excluded from the corresponding target-specific table. The target variables were log-transformed PGA, PGV and available SA ordinates. Derived feature tables allow most experiments to be reproduced without retaining the full raw waveform files locally.

The target transformation is applied after checking that the physical target is positive. Model errors are reported in log10 target units. This makes PGA, PGV and SA comparable at the level of relative multiplicative error, and it also makes factor-of-two underprediction checks a fixed threshold of approximately 0.3 log10 units.

### Early-window features

The primary feature representation uses compact waveform summaries from the early P-window. These include amplitude statistics, absolute and squared amplitude summaries, cumulative energy, envelope summaries, component-wise ratios and simple frequency-domain summaries. The feature design is intentionally simple. It avoids using target-window information and keeps the comparison focused on how much information is already present in the early P motion.

The tabular strong-motion features used in the main held-out experiments are computed separately on the vertical, north and east components. For each component we retain the maximum absolute amplitude, root mean square amplitude, standard deviation and 95th percentile of absolute amplitude. We also retain the horizontal vector maximum from the two horizontal components, and the three-component vector maximum and vector root mean square. These summaries are computed only inside the P-window.

For the full-manifest AQ2009GM validation, the compact features are velocity-based and paired with official PGA/PGV metadata targets. For CWA and ESM, the features include component absolute maximum, root mean square, standard deviation, 95th-percentile absolute amplitude, horizontal maximum, vector maximum and vector root mean square. Full-record peak features are excluded from predictive feature sets.

Metadata features include magnitude, source depth, source distance, station elevation, Vs30 where available, event year and sample count. Station or regional labels are used only in experiments that explicitly test whether such information changes transfer or uncertainty behavior. The baseline model uses source-path metadata without early-window waveform features. The early-waveform model adds the P-window feature set.

Cross-region waveform-transfer experiments use the intersection of waveform columns available across InstanceGM, K-NET, AQ2009GM and ESM. For these tests each waveform summary is transformed as log10(abs(x) + 1e-12), and magnitude, distance, site variables, event identifiers and station identifiers are excluded. This construction isolates transfer of the early waveform representation itself.

### Splits and models

We used grouped splits to avoid leakage. The held-station split keeps station identifiers disjoint between training and test sets. Held-event checks keep event identifiers disjoint. Random splits are reported as easier reference tests, not as the main evidence. Split audits verify zero group overlap for the main held-out tests.

The grouped splits are built before target-specific row filtering within each feature table. For held-station tests, station keys combine network and station codes when both are available. For held-event tests, event identifiers define the held-out groups. The split metadata table records eligible rows, eligible groups, selected train and test rows, train and test group counts and group overlap. Any nonzero overlap fails the verification run.

The regressors are histogram gradient boosting and XGBoost-style tree ensembles depending on the experiment table. The common tabular regressor is a median-imputed histogram gradient boosting model with 200 boosting iterations, learning rate 0.05, 31 maximum leaf nodes, L2 regularization 0.01 and random state 17. Hyperparameters are kept conservative and fixed across related targets where possible. Model comparison is not the aim. Stable models estimate the information added by the early waveform under the same split and target definition.

Random splits use seed 19. Held-event and held-station strong-motion splits use seed 31, with a fixed offset for station holdout. AQ2009GM uses seed 43. ESM uses seed 71. PNWAccelerometers uses seed 83. Phase-audit sampling uses seed 7. Conformal intervals use seed 17. Boundary sensitivity repeats seeds 17, 59 and 101.

Performance is reported as mean absolute error in log target units and as relative reduction compared with the source-path baseline. Relative error reduction is 100 times the baseline MAE minus the early-waveform MAE, divided by the baseline MAE. Positive values mean that early-waveform features improve the prediction under the same split.

### Support, bootstrap and tail audits

The source-path support audit restricts held-station test rows to magnitude and distance ranges supported by the training data. The range uses the central training support and does not condition on the observed target amplitude, separating source-path interpolation from target-matched post-hoc checks.

Uncertainty in relative error reduction was estimated with paired bootstrap resampling of test records. Each bootstrap draw resamples records with replacement and recomputes the paired baseline and early-waveform errors. The held-station bootstrap uses 2,000 resamples with seed 20260620. Confidence intervals are empirical 2.5 and 97.5 percentile bounds of the bootstrap distribution.

Strong-tail audits focus on the top 5% of target amplitudes in each held-station test. We report tail mean absolute error reduction and factor-of-two underprediction rates. This separates ordinary average-error gains from high-consequence underprediction behavior.

Factor-of-two underprediction is defined as a prediction more than 0.3 log10 units below the observed target. This threshold is evaluated within target-specific top-tail subsets, so a model can reduce tail MAE and still be flagged if it increases severe underprediction in a high-amplitude subset.

The residual-persistence audit joins the 1 s, 3 s and 10 s residual tables by event-station record and target. Top-tail residuals are defined as the largest 5% of absolute residuals within each dataset, target and window. We report the fraction of 10 s top-tail records that are also top-tail at 1 s and 3 s, the fraction of 1 s top-tail records that leave the top-tail set by 10 s, residual-sign stability and the median source-distance shift of the remaining 10 s tail.

The residual-mechanism audit compares the largest 5% of 10 s absolute residuals with all 10 s held-station residuals for the metadata-plus-early-waveform model. For each dataset-target pair, we compute median shifts in source distance, magnitude, source depth, Vs30 where available, log early-window vector amplitude and observed log target. Shifts are divided by the interquartile range of the full held-station distribution for the same variable. This gives a scale-free description of where large residuals concentrate without fitting another explanatory model.

The dominant shifted covariate is mapped to a residual-boundary class. Distance-dominated tails are labelled path-attenuation boundaries. Target-amplitude tails are labelled strong-motion-tail boundaries. Early-amplitude tails are labelled early-amplitude boundaries. This classification is descriptive. It is used to report where large errors concentrate after the early-window model has used source-path and site metadata, not to assign causal mechanisms.

The pre-peak audit is performed on K-NET PGA. It compares the early horizontal peak amplitude with the final PGA target and retains records below a chosen ratio threshold. The main threshold is 0.8. The test asks whether early-window gains remain when the early window has not already captured target-scale horizontal acceleration.

### Classical references and regional GMM screening

Classical references are evaluated on the same held-out feature tables where their input variables are available. Low-parameter attenuation-style references use magnitude and distance terms. OpenQuake BooreEtAl2014 references use source distance as an Rjb proxy, rake fixed to 0, Vs30 where available and 760 m/s where missing. Predictions are bias-corrected by the median training residual before test evaluation.

The K-NET regional screening uses OpenQuake Kanno2006, Zhao2006 and SiMidorikawa1999 variants for PGA. The local K-NET tables do not contain Vs30, rupture-distance geometry or focal-mechanism fields, so these comparisons are reported as screening references. They test whether the early-waveform model is only beating a weak source-path baseline.

The ESM regional GMM screening uses BooreEtAl2014, AkkarEtAl2014, BindiEtAl2014 and CauzziEtAl2015 candidates for PGA and PGV. Rows without source magnitude are excluded because every screened GMM requires magnitude. Rjb models use `source_distance_km`; Rhyp and Rrup models use `path_hyp_distance_km`. Vs30 is clipped to 150-1500 m/s and missing Vs30 is set to 760 m/s for the GMM calculation. The early P+distance+site comparator is retrained on the same rows and split as the GMM screening.

### Uncertainty and transfer evaluation

Prediction intervals were evaluated with conformal calibration. Target-domain conformal intervals use calibration residuals from the same target domain. Source-domain transfer intervals use residuals from the source region and apply them to the target region. Target-offset calibration adds a small target-domain residual correction.

For the balanced held-station conformal experiment, the training table is shuffled with seed 17 and split into a proper training subset and a calibration subset. The calibration subset contains at least 100 records and otherwise 20% of the available training rows. The 90% interval half-width is the split-conformal quantile of the absolute calibration residuals, computed with the finite-sample quantile index ceil((n + 1)(1 - alpha)) at alpha = 0.1.

Cross-regional transfer tests train models in one region and evaluate in another. We report error ratios relative to target-domain models or target baselines. The Japan-to-Europe and Japan-to-Australia analyses measure how early-waveform information, source-path metadata and calibration behave when the waveform distribution and network conditions change.

The transfer-boundary model intentionally removes magnitude, distance, site variables, event identifiers and station identifiers. This isolates early-waveform-domain transfer. Within-domain target models provide the reference error. Zero-shot transfer trains on a source dataset and evaluates on the target test split. Target-offset transfer applies one scalar correction equal to the median target-training residual under the source model. Target-offset conformal intervals then use the target-training residual distribution after this scalar correction.

Boundary sensitivity repeats the four-domain transfer calculation for 2 s and 5 s windows over seeds 17, 59 and 101. The same run writes point-error, conformal-coverage, interval-width and top-tail underprediction tables. The core Figure 7 boundary uses the median behaviour across those repeated transfer checks.

### Software and reproducibility

All scripts were run locally in the project environment. The verified run used Python 3.12.13 with numpy 2.4.4, pandas 3.0.2, scikit-learn 1.8.0, matplotlib 3.10.8, Pillow 12.2.0, h5py 3.16.0, SeisBench 0.11.5 and OpenQuake engine 3.25.1. Derived tables, figures and audit summaries are stored in the repository under the `work` and `outputs` trees. Raw waveform data remain external and should be obtained from their public providers. Before submission, the public code archive should contain exact data-access instructions and only the files needed to regenerate the reported tables and figures.

A verification script checks the reported record counts, split group overlap, main error reductions, bootstrap bounds, strong-tail metrics, conformal coverage, transfer-boundary tables, residual-persistence outputs, figure files and generated PDF text. The script also checks that the manuscript does not advertise missing display items and that agent-marker text is absent from the official-format manuscript and PDF.

## Data availability

This study uses public strong-motion data sources, including InstanceGM, K-NET, European Strong-Motion records, AQ2009GM and CWA. Derived feature tables and split manifests will be released with the final repository or an archival deposit. Raw waveform redistribution will follow the terms of the original data providers. The current draft does not yet contain final repository DOIs or provider-specific access statements.

## Code availability

Analysis code, figure-generation scripts and verification scripts are available in the local project repository. A clean public release will be prepared before submission, with commands for regenerating the tables and figures used in the manuscript.

## Acknowledgements

The authors acknowledge the public data providers and open-source software communities whose resources made this benchmark possible.

Funding: none.

## Author contributions

Z.H. designed and implemented the benchmark analyses, processed the derived feature tables, generated the figures and drafted the manuscript. Q.M. supervised the study, advised the scientific framing and reviewed the manuscript. Both authors approved the manuscript draft.

## Competing interests

The authors declare no competing interests.

## Tables

**Table 1 | Evidence layers and retained public data.**

| Evidence layer | Retained data | Main targets | Role in the claim |
| --- | --- | --- | --- |
| Main in-domain benchmark | InstanceGM: 1,159,223 records; K-NET: 22,119 records | PGA, PGV, SA where available | Measures held-event and held-station early-window information gain |
| External strong-motion checks | AQ2009GM: 345,226 rows; ESM: 134,250 rows; CWA: 5,882 rows | PGA, PGV | Tests whether the information-gain pattern persists outside the main archives |
| Phase-window quality control | STEAD, Iquique, K-NET and InstanceGM phase audits | P and S pick offsets | Checks whether the P-window construction is stable enough for the main task |
| Supplementary robustness | PNWAccelerometers peak-amplitude check | Peak acceleration proxy | Tests an accelerometer-only boundary where official PGA/PGV targets are absent |

\clearpage

**Table 2 | Main early-window information checks.**

| Check | Window or subset | Result | Interpretation |
| --- | --- | --- | --- |
| Main held-station gain | 10 s | InstanceGM PGA 35.5%, PGV 52.6%, SA03 26.0%, SA10 20.9%, SA30 27.8%; K-NET PGA 49.9% | Early waveform features add information beyond source-path metadata at unseen stations |
| Paired bootstrap | Held-station rows | All six balanced targets have positive 95% intervals; K-NET PGA 49.9% [46.6%, 53.1%] | The gain is stable under record-level resampling |
| Strongest-motion tail | Top 5% targets | Tail MAE reductions range from 18.9% to 66.0% | The gain reaches high-consequence records |
| Pre-peak K-NET subset | 1 s and 3 s | MAE reductions of 13.8% and 17.9% | The gain remains before the early window captures the later PGA-scale peak |

**Table 3 | Transfer and uncertainty boundary checks.**

| Check | Result | Boundary shown |
| --- | --- | --- |
| Target-domain conformal calibration | 90% interval coverage ranges from 0.820 to 0.925 in main held-station tests | In-domain residuals can support useful uncertainty calibration |
| Source-domain conformal transfer | Coverage falls to 0.468 at 2 s and 0.298 at 5 s | Source-region residuals under-cover target regions |
| Target-offset calibration | Coverage returns near nominal with median width 2.177 log10 units | Restored coverage carries a large interval-width cost |
| Zero-shot regional transfer | Median error ratios rise from 2.25 at 1 s to 4.27 at 10 s | More early waveform information can amplify regional mismatch without calibration |

## Figure legends

**Figure 1 | Public-data benchmark design links each evidence layer to an event-station prediction task.** InstanceGM and K-NET anchor the main in-domain strong-motion tests, AQ2009GM, CWA and European Strong-Motion records test external checks, and STEAD/Iquique support phase-window quality control. The workflow panel shows how public waveforms become P-window features, strong-motion targets, split tests and uncertainty checks.

**Figure 2 | Longer P windows add strong-motion information, with target-dependent saturation.** Early-waveform features reduce mean and tail errors from short windows onward, while combined-model error and skill show that PGA, PGV and spectral acceleration do not share a single universal lead-time curve.

**Figure 3 | Held-out tests show that the early-waveform gain survives held events and unseen stations.** Positive held-event and held-station gains remain after group-overlap checks, while distribution panels expose the magnitude, distance and PGA shifts that make the held-station setting a harder deployment test.

**Figure 4 | Early waveform observations improve over available classical references and require explicit calibration.** Bias-corrected OpenQuake comparisons show added information beyond source-path terms, and conformal panels show where prediction intervals approach or miss nominal coverage. Regional GMM screening is reported in the Results and Supplementary tables.

**Figure 5 | Residual structure marks the part of strong shaking that early P waves still leave uncertain.** Error reductions coexist with distance-dependent residual tails and repeated high-residual records, separating early-waveform information from unresolved strong-motion cases.

**Figure 6 | P-window alignment is stable enough for the main task, while S picks remain dataset dependent.** Cross-dataset picker audits show small P-pick errors for the main early-window construction and larger S-pick tails, supporting a P-window benchmark instead of a broad phase-transfer claim.

**Figure 7 | The predictability boundary is positive in-domain and fragile under direct regional transfer.** Within-domain gains increase with P-window length, cross-region error ratios grow without target calibration, source-domain conformal intervals under-cover target regions, and the strongest-motion tail keeps a visible underprediction boundary.

**Extended Data Figure 1 | Waveform case audits identify records that carry large residuals after early-waveform modelling.** Repeated InstanceGM high-residual records and K-NET PGA waveform cases show where the benchmark should guide additional physical or site-specific analysis.

**Extended Data Figure 2 | Large residuals concentrate in specific covariate corners instead of spreading uniformly.** Dominant IQR-scaled median shifts separate path-attenuation, strong-motion-tail and early-amplitude boundaries. The underprediction panel shows that these high-residual cases are modestly biased toward underprediction, supporting a tail-risk boundary without treating the covariate shifts as causal attribution.

## References

1. Kanamori, H. Real-time seismology and earthquake damage mitigation. Annual Review of Earth and Planetary Sciences 33, 195-214 (2005). https://doi.org/10.1146/annurev.earth.33.092203.122626

2. Allen, R. M. & Melgar, D. Earthquake early warning: advances, scientific challenges, and societal needs. Annual Review of Earth and Planetary Sciences 47, 361-388 (2019). https://doi.org/10.1146/annurev-earth-053018-060457

3. Michelini, A., Cianetti, S., Gaviano, S., Giunchi, C., Jozinovic, D. & Lauciani, V. INSTANCE - the Italian seismic dataset for machine learning. Earth System Science Data 13, 5509-5544 (2021). https://doi.org/10.5194/essd-13-5509-2021

4. National Research Institute for Earth Science and Disaster Resilience. NIED K-NET, KiK-net. National Research Institute for Earth Science and Disaster Resilience (2019). https://doi.org/10.17598/NIED.0004

5. Luzi, L. et al. The Engineering Strong-Motion Database: a platform to access pan-European accelerometric data. Seismological Research Letters 87, 987-997 (2016). https://doi.org/10.1785/0220150278

6. Bagagli, M., Valoroso, L., Michelini, A., Cianetti, S., Gaviano, S., Giunchi, C., Jozinovic, D. & Lauciani, V. AQ2009 - The 2009 Aquila Mw 6.1 earthquake aftershocks seismic dataset for machine learning application. Istituto Nazionale di Geofisica e Vulcanologia (INGV) (2023). https://doi.org/10.13127/AI/AQUILA2009

7. Mousavi, S. M., Sheng, Y., Zhu, W. & Beroza, G. C. STanford EArthquake Dataset (STEAD): a global data set of seismic signals for AI. IEEE Access 7, 179464-179476 (2019). https://doi.org/10.1109/ACCESS.2019.2947848

8. Woollam, J. et al. SeisBench - a toolbox for machine learning in seismology. Seismological Research Letters 93, 1695-1709 (2022). https://doi.org/10.1785/0220210324

9. Zhu, W. & Beroza, G. C. PhaseNet: a deep-neural-network-based seismic arrival-time picking method. Geophysical Journal International 216, 261-273 (2019). https://doi.org/10.1093/gji/ggy423

10. Mousavi, S. M., Ellsworth, W. L., Zhu, W., Chuang, L. Y. & Beroza, G. C. Earthquake transformer - an attentive deep-learning model for simultaneous earthquake detection and phase picking. Nature Communications 11, 3952 (2020). https://doi.org/10.1038/s41467-020-17591-w

11. Boore, D. M., Stewart, J. P., Seyhan, E. & Atkinson, G. M. NGA-West2 equations for predicting PGA, PGV, and 5% damped PSA for shallow crustal earthquakes. Earthquake Spectra 30, 1057-1085 (2014). https://doi.org/10.1193/070113EQS184M

12. Akkar, S., Sandikkaya, M. A. & Bommer, J. J. Empirical ground-motion models for point- and extended-source crustal earthquake scenarios in Europe and the Middle East. Bulletin of Earthquake Engineering 12, 359-387 (2014). https://doi.org/10.1007/s10518-013-9461-4

13. Bindi, D. et al. Pan-European ground-motion prediction equations for the average horizontal component of PGA, PGV and 5%-damped PSA at spectral periods up to 3.0 s using the RESORCE dataset. Bulletin of Earthquake Engineering 12, 391-430 (2014). https://doi.org/10.1007/s10518-013-9525-5

14. Cauzzi, C., Faccioli, E., Vanini, M. & Bianchini, A. Updated predictive equations for broadband (0.01-10 s) horizontal response spectra and peak ground motions, based on a global dataset of digital acceleration records. Bulletin of Earthquake Engineering 13, 1587-1612 (2015). https://doi.org/10.1007/s10518-014-9685-y

15. Kanno, T. et al. A new attenuation relation for strong ground motion in Japan based on recorded data. Bulletin of the Seismological Society of America 96, 879-897 (2006). https://doi.org/10.1785/0120050138

16. Zhao, J. X. et al. Attenuation relations of strong ground motion in Japan using site classification based on predominant period. Bulletin of the Seismological Society of America 96, 898-913 (2006). https://doi.org/10.1785/0120050122

17. Si, H. & Midorikawa, S. New attenuation relationships for peak ground acceleration and velocity considering effects of fault type and site condition. Journal of Structural and Construction Engineering 64, 63-70 (1999). https://doi.org/10.3130/aijs.64.63_2

18. Pagani, M. et al. OpenQuake Engine: an open hazard and risk software for the Global Earthquake Model. Seismological Research Letters 85, 692-702 (2014). https://doi.org/10.1785/0220130087

19. Vovk, V., Gammerman, A. & Shafer, G. Algorithmic Learning in a Random World. Springer (2005). https://doi.org/10.1007/b106715

20. Angelopoulos, A. N. & Bates, S. Conformal prediction: a gentle introduction. Foundations and Trends in Machine Learning 16, 494-591 (2023). https://doi.org/10.1561/2200000101
