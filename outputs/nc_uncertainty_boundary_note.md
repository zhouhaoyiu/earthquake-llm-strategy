# Uncertainty Boundary Note

Split conformal prediction gives finite-sample marginal coverage when calibration and test residuals are exchangeable. This assumption is credible inside a carefully defined split, weaker under held-station shift, and intentionally broken in cross-region transfer.

The current evidence uses this distinction directly:

| Setting | Calibration residuals | Test residuals | Interpretation |
|---|---|---|---|
| Target-domain held-station | target training split | target held-station split | station-shift calibration check |
| Source conformal transfer | source domain | target domain | exchangeability stress test |
| Target-offset conformal | target training split after scalar offset | target test split | minimal target-domain recalibration |

Observed boundary:

- Target-domain conformal coverage stays near nominal in the 2/5 s sensitivity check: about 0.895.
- Source-domain conformal intervals under-cover target domains: 0.468 at 2 s and 0.298 at 5 s.
- Target-offset conformal calibration restores coverage to about 0.90 with wider intervals.

Manuscript wording:

Early waveform features improve point prediction, but uncertainty intervals are transportable only when the calibration residual distribution matches the target residual distribution. Cross-region transfer breaks that condition, and the observed under-coverage quantifies the boundary.
