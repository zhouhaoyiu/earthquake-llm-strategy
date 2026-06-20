# NC Core Predictability-Boundary Synthesis

This file is generated from existing validated outputs. It does not add a new model run.

| Window | Main held-station gain % | AQ station gain % | ESM station gain vs median % | Zero-shot transfer ratio | Offset transfer ratio | Source conformal coverage | Target-offset coverage | Target-domain top5 under-rate |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1s | 20.2 | 32.4 | 45.9 | 2.25 | 1.40 | NA | NA | NA |
| 2s | 21.2 | 38.0 | 35.5 | 2.65 | 1.55 | 0.468 | 0.905 | 0.520 |
| 3s | 22.9 | 47.2 | 49.6 | 2.98 | 1.67 | NA | NA | NA |
| 5s | 24.8 | 63.8 | 47.4 | 3.38 | 1.85 | 0.298 | 0.903 | 0.320 |
| 10s | 31.6 | 77.5 | 66.2 | 4.27 | 2.46 | NA | NA | NA |

Plain-language read:
- Early-window information gain is consistently positive under held-station or held-station-like checks.
- Cross-region transfer penalties grow from 1 s to 10 s, and offset calibration does not remove them.
- Source-domain conformal intervals under-cover target domains at 2 s and 5 s.
- The strongest-shaking tail improves from 2 s to 5 s, but the top-tail underprediction boundary remains visible.

Files:
- `outputs/nc_core_predictability_boundary_table.csv`
- `outputs/figures/nc_core_predictability_boundary.png`
