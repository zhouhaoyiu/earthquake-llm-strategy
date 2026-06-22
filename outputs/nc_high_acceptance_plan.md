# NC High-Acceptance Plan

Date: 2026-06-21

## Position

Aim for Nature Communications with the narrowed story:

**Cross-regional predictability limits of strong shaking from the first seconds of P waves.**

Lead with the public benchmark, held-out early-window gains, uncertainty calibration, and cross-region transfer boundary.

## Probability

Current verified figure-ready package plus AQ2009GM full-manifest chunk-streaming, CWA official PGA/PGV one-year layer, ESM European strong-motion validation, ESM regional GMM screening, four-domain transfer boundary, ESM waveform-onset spot audit, residual-persistence audit, residual-mechanism classes, author metadata and DOI-backed references: **65-70%**.

With clean data/code availability statements, source-data package and final archive DOI: **66-71%**.

With one more major independent layer, such as manual ESM P picks or a fully specified regional GMM comparison with curated rupture/site/mechanism fields: **68-73%**.

Treat **70-80%** as a gate, not a current probability. AQ2009GM full-manifest chunk-streaming and CWA 2011 now support early-window information in two additional SeisBench ground-motion datasets with official PGA/PGV metadata targets. ESM adds an external European strong-motion domain and a regional GMM screening layer. Four-domain transfer adds a measurable boundary: zero-shot median MAE penalty rises from 2.25x at 1 s to 4.27x at 10 s. The residual-persistence and residual-mechanism audits make the unresolved tail inspectable. A defensible 70-80% estimate still needs manual ESM P picks, a fully specified regional GMM layer, or a stronger independent physical mechanism layer.

## Must-Have Work

1. **Official K-NET unit verification**

   Done at documentation level. NIED states K-NET CSV waveform values are acceleration in gal. NIED FAQ states `1 gal = 1 cm/s^2`. K-NET ASCII documentation defines maximum acceleration from the offset-subtracted acceleration time series.

   Remaining local action: update manuscript methods and data notes. Do not silently change raw HDF5 attrs unless conversion is rerun.

2. **Held-out split evidence**

   Done for 10 s windows. Held-event and balanced held-station splits have zero group overlap.

   Main result: held-event improves all InstanceGM targets and K-NET PGA. Balanced held-station improves all tested InstanceGM targets and K-NET PGA, with strongest gains for InstanceGM PGV and K-NET PGA.

3. **Balanced station split**

   Done. The current split holds out 50 InstanceGM stations and 50 K-NET stations, then samples 1,000 test records while preserving station coverage.

   Distribution audit is done. InstanceGM station-held testing is shifted toward farther, weaker records; K-NET train/test coverage is close for distance and PGA. Remaining action: describe split provenance and distribution shift directly.

4. **Ground-motion reference**

   Done at first-pass level with OpenQuake BooreEtAl2014:

   - metadata-only HGB remains the ML baseline;
   - BooreEtAl2014 is bias-corrected on the train set;
   - Rjb, rake, and Vs30 limitations must be explicit.

   Additional K-NET screening is done with Kanno2006, Zhao2006, and SiMidorikawa1999 variants. The best screened Japanese GMM candidate is Kanno2006Shallow with MAE 0.242 on balanced held-station K-NET PGA; the early-waveform model has MAE 0.111. This is a screening reference because Vs30, rupture distance, and tectonic class are approximated.

   ESM regional screening is done with BooreEtAl2014, AkkarEtAl2014, BindiEtAl2014, and CauzziEtAl2015 candidates. On held-station ESM rows, the early P+distance+site model reduces MAE relative to the best screened regional GMM by 34.8%/23.8% for 2 s PGA/PGV, 48.3%/30.2% for 5 s PGA/PGV, and 43.1%/30.4% for 10 s PGA/PGV.

5. **Uncertainty and tail risk**

   Done with split-conformal intervals on balanced held-station features.

   Remaining action: describe under-coverage for some InstanceGM targets as a real station-shift limitation.

