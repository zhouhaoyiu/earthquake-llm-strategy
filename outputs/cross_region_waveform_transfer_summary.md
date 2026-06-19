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
| PGA | aq2009gm | source_only | log_waveform | instancegm | 0.167 | 0.853 | 1.71 |
| PGA | aq2009gm | target_offset_calibrated | log_waveform | instancegm | 0.164 | 0.860 | 1.68 |
| PGA | instancegm | source_only | raw_waveform | aq2009gm | 0.479 | 0.094 | 1.35 |
| PGA | instancegm | target_offset_calibrated | log_waveform | aq2009gm | 0.463 | 0.180 | 1.32 |
| PGA | knet | source_only | log_waveform | aq2009gm | 0.356 | -0.195 | 2.60 |
| PGA | knet | target_offset_calibrated | log_waveform | instancegm | 0.346 | -0.002 | 2.53 |
| PGV | aq2009gm | source_only | raw_waveform | instancegm | 0.109 | 0.920 | 4.98 |
| PGV | aq2009gm | target_offset_calibrated | log_waveform | instancegm | 0.102 | 0.920 | 4.66 |
| PGV | instancegm | source_only | log_waveform | aq2009gm | 0.315 | 0.549 | 1.32 |
| PGV | instancegm | target_offset_calibrated | log_waveform | aq2009gm | 0.315 | 0.549 | 1.32 |

Boundary interpretation:
- Zero-shot transfer median MAE ratio vs target-domain training: 2.84.
- Target-train offset calibration median MAE ratio vs target-domain training: 2.26.
- Treat large cross-domain penalties as evidence for a predictability boundary and unit/measurement harmonization need, not as a failed main result.

Files:
- `work/cross_region_waveform_transfer/cross_region_waveform_transfer_metrics.csv`
- `work/cross_region_waveform_transfer/cross_region_waveform_transfer_boundary.csv`
- `outputs/figures/ground_motion_audit/cross_region_waveform_transfer_boundary.png`
