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
| PGA | aq2009gm | source_only | raw_waveform | instancegm | 0.273 | 0.636 | 1.52 |
| PGA | aq2009gm | target_offset_calibrated | raw_waveform | instancegm | 0.250 | 0.702 | 1.40 |
| PGA | instancegm | source_only | raw_waveform | aq2009gm | 0.649 | -0.420 | 1.41 |
| PGA | instancegm | target_offset_calibrated | log_waveform | aq2009gm | 0.565 | -0.097 | 1.23 |
| PGA | knet | source_only | raw_waveform | instancegm | 0.367 | -0.041 | 1.47 |
| PGA | knet | target_offset_calibrated | raw_waveform | instancegm | 0.346 | -0.001 | 1.40 |
| PGV | aq2009gm | source_only | raw_waveform | instancegm | 0.221 | 0.776 | 1.35 |
| PGV | aq2009gm | target_offset_calibrated | raw_waveform | instancegm | 0.218 | 0.775 | 1.34 |
| PGV | instancegm | source_only | log_waveform | aq2009gm | 0.429 | 0.322 | 1.26 |
| PGV | instancegm | target_offset_calibrated | raw_waveform | aq2009gm | 0.418 | 0.371 | 1.24 |

Boundary interpretation:
- Zero-shot transfer median MAE ratio vs target-domain training: 1.49.
- Target-train offset calibration median MAE ratio vs target-domain training: 1.40.
- Treat large cross-domain penalties as evidence for a predictability boundary and unit/measurement harmonization need, not as a failed main result.

Files:
- `work/cross_region_waveform_transfer_1s/cross_region_waveform_transfer_metrics.csv`
- `work/cross_region_waveform_transfer_1s/cross_region_waveform_transfer_boundary.csv`
- `outputs/figures/ground_motion_audit/cross_region_waveform_transfer_1s_boundary.png`
