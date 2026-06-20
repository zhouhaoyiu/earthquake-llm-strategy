# NC Next Experiment Decision

Decision date: 2026-06-20

## Decision

Run a small ESM waveform-level P-pick spot audit next. Defer a fully specified regional GMPE/GMM comparison until rupture distance, site terms, and tectonic or focal-mechanism metadata are available.

## Rationale

The current package already has held-out gains, AQ2009GM full-manifest streaming, ESM held-out validation, four-domain transfer, conformal transfer, tail-risk checks, and GMM screening. The weakest active claim boundary is ESM timing: local ESM headers lack explicit P picks, and the Vp sensitivity audit shows 2 s-scale theoretical-onset shifts. A waveform-level P-pick spot audit directly tests that boundary with limited new data handling.

A full regional GMPE/GMM comparison is not the next step. The readiness audit shows that K-NET lacks Vs30, rupture distance, and focal-mechanism fields in the approved local package. InstanceGM has complete Vs30 in the balanced held-station split but sparse focal-mechanism coverage. Running a nominal regional GMM now would look more complete than the metadata support allows.

## Minimal ESM Audit Spec

- Sample 50-100 ESM event-station records across distance and PGA quantiles.
- Run an offline picker or manual-onset proxy on the retained waveform files.
- Compare picked P onset with the current theoretical 6 km/s onset.
- Report median, q90, q95 timing offset and the fraction of 1/2/3/5/10 s windows whose feature validity changes.
- Keep the result as an audit table unless it materially changes transfer conclusions.

## Deferred Work

Full regional GMPE/GMM comparison waits for curated rupture distance, Vs30 or site class, and tectonic or focal-mechanism metadata.
