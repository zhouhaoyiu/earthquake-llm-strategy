# NC Next Experiment Decision

Decision date: 2026-06-20

## Decision

The small ESM waveform-level onset-proxy spot audit and the ESM regional GMM screening are now complete. Defer a fully specified regional GMPE/GMM comparison until rupture distance, site terms, and tectonic or focal-mechanism metadata are available.

## Rationale

The current package already has held-out gains, AQ2009GM full-manifest streaming, ESM held-out validation, ESM regional GMM screening, four-domain transfer, conformal transfer, tail-risk checks, and residual-mechanism classes. The weakest active claim boundary was ESM timing: local ESM headers lack explicit P picks, and the Vp sensitivity audit shows 2 s-scale theoretical-onset shifts. The completed waveform-level spot audit directly tests that boundary with limited new data handling.

The spot audit sampled 200 ESM event-station records across distance and PGA quantiles. It detected automated waveform-envelope onset proxies in 105 records, including 86 high-confidence proxies. In the high-confidence subset, the median absolute offset between the waveform proxy and the theoretical 6 km/s onset is 1.223 s, q90 is 3.338 s, q95 is 3.960 s, and 98.8% are within 5 s. This supports using ESM as an external transfer-domain check with explicit onset-proxy wording. It still does not support catalog/manual P-pick lead-time claims.

The ESM regional screening is the current honest GMM layer. It evaluates BooreEtAl2014, AkkarEtAl2014, BindiEtAl2014 and CauzziEtAl2015 candidates on the same held-station rows used by the early-window model, after dropping records without source magnitude and applying train-set median bias correction. The early P+distance+site model reduces MAE relative to the best screened regional GMM by 23.8-48.3% across 2 s and 5 s PGA/PGV tests, and by 30.4-43.1% at 10 s.

A fully specified regional GMPE/GMM comparison is still deferred. The readiness audit shows that K-NET lacks Vs30, rupture distance, and focal-mechanism fields in the approved local package. InstanceGM has complete Vs30 in the balanced held-station split but sparse focal-mechanism coverage. Running a nominal full regional GMM now would look more complete than the metadata support allows.

## Completed ESM Audit

- Script: `work/scripts/audit_esm_waveform_p_pick_spotcheck.py`
- Regional GMM script: `work/scripts/run_esm_regional_gmm_screening.py`
- Table: `outputs/esm_waveform_p_pick_spotcheck.csv`
- Regional GMM table: `outputs/esm_regional_gmm_screening.csv`
- Summary: `outputs/esm_waveform_p_pick_spotcheck.md`
- Regional GMM summary: `outputs/esm_regional_gmm_screening_summary.md`
- Figure: `outputs/figures/ground_motion_audit/esm_waveform_p_pick_spotcheck.png`
- Regional GMM figure: `outputs/figures/ground_motion_audit/esm_regional_gmm_screening.png`

## Deferred Work

Full regional GMPE/GMM comparison waits for curated rupture distance, Vs30 or site class, and tectonic or focal-mechanism metadata.
