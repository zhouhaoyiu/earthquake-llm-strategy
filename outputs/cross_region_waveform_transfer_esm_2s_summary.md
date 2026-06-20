# Cross-region early-waveform transfer

This check uses compact public-dataset feature tables only. Models use early waveform features, not source distance, site terms, event id, or station id.

Splits:

| Dataset | Split | Train rows | Test rows | Train groups | Test groups | Group overlap |
|---|---|---:|---:|---:|---:|---:|
| instancegm | balanced_held_station | 5000 | 1000 | 411 | 50 | 0 |
| knet | balanced_held_station | 5000 | 1000 | 726 | 50 | 0 |
| esm | held_station | 20000 | 3021 | 1321 | 200 | 0 |

Best cross-region rows by target/test domain:

| Target | Test domain | Calibration | Feature set | Source domain | MAE | R2 | MAE ratio vs within target |
|---|---|---|---|---|---:|---:|---:|
| PGA | esm | source_only | raw_waveform | knet | 1.032 | -1.916 | 3.27 |
| PGA | esm | target_offset_calibrated | raw_waveform | instancegm | 0.490 | 0.171 | 1.53 |
| PGA | instancegm | source_only | raw_waveform | esm | 0.658 | -0.096 | 1.46 |
| PGA | instancegm | target_offset_calibrated | log_waveform | knet | 0.698 | -0.168 | 1.56 |
| PGA | knet | source_only | raw_waveform | instancegm | 0.385 | -0.119 | 1.71 |
| PGA | knet | target_offset_calibrated | log_waveform | esm | 0.335 | 0.074 | 1.50 |
| PGV | esm | source_only | raw_waveform | instancegm | 1.089 | -2.267 | 2.87 |
| PGV | esm | target_offset_calibrated | raw_waveform | instancegm | 0.495 | 0.109 | 1.30 |
| PGV | instancegm | source_only | log_waveform | esm | 0.792 | -0.602 | 2.53 |
| PGV | instancegm | target_offset_calibrated | raw_waveform | esm | 0.609 | -0.125 | 1.97 |

Boundary interpretation:
- Zero-shot transfer median MAE ratio vs target-domain training: 2.83.
- Target-train offset calibration median MAE ratio vs target-domain training: 1.55.
- Treat large cross-domain penalties as evidence for a predictability boundary and unit/measurement harmonization need, not as a failed main result.

Files:
- `work/cross_region_waveform_transfer_esm_2s/cross_region_waveform_transfer_metrics.csv`
- `work/cross_region_waveform_transfer_esm_2s/cross_region_waveform_transfer_boundary.csv`
- `outputs/figures/ground_motion_audit/cross_region_waveform_transfer_esm_2s_boundary.png`