6. **AQ2009GM full-manifest chunk-streaming supplement**

   Done as a supplementary SeisBench ground-motion check. It streams all 254 chunks in the local AQ2009GM manifest and retains feature tables for 345,226 valid PGA/PGV records from 60,310 events and 66 stations. Metadata provides `trace_pga_cmps2` and `trace_pgv_cmps`. Held-event, held-station, and held-time splits have zero group overlap. Metadata plus early velocity features improve every PGA/PGV row across 1/3/10 s windows, with the weakest reduction still 28.8%.

   Remaining action: describe it as full-manifest streaming validation and state that raw AQ2009GM HDF5 files were not retained.

7. **CWA official PGA/PGV supplement**

   Done for the public 2011 CWA benchmark year. The retained table has 5,882 valid PGA/PGV records from 775 events and 705 stations. Held-event and held-station tests show positive reductions at 2 s and 5 s for both PGA and PGV. Raw CWA metadata, HDF5 and the downloaded tar archive were deleted after feature extraction.

8. **Cross-region transfer boundary**

   Done across InstanceGM, K-NET, and AQ2009GM using early waveform features only. The experiment excludes distance, magnitude, site terms, event id, and station id. Every cross-domain row is worse than target-domain training. Median zero-shot penalties are 1.49x, 1.74x, and 2.84x at 1, 3, and 10 s. Target-train offset calibration reduces the medians to 1.40x, 1.65x, and 2.26x.

9. **PNWAccelerometers robustness**

   Done as a supplementary SeisBench accelerometer check. It uses 5,981 earthquake records, held-event and held-station splits, and 2/5/10 s windows. The local file lacks waveform units, so the target is full-record peak horizontal waveform amplitude. Held-station MAE reductions are 39.2%, 68.0%, and 90.5% for 2, 5, and 10 s.

10. **ESM European strong-motion validation**

   Done as an external strong-motion check from local ASCII zip packages. The compact feature table covers 951 zip files, 134,250 early-window rows, 861 events, 1,568 stations, and 26,850 event-station samples. ESM held-station baselines and four-domain transfer are complete. The P-onset sensitivity audit quantifies Vp dependence, and the waveform-onset spot audit samples 200 event-station records. In 86 high-confidence onset-proxy detections, median absolute offset from the theoretical 6 km/s onset is 1.223 s and q95 is 3.960 s.

   The ESM regional GMM screening is now complete and should be used as the stronger classical-reference layer in the manuscript. It remains a screening comparison because rake and distance geometry are approximated.

11. **Figure polish**

   Done for the current evidence package. Main figures now cover:

   - dataset/task matrix;
   - early-window 1/3/10 s performance;
   - held-event/held-station performance;
   - OpenQuake reference and split-conformal uncertainty;
   - residual diagnostics and waveform audit cases;
   - phase-label transfer audit.

12. **Evidence verification**

   Done. `outputs/nc_evidence_verification_report.md` verifies generated artifacts, figure files, key CSV row counts, held-out group overlap, OpenQuake comparison direction, conformal probability bounds, and document references.

## Claims To Use

- Early post-P waveform information improves strong-motion inference across independent datasets, AQ2009GM full-manifest chunk-streaming and a CWA official PGA/PGV one-year check.
- The gain appears at 1 s and increases for several targets at 3 s and 10 s.
- Held-event results rule out ordinary random-split leakage as the explanation.
- Held-station results show useful but target-dependent transfer.
- Cross-region early-waveform transfer gives an empirical boundary on direct regional portability.
- Residual tails separate into path-attenuation, strong-motion-tail, and early-amplitude boundaries.

## Claims To Avoid

- Earthquake prediction.
- Operational EEW readiness.
- Foundation model superiority.
- Physical causality from residual correlations.
- General ground-motion generation.
- Local retention of the full raw AQ2009GM archive.

## Next Action

Tighten manuscript prose and Methods around the verified evidence package. More local experiments help only if they add manual P-pick evidence, a fully specified regional GMM comparison, or broader multi-region strong-motion validation.
