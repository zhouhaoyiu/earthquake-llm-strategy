# NC boundary sensitivity checks

Feature set: early log-waveform features only. Models exclude distance, site terms, event id, and station id.

## Conformal transfer boundary

| Window | Mode | Median coverage90 | Median width |
|---:|---|---:|---:|
| 2s | target_domain | 0.895 | 1.230 |
| 2s | target_offset_conformal | 0.905 | 2.177 |
| 2s | zero_shot_source_conformal | 0.468 | 1.228 |
| 5s | target_domain | 0.895 | 0.828 |
| 5s | target_offset_conformal | 0.903 | 2.177 |
| 5s | zero_shot_source_conformal | 0.298 | 0.826 |

## Strong-motion tail underprediction

| Window | Mode | Tail | Median factor-2 underprediction rate | Median q95 underprediction |
|---:|---|---:|---:|---:|
| 2s | target_domain | top 10% | 0.475 | 1.277 |
| 2s | target_domain | top 5% | 0.520 | 1.479 |
| 2s | target_offset_conformal | top 10% | 1.000 | 1.809 |
| 2s | target_offset_conformal | top 5% | 1.000 | 1.980 |
| 2s | zero_shot_source_conformal | top 10% | 0.282 | 0.841 |
| 2s | zero_shot_source_conformal | top 5% | 0.563 | 1.133 |
| 5s | target_domain | top 10% | 0.270 | 0.678 |
| 5s | target_domain | top 5% | 0.320 | 0.715 |
| 5s | target_offset_conformal | top 10% | 1.000 | 1.734 |
| 5s | target_offset_conformal | top 5% | 1.000 | 1.907 |
| 5s | zero_shot_source_conformal | top 10% | 0.250 | 0.753 |
| 5s | zero_shot_source_conformal | top 5% | 0.442 | 1.017 |

## Three-seed transfer robustness

| Window | Target | Mode | Median ratio range |
|---:|---|---|---:|
| 2s | PGA | target_offset_conformal | 1.54-1.58 |
| 2s | PGA | zero_shot_source_conformal | 2.93-3.24 |
| 2s | PGV | target_offset_conformal | 1.40-1.42 |
| 2s | PGV | zero_shot_source_conformal | 2.28-2.95 |
| 5s | PGA | target_offset_conformal | 1.81-1.85 |
| 5s | PGA | zero_shot_source_conformal | 4.30-4.71 |
| 5s | PGV | target_offset_conformal | 1.87-1.98 |
| 5s | PGV | zero_shot_source_conformal | 2.92-3.34 |

Files:
- `work/nc_boundary_sensitivity/conformal_boundary.csv`
- `work/nc_boundary_sensitivity/tail_underprediction.csv`
- `work/nc_boundary_sensitivity/seed_robustness.csv`
