# NC High-Acceptance Plan

Date: 2026-06-18

## Position

Aim for Nature Communications with the narrowed story:

**Cross-regional predictability limits of strong shaking from the first seconds of P waves.**

Lead with the public benchmark, held-out early-window gains, uncertainty calibration, and cross-region transfer boundary.

## Probability

Current verified figure-ready package plus AQ2009GM full-manifest chunk-streaming and cross-region transfer boundary: **50-59%**.

With final manuscript prose, Methods provenance, and careful caveats: **50-59%**.

With a fully specified regional GMM comparison, broader multi-region strong-motion validation, or a stronger physical residual mechanism: **52-59%**.

Treat **60%** as unproven. AQ2009GM full-manifest chunk-streaming supports early-window information in another SeisBench ground-motion dataset with official PGA/PGV metadata targets. Cross-region transfer across InstanceGM, K-NET, and AQ2009GM adds a measurable boundary: zero-shot median MAE penalty rises from 1.49x at 1 s to 2.84x at 10 s. Publication-grade high-confidence validation still needs broader multi-region coverage, a fully specified regional GMM layer, or a stronger physical residual mechanism.

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

5. **Uncertainty and tail risk**

   Done with split-conformal intervals on balanced held-station features.

   Remaining action: describe under-coverage for some InstanceGM targets as a real station-shift limitation.

6. **AQ2009GM full-manifest chunk-streaming supplement**

   Done as a supplementary SeisBench ground-motion check. It streams all 254 chunks in the local AQ2009GM manifest and retains feature tables for 345,226 valid PGA/PGV records from 60,310 events and 66 stations. Metadata provides `trace_pga_cmps2` and `trace_pgv_cmps`. Held-event, held-station, and held-time splits have zero group overlap. Metadata plus early velocity features improve every PGA/PGV row across 1/3/10 s windows, with the weakest reduction still 28.8%.

   Remaining action: describe it as full-manifest streaming validation and state that raw AQ2009GM HDF5 files were not retained.

7. **Cross-region transfer boundary**

   Done across InstanceGM, K-NET, and AQ2009GM using early waveform features only. The experiment excludes distance, magnitude, site terms, event id, and station id. Every cross-domain row is worse than target-domain training. Median zero-shot penalties are 1.49x, 1.74x, and 2.84x at 1, 3, and 10 s. Target-train offset calibration reduces the medians to 1.40x, 1.65x, and 2.26x.

8. **PNWAccelerometers robustness**

   Done as a supplementary SeisBench accelerometer check. It uses 5,981 earthquake records, held-event and held-station splits, and 1/3/10 s windows. The local file lacks waveform units, so the target is full-record peak horizontal waveform amplitude.

9. **Figure polish**

   Done for the current evidence package. Main figures now cover:

   - dataset/task matrix;
   - early-window 1/3/10 s performance;
   - held-event/held-station performance;
   - OpenQuake reference and split-conformal uncertainty;
   - residual diagnostics and waveform audit cases;
   - phase-label transfer audit.

10. **Evidence verification**

   Done. `outputs/nc_evidence_verification_report.md` verifies generated artifacts, figure files, key CSV row counts, held-out group overlap, OpenQuake comparison direction, conformal probability bounds, and document references.

## Claims To Use

- Early post-P waveform information improves strong-motion inference across independent datasets and an AQ2009GM full-manifest chunk-streaming supplementary check.
- The gain appears at 1 s and increases for several targets at 3 s and 10 s.
- Held-event results rule out ordinary random-split leakage as the explanation.
- Held-station results show useful but target-dependent transfer.
- Cross-region early-waveform transfer gives an empirical boundary on direct regional portability.
- Residual tails identify audit targets consistent with path, site, label, or rare waveform-target effects.

## Claims To Avoid

- Earthquake prediction.
- Operational EEW readiness.
- Foundation model superiority.
- Physical causality from residual correlations.
- General ground-motion generation.
- Local retention of the full raw AQ2009GM archive.

## Next Action

Tighten manuscript prose and Methods around the verified evidence package. More local experiments help only if they add a fully specified regional GMM comparison, add broader multi-region strong-motion validation, or strengthen the residual mechanism.
