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
| PGA | esm | source_only | raw_waveform | knet | 1.063 | -2.424 | 5.10 |
| PGA | esm | target_offset_calibrated | raw_waveform | instancegm | 0.407 | 0.361 | 1.95 |
| PGA | instancegm | source_only | raw_waveform | esm | 0.989 | -1.390 | 2.42 |
| PGA | instancegm | target_offset_calibrated | log_waveform | esm | 0.653 | -0.022 | 1.62 |
| PGA | knet | source_only | raw_waveform | instancegm | 0.408 | -0.236 | 2.17 |
| PGA | knet | target_offset_calibrated | log_waveform | esm | 0.343 | 0.040 | 1.83 |
| PGV | esm | source_only | raw_waveform | instancegm | 1.223 | -2.811 | 4.11 |
| PGV | esm | target_offset_calibrated | log_waveform | instancegm | 0.411 | 0.334 | 1.38 |
| PGV | instancegm | source_only | raw_waveform | esm | 0.651 | -0.391 | 2.34 |
| PGV | instancegm | target_offset_calibrated | raw_waveform | esm | 0.562 | 0.093 | 2.04 |

Boundary interpretation:
- Zero-shot transfer median MAE ratio vs target-domain training: 3.81.
- Target-train offset calibration median MAE ratio vs target-domain training: 1.84.
- Treat large cross-domain penalties as evidence for a predictability boundary and unit/measurement harmonization need, not as a failed main result.

Files:
- `work/cross_region_waveform_transfer_esm_5s/cross_region_waveform_transfer_metrics.csv`
- `work/cross_region_waveform_transfer_esm_5s/cross_region_waveform_transfer_boundary.csv`
- `outputs/figures/ground_motion_audit/cross_region_waveform_transfer_esm_5s_boundary.png`
