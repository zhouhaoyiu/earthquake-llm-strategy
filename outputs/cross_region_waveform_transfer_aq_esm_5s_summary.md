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
| PGA | aq2009gm | source_only | raw_waveform | instancegm | 0.189 | 0.827 | 1.57 |
| PGA | aq2009gm | target_offset_calibrated | raw_waveform | instancegm | 0.188 | 0.825 | 1.56 |
| PGA | esm | source_only | raw_waveform | knet | 1.063 | -2.424 | 5.10 |
| PGA | esm | target_offset_calibrated | raw_waveform | instancegm | 0.407 | 0.361 | 1.95 |
| PGA | instancegm | source_only | log_waveform | aq2009gm | 0.534 | 0.012 | 1.31 |
| PGA | instancegm | target_offset_calibrated | raw_waveform | aq2009gm | 0.488 | 0.179 | 1.21 |
| PGA | knet | source_only | log_waveform | aq2009gm | 0.356 | -0.194 | 1.89 |
| PGA | knet | target_offset_calibrated | log_waveform | esm | 0.343 | 0.040 | 1.83 |
| PGV | aq2009gm | source_only | log_waveform | instancegm | 0.182 | 0.868 | 2.63 |
| PGV | aq2009gm | target_offset_calibrated | log_waveform | instancegm | 0.147 | 0.881 | 2.14 |
| PGV | esm | source_only | raw_waveform | aq2009gm | 0.971 | -1.797 | 3.26 |
| PGV | esm | target_offset_calibrated | log_waveform | instancegm | 0.411 | 0.334 | 1.38 |
| PGV | instancegm | source_only | log_waveform | aq2009gm | 0.320 | 0.574 | 1.15 |
| PGV | instancegm | target_offset_calibrated | log_waveform | aq2009gm | 0.320 | 0.585 | 1.16 |

Boundary interpretation:
- Zero-shot transfer median MAE ratio vs target-domain training: 3.38.
- Target-train offset calibration median MAE ratio vs target-domain training: 1.85.
- Treat large cross-domain penalties as evidence for a predictability boundary and unit/measurement harmonization need, not as a failed main result.

Files:
- `work/cross_region_waveform_transfer_aq_esm_5s/cross_region_waveform_transfer_metrics.csv`
- `work/cross_region_waveform_transfer_aq_esm_5s/cross_region_waveform_transfer_boundary.csv`
- `outputs/figures/ground_motion_audit/cross_region_waveform_transfer_aq_esm_5s_boundary.png`
