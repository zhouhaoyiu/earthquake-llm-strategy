# Cross-region early-waveform transfer

This check uses compact public-dataset feature tables only. Models use early waveform features, not source distance, site terms, event id, or station id.

Splits:

| Dataset | Split | Train rows | Test rows | Train groups | Test groups | Group overlap |
|---|---|---:|---:|---:|---:|---:|
| instancegm | balanced_held_station | 5000 | 1000 | 411 | 50 | 0 |
| knet | balanced_held_station | 5000 | 1000 | 726 | 50 | 0 |
| aq2009gm | held_event | 30000 | 10000 | 21415 | 1774 | 0 |

Best cross-region rows by target/test domain:

| Target | Test domain | Calibration | Feature set | Source domain | MAE | R2 | MAE ratio vs within target |
|---|---|---|---|---|---:|---:|---:|
| PGA | aq2009gm | source_only | log_waveform | instancegm | 0.243 | 0.748 | 1.67 |
| PGA | aq2009gm | target_offset_calibrated | log_waveform | instancegm | 0.237 | 0.771 | 1.64 |
| PGA | instancegm | source_only | raw_waveform | aq2009gm | 0.603 | -0.180 | 1.38 |
| PGA | instancegm | target_offset_calibrated | log_waveform | aq2009gm | 0.508 | 0.128 | 1.17 |
| PGA | knet | source_only | raw_waveform | aq2009gm | 0.354 | -0.175 | 1.69 |
| PGA | knet | target_offset_calibrated | raw_waveform | instancegm | 0.346 | -0.001 | 1.66 |
| PGV | aq2009gm | source_only | log_waveform | instancegm | 0.223 | 0.806 | 1.79 |
| PGV | aq2009gm | target_offset_calibrated | log_waveform | instancegm | 0.214 | 0.815 | 1.73 |
| PGV | instancegm | source_only | log_waveform | aq2009gm | 0.356 | 0.502 | 1.18 |
| PGV | instancegm | target_offset_calibrated | log_waveform | aq2009gm | 0.341 | 0.555 | 1.14 |

Boundary interpretation:
- Zero-shot transfer median MAE ratio vs target-domain training: 1.74.
- Target-train offset calibration median MAE ratio vs target-domain training: 1.65.
- Treat large cross-domain penalties as evidence for a predictability boundary and unit/measurement harmonization need, not as a failed main result.

Files:
- `work/cross_region_waveform_transfer_3s/cross_region_waveform_transfer_metrics.csv`
- `work/cross_region_waveform_transfer_3s/cross_region_waveform_transfer_boundary.csv`
- `outputs/figures/ground_motion_audit/cross_region_waveform_transfer_3s_boundary.png`
