# Cross-region early-waveform transfer

This check uses compact public-dataset feature tables only. Models use early waveform features, not source distance, site terms, event id, or station id.

Splits:

| Dataset | Split | Train rows | Test rows | Train groups | Test groups | Group overlap |
|---|---|---:|---:|---:|---:|---:|
| instancegm | balanced_held_station | 5000 | 1000 | 411 | 50 | 0 |
| knet | balanced_held_station | 5000 | 1000 | 726 | 50 | 0 |
| aq2009gm | held_event | 30000 | 10000 | 21415 | 1774 | 0 |
| esm | held_station | 20000 | 3021 | 1321 | 200 | 0 |

Best cross-region rows by target/test domain:

| Target | Test domain | Calibration | Feature set | Source domain | MAE | R2 | MAE ratio vs within target |
|---|---|---|---|---|---:|---:|---:|
| PGA | aq2009gm | source_only | raw_waveform | instancegm | 0.273 | 0.677 | 1.64 |
| PGA | aq2009gm | target_offset_calibrated | raw_waveform | instancegm | 0.237 | 0.754 | 1.43 |
| PGA | esm | source_only | raw_waveform | knet | 1.032 | -1.916 | 3.27 |
| PGA | esm | target_offset_calibrated | raw_waveform | instancegm | 0.490 | 0.171 | 1.53 |
| PGA | instancegm | source_only | raw_waveform | aq2009gm | 0.639 | -0.349 | 1.42 |
| PGA | instancegm | target_offset_calibrated | log_waveform | aq2009gm | 0.532 | 0.016 | 1.19 |
| PGA | knet | source_only | raw_waveform | aq2009gm | 0.364 | -0.261 | 1.62 |
| PGA | knet | target_offset_calibrated | raw_waveform | esm | 0.335 | 0.074 | 1.50 |
| PGV | aq2009gm | source_only | raw_waveform | instancegm | 0.204 | 0.808 | 1.37 |
| PGV | aq2009gm | target_offset_calibrated | raw_waveform | instancegm | 0.204 | 0.809 | 1.38 |
| PGV | esm | source_only | raw_waveform | aq2009gm | 0.900 | -1.465 | 2.37 |
| PGV | esm | target_offset_calibrated | raw_waveform | instancegm | 0.495 | 0.109 | 1.30 |
| PGV | instancegm | source_only | raw_waveform | aq2009gm | 0.395 | 0.393 | 1.26 |
| PGV | instancegm | target_offset_calibrated | raw_waveform | aq2009gm | 0.374 | 0.467 | 1.20 |

Boundary interpretation:
- Zero-shot transfer median MAE ratio vs target-domain training: 2.65.
- Target-train offset calibration median MAE ratio vs target-domain training: 1.55.
- Treat large cross-domain penalties as evidence for a predictability boundary and unit/measurement harmonization need, not as a failed main result.

Files:
- `work/cross_region_waveform_transfer_aq_esm_2s/cross_region_waveform_transfer_metrics.csv`
- `work/cross_region_waveform_transfer_aq_esm_2s/cross_region_waveform_transfer_boundary.csv`
- `outputs/figures/ground_motion_audit/cross_region_waveform_transfer_aq_esm_2s_boundary.png`
