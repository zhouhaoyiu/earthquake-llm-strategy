# AQ2009GM full-manifest stress tests

- feature rows: 1035678
- unique valid records: 345226
- train/test cap: 30000/10000

| Split | Target | Window | MAE reduction | Combined R2 | Q90 coverage | Q95 coverage |
|---|---|---:|---:|---:|---:|---:|
| far_distance_path | PGA | 1s | 44.2% | 0.803 | 0.730 | 0.824 |
| far_distance_path | PGA | 3s | 51.8% | 0.842 | 0.678 | 0.786 |
| far_distance_path | PGA | 10s | 60.5% | 0.871 | 0.655 | 0.726 |
| far_distance_path | PGV | 1s | 44.0% | 0.796 | 0.695 | 0.798 |
| far_distance_path | PGV | 3s | 54.6% | 0.861 | 0.641 | 0.761 |
| far_distance_path | PGV | 10s | 74.8% | 0.906 | 0.605 | 0.659 |
| high_magnitude_event | PGA | 1s | 46.2% | 0.800 | 0.711 | 0.789 |
| high_magnitude_event | PGA | 3s | 53.2% | 0.842 | 0.652 | 0.750 |
| high_magnitude_event | PGA | 10s | 63.2% | 0.883 | 0.637 | 0.718 |
| high_magnitude_event | PGV | 1s | 45.4% | 0.751 | 0.641 | 0.722 |
| high_magnitude_event | PGV | 3s | 54.2% | 0.804 | 0.604 | 0.689 |
| high_magnitude_event | PGV | 10s | 74.0% | 0.882 | 0.489 | 0.590 |
| high_target_tail | PGA | 1s | 19.1% | -2.423 | 0.219 | 0.344 |
| high_target_tail | PGA | 3s | 25.4% | -2.104 | 0.190 | 0.286 |
| high_target_tail | PGA | 10s | 25.7% | -2.105 | 0.057 | 0.121 |
| high_target_tail | PGV | 1s | 19.0% | -2.121 | 0.176 | 0.290 |
| high_target_tail | PGV | 3s | 28.6% | -1.673 | 0.191 | 0.276 |
| high_target_tail | PGV | 10s | 30.1% | -1.647 | 0.000 | 0.004 |

Files:
- `work/aq2009gm_full_stream_stress_tests/aq2009gm_stream_stress_metrics.csv`
- `work/aq2009gm_full_stream_stress_tests/aq2009gm_stream_stress_uncertainty.csv`
- `work/aq2009gm_full_stream_stress_tests/aq2009gm_stream_stress_splits.csv`
