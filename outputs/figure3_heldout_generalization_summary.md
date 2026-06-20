# Figure 3 Held-Out Generalization

Date: 2026-06-18

Figure 3 combines the 10 s held-event results, balanced held-station results, and station-split distribution audit. It uses the existing experiment outputs only; no model was rerun.

- held-event InstanceGM PGA: 0.312 -> 0.191 (38.8% reduction), R2=0.875.
- balanced held-station InstanceGM PGA: 0.392 -> 0.253 (35.5% reduction), R2=0.799.
- held-event InstanceGM PGV: 0.313 -> 0.155 (50.4% reduction), R2=0.895.
- balanced held-station InstanceGM PGV: 0.372 -> 0.176 (52.6% reduction), R2=0.858.
- held-event K-NET PGA: 0.238 -> 0.108 (54.5% reduction), R2=0.869.
- balanced held-station K-NET PGA: 0.222 -> 0.111 (49.9% reduction), R2=0.875.

Distribution audit:

- InstanceGM station-held records are farther from the source: train median 44.27 km, test median 70.61 km, overlap 0.76.
- InstanceGM station-held PGA targets are weaker: train median log10 PGA -1.68, test median -2.11, overlap 0.78.
- K-NET station-held distance and PGA distributions have high overlap, above 0.91 in the current audit.

Interpretation:

The held-out evidence supports the narrow claim that early post-P waveform features add strong-motion information beyond metadata under event and station separation. The split audit shows that the station-held test retains nontrivial distribution shift.

Figure: `outputs/figures/figure3_heldout_generalization.png`
CSV: `outputs/figure3_heldout_generalization.csv`
