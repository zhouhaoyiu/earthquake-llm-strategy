# ESM held-out early-window baseline

This check uses compact features extracted from local ESM ASCII zip packages. P windows use a fixed-velocity theoretical onset.

Splits:

| Holdout | Window | Train rows | Test rows | Train groups | Test groups | Overlap |
|---|---:|---:|---:|---:|---:|---:|
| event | 1s | 20000 | 6000 | 665 | 191 | 0 |
| station | 1s | 20000 | 3151 | 1331 | 200 | 0 |
| event | 2s | 20000 | 6000 | 664 | 192 | 0 |
| station | 2s | 20000 | 3727 | 1334 | 200 | 0 |
| event | 3s | 20000 | 6000 | 670 | 185 | 0 |
| station | 3s | 20000 | 2427 | 1319 | 200 | 0 |
| event | 5s | 20000 | 6000 | 654 | 202 | 0 |
| station | 5s | 20000 | 4240 | 1343 | 200 | 0 |
| event | 10s | 20000 | 6000 | 677 | 178 | 0 |
| station | 10s | 20000 | 3242 | 1340 | 200 | 0 |

Held-station information gain:

| Target | Window | Median MAE | P only MAE | P+distance MAE | P+distance+site MAE | Site gain vs P+distance |
|---|---:|---:|---:|---:|---:|---:|
| PGA | 1s | 0.717 | 0.522 | 0.378 | 0.371 | 1.8% |
| PGA | 2s | 0.455 | 0.300 | 0.279 | 0.275 | 1.4% |
| PGA | 3s | 0.553 | 0.263 | 0.251 | 0.251 | -0.1% |
| PGA | 5s | 0.457 | 0.226 | 0.224 | 0.214 | 4.4% |
| PGA | 10s | 0.616 | 0.207 | 0.221 | 0.197 | 11.0% |
| PGV | 1s | 0.676 | 0.516 | 0.371 | 0.382 | -3.1% |
| PGV | 2s | 0.471 | 0.368 | 0.330 | 0.323 | 2.1% |
| PGV | 3s | 0.556 | 0.338 | 0.308 | 0.308 | 0.2% |
| PGV | 5s | 0.483 | 0.311 | 0.290 | 0.282 | 2.8% |
| PGV | 10s | 0.600 | 0.253 | 0.227 | 0.214 | 5.8% |

Files:
- `work/esm_heldout_baseline/esm_heldout_metrics.csv`
- `work/esm_heldout_baseline/esm_heldout_split_info.csv`
- `work/esm_heldout_baseline/esm_heldout_summary.json`
