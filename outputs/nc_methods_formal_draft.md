# Methods Draft for NC Submission

## Data Sources

The benchmark uses STEAD, InstanceGM, Iquique, K-NET, AQ2009GM, CWA, PNWAccelerometers, and local ESM strong-motion packages. SeisBench provides STEAD, InstanceGM, Iquique, AQ2009GM, CWA, and PNWAccelerometers. K-NET was converted from the approved local BSON package into HDF5 and CSV metadata with `UD`, `NS`, and `EW` mapped to `Z`, `N`, and `E`. K-NET acceleration is reported in gal, equivalent to `cm/s2`. ESM features were extracted from local ASCII zip packages without modifying the original archives.

The unified manifest stores record identifiers, dataset names, waveform paths, component order, available P and S picks, source metadata, station metadata, and ground-motion targets.

## Early-Window Features and Targets

Waveforms with catalog P arrivals were aligned to the P pick. Early windows were extracted at 1, 2, 3, 5, and 10 s where retained feature tables were available. The main InstanceGM/K-NET random figures use 1, 3, and 10 s; the held-station scan, AQ2009GM, ESM, and transfer synthesis include 2 and 5 s. Features include component absolute maximum, RMS, standard deviation, 95th-percentile absolute amplitude, horizontal maximum, vector maximum, and vector RMS. Full-record peak features were excluded from predictive feature sets.

Targets were modeled in log10 units. InstanceGM targets include PGA, PGV, SA03, SA10, and SA30. K-NET provides PGA. AQ2009GM and CWA provide metadata PGA and PGV. ESM PGA and PGV were computed from paired ACC.AP and VEL.AP streams. PNWAccelerometers is retained as a supplementary peak-amplitude check because the local HDF5 cache lacks waveform unit metadata.

CWA is included as a one-year official metadata-target supplement. The 2011 metadata and waveform HDF5 were extracted from the public benchmark archive, compact 2 s and 5 s post-P waveform features were computed, and the raw HDF5, metadata, tar archive and failed-download cache were deleted after feature extraction. The retained table has 5,882 eligible PGA/PGV records from 775 events and 705 stations. This layer is used as a Taiwan check; it is not a full 2011-2021 CWA validation.

ESM headers do not provide explicit P arrivals. ESM windows use a theoretical onset from origin time, first sample time, epicentral distance, depth, and `Vp = 6 km/s`. The sensitivity audit tested `Vp = 5.5` and `6.5 km/s`; retained-window validity stayed above 0.99, while median onset shifts were about 2.1-2.5 s. ESM is used as an external supplement and transfer-domain check.

An ESM waveform-onset spot audit sampled 200 event-station records across distance and PGA quantiles and compared the theoretical onset with an automated three-component acceleration-envelope onset proxy. The audit detected 86 high-confidence proxies with median absolute offset 1.223 s and q95 absolute offset 3.960 s. This check supports ESM as an external timing sanity check. It is not a manual or catalog P-pick validation.

## Splits and Models

Random splits measure baseline information gain. Held-event splits remove selected events from training. Held-station splits remove selected stations from training. Balanced held-station splits hold out 50 stations per main strong-motion dataset and sample test records while preserving station coverage. Split files record train groups, test groups, and group overlap; verified held-out overlap is zero.

The main regressor is `HistGradientBoostingRegressor` with fixed settings across experiments. Feature sets include median-only, metadata-only, early-waveform-only, and metadata plus early-waveform models. Metadata features include magnitude, depth, distance, station elevation, Vs30 where available, year, and sample count. Cross-region transfer uses early waveform features only and excludes distance, magnitude, site terms, event identifiers, and station identifiers.

Random seeds are fixed in the released scripts. Main random-split sampling uses seed 19. Held-event and held-station strong-motion splits use seed 31, with a +101 offset for station holdout. AQ2009GM streaming validation uses seed 43, CWA uses seed 47, ESM held-out validation uses seed 71, PNWAccelerometers uses seed 83, phase-audit sampling uses seed 7, conformal intervals use seed 17, and the 2/5 s boundary sensitivity repeats seeds 17, 59, and 101. Sampling scripts write split-info tables with train groups, test groups, and overlap counts.

## Classical References

Classical references include an attenuation-shaped ridge model, bias-corrected OpenQuake BooreEtAl2014, K-NET Japanese GMM screening, and ESM regional GMM screening. BooreEtAl2014 uses source distance as an Rjb proxy, rake fixed at 0, missing Vs30 set to 760 m/s, and train-set median bias correction. K-NET GMM screening uses source distance as an Rrup proxy and missing Vs30 defaults.

The ESM regional screening evaluates BooreEtAl2014, AkkarEtAl2014, BindiEtAl2014, and CauzziEtAl2015 candidates for PGA and PGV on held-station rows. Records without source magnitude are excluded. Rjb models use source distance, Rhyp/Rrup models use hypocentral distance, Vs30 is clipped to 150-1500 m/s, missing Vs30 is set to 760 m/s, and predictions are bias-corrected by the train-set median residual. These comparisons are reference checks under documented metadata limits. A fully specified regional GMPE/GMM comparison requires curated rupture distance, site terms, and tectonic or focal-mechanism metadata.

## Uncertainty and Boundary Analysis

Split-conformal intervals use a proper-training and calibration split within training records. Coverage is evaluated on held-station test records. The exchangeability condition is explicit: calibration and test residuals must come from the same residual distribution for finite-sample marginal coverage to apply. Source-domain conformal transfer intentionally violates this condition and measures the uncertainty-transfer boundary. Target-offset conformal calibration uses the target-domain training split before target test evaluation.

Residuals are predicted log10 target minus observed log10 target. Residual audits evaluate binned behavior by source, path, station, and early waveform variables, then select high-residual cases for waveform-level inspection. The residual-mechanism class table maps the dominant shifted covariate in each series to path-attenuation, strong-motion-tail, or early-amplitude boundaries. This classification is descriptive and does not assign causal mechanisms. Figure-style audits record Figure 1-7 dimensions and provide a contact sheet for final production review.

## Software and Local Data Access

Analyses were run in the local `zhy` environment with Python 3.12.13, numpy 2.4.4, pandas 3.0.2, scikit-learn 1.8.0, matplotlib 3.10.8, Pillow 12.2.0, h5py 3.16.0, SeisBench 0.11.5, and OpenQuake engine 3.25.1. SeisBench caches are read from `/Users/yojironoda/.seisbench/datasets`. K-NET is read from `/Users/yojironoda/Downloads/s7rk7bj3zn-1/knet_1530`. ESM zip packages are read from `/Users/yojironoda/Documents/New project 2/outputs/strong_motion_downloads/欧洲_ESM`. CWA raw files were removed after the derived feature table was generated. Raw data redistribution must follow each source archive license; reproducible release files should include scripts, split files, figure tables, verifier output, and derived feature tables where licensing allows.
