# K-NET Pre-Peak Subset Audit

Date: 2026-06-18

This audit evaluates K-NET PGA records where the early-window horizontal peak is below a fraction of the observed full-record PGA target. It uses existing residual prediction tables.

## Main threshold: early/target ratio < 0.8

- 1 s: 302 records; metadata MAE 0.238; combined MAE 0.205; reduction 13.8%.
- 3 s: 255 records; metadata MAE 0.239; combined MAE 0.197; reduction 17.9%.
- 10 s: 53 records; metadata MAE 0.275; combined MAE 0.210; reduction 23.8%.

## Interpretation

The 1 s and 3 s pre-peak subsets support a lead-time-sensitive K-NET signal: early waveform features still reduce error when the early horizontal peak remains below 80% of the observed PGA. The 10 s pre-peak subset is small, so it is an audit result rather than a primary performance claim.

CSV: `outputs/knet_prepeak_subset_audit.csv`
