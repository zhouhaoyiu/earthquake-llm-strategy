# Nature Communications Execution Plan

Date: 2026-06-19

## Target

Primary target: **Nature Communications**

Working title:

**Cross-regional predictability limits of strong shaking from the first seconds of P waves**

## Central Claim

Public strong-motion archives can be organized into a reproducible early-window benchmark that measures how much final strong shaking is predictable from the first seconds after P arrival. Early waveform features add information beyond source-path-site metadata, but the gain, tail risk, and calibration limits vary by target, split, and region.

This is a benchmark and uncertainty paper. It is not a new-model paper, not an earthquake-prediction paper, and not an operational early-warning claim.

## Current Evidence

Verified package:

- Unified manifest: 2,460,425 records across STEAD, InstanceGM, Iquique, and K-NET.
- K-NET conversion: 22,119 complete ZNE records; gal to cm/s2 unit provenance verified.
- Main strong-motion evidence: InstanceGM PGA, PGV, SA03, SA10, SA30; K-NET PGA.
- Early windows: 1 s, 3 s, and 10 s after catalog P arrival.
- Split tests: random, held-event, balanced held-station with zero group overlap.
- Classical references: attenuation-shaped ridge, bias-corrected BooreEtAl2014, and K-NET Japanese GMM screening.
- Uncertainty: split-conformal intervals on balanced held-station features.
- Predictability boundary table: 10 s random performance, held-event and held-station residual floors, robust held-out gains, and conformal coverage gaps.
- Audits: K-NET pre-peak subset, residual tails, phase-label transfer, AQ2009GM 096-100 supplement, PNW accelerometer peak-amplitude supplement.

Verifier:

`outputs/nc_evidence_verification_report.md`

## Main Storyline

1. Build a public early-window strong-motion benchmark with explicit data, split, unit, and target provenance.
2. Quantify lead-time-dependent information gain from 1 s, 3 s, and 10 s post-P windows.
3. Test whether the gain survives held-event and balanced held-station evaluation.
4. Compare against metadata baselines and classical ground-motion references.
5. Report uncertainty calibration and tail-risk limits, not only point-prediction error.
6. Audit residuals and phase labels to expose where the benchmark still fails.

## Core Quantities

### Predictability gain

`G(t) = R(metadata) - R(metadata + early waveform at t)`

Report for MAE, q95 absolute residual, and R2 where useful.

### Relative gain

`G_rel(t) = (R(metadata) - R(combined_t)) / R(metadata)`

Use this for Figure 2 and table summaries.

### Split degradation

`D(split) = R(combined, split) - R(combined, random)`

Use random only as a reference. Lead with held-event and balanced held-station.

### Calibration gap

`C_gap = observed_coverage - nominal_coverage`

Use split-conformal intervals. Report under-coverage directly.

### Empirical boundary

`B = {held-station MAE, q90/q95 residual, C_gap}`

Use this as a measured boundary tied to the current data, features, and splits.

## Minimum NC Evidence

Required before submission:

- Figure 1: benchmark matrix and data provenance.
- Figure 2: information-gain curves across 1/3/10 s.
- Figure 3: held-event and balanced held-station generalization with split audit.
- Figure 4: classical references plus conformal uncertainty.
- Figure 5: residual and waveform audit.
- Figure 6: phase-label audit supporting P alignment.
- Predictability boundary table.
- Methods provenance table.
- Reviewer risk matrix.
- Evidence verifier with all checks passing.

Already present:

- `outputs/nc_minimum_submission_package.md`
- `outputs/manuscript_scaffold_cross_dataset_early_window_residual_audit.md`
- `outputs/nc_reviewer_risk_matrix.md`
- `outputs/methods_provenance_table.md`
- `outputs/predictability_boundary_summary.md`
- `outputs/predictability_boundary_table.csv`
- `outputs/nc_evidence_verification_report.md`

## Immediate Work Queue

1. Rename and rewrite the manuscript scaffold around predictability limits, not residual auditing alone.
2. Rebuild the six main figures in one Nature-style visual system.
3. Turn the current evidence packet into a full manuscript draft.
4. Decide whether to expand AQ2009GM beyond chunks 096-100; keep the current five-chunk result supplementary.
5. Add a short Data and Code Availability section with exact scripts and split files.
6. Re-run the verifier after every figure/table regeneration.

## Claim Boundaries

Use:

- Early post-P waveform windows contain strong-motion information beyond source-path-site metadata.
- This information persists under held-event and balanced held-station tests.
- Public archives can support a reproducible benchmark for early strong-motion predictability.
- Tail risk and conformal coverage show remaining limits under station shift.

Avoid:

- No operational warning readiness.
- No prospective real-time performance claim.
- No earthquake prediction claim.
- No foundation-model or learned-representation superiority claim.
- No full superiority over a fully specified regional GMM.
- No physical-causality claim from residual correlations alone.

## Submission Route

Primary: Nature Communications.

Fallbacks:

- Science Advances, only if the paper is framed as a broader predictability-limit result for rapid hazard science.
- JGR: Solid Earth, BSSA, or GJI if reviewers want a more specialist seismology venue.
- Earthquake Spectra if the final paper becomes more engineering-risk centered.
