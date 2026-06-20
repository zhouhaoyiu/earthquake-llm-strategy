# aq2009gm_full_stream AQ2009GM full-manifest chunk-streaming validation

This validation streams every chunk listed in the local SeisBench AQ2009GM chunk manifest. Raw HDF5 and metadata files were deleted after feature extraction with `--delete-raw`; the retained evidence is the compact feature table and generated metrics.

- chunks: 254
- metadata rows: 1258006
- valid records: 345226
- events: 60310
- stations: 66

## Splits

| Holdout | Eligible rows | Eligible groups | Train rows | Test rows | Train groups | Test groups | Overlap |
|---|---:|---:|---:|---:|---:|---:|---:|
| event | 345226 | 60310 | 30000 | 10000 | 21573 | 1731 | 0 |
| station | 345226 | 66 | 30000 | 10000 | 46 | 20 | 0 |
| time | 345226 | 60310 | 30000 | 10000 | 21438 | 2793 | 0 |

## Metadata + early velocity

| Holdout | Target | Window | Metadata MAE | Combined MAE | MAE reduction | Metadata R2 | Combined R2 |
|---|---|---:|---:|---:|---:|---:|---:|
| event | PGA | 1s | 0.205 | 0.145 | 29.3% | 0.841 | 0.922 |
| event | PGA | 3s | 0.205 | 0.109 | 46.8% | 0.841 | 0.952 |
| event | PGA | 10s | 0.205 | 0.077 | 62.5% | 0.841 | 0.977 |
| event | PGV | 1s | 0.192 | 0.132 | 31.1% | 0.854 | 0.934 |
| event | PGV | 3s | 0.192 | 0.087 | 54.8% | 0.854 | 0.966 |
| event | PGV | 10s | 0.192 | 0.025 | 86.7% | 0.854 | 0.994 |
| station | PGA | 1s | 0.311 | 0.222 | 28.8% | 0.639 | 0.810 |
| station | PGA | 3s | 0.311 | 0.175 | 43.9% | 0.639 | 0.871 |
| station | PGA | 10s | 0.311 | 0.113 | 63.6% | 0.639 | 0.949 |
| station | PGV | 1s | 0.286 | 0.183 | 36.0% | 0.674 | 0.861 |
| station | PGV | 3s | 0.286 | 0.142 | 50.4% | 0.674 | 0.907 |
| station | PGV | 10s | 0.286 | 0.025 | 91.4% | 0.674 | 0.994 |
| time | PGA | 1s | 0.271 | 0.176 | 35.1% | 0.676 | 0.862 |
| time | PGA | 3s | 0.271 | 0.134 | 50.4% | 0.676 | 0.911 |
| time | PGA | 10s | 0.271 | 0.092 | 66.1% | 0.676 | 0.960 |
| time | PGV | 1s | 0.249 | 0.151 | 39.4% | 0.702 | 0.898 |
| time | PGV | 3s | 0.249 | 0.095 | 62.0% | 0.702 | 0.951 |
| time | PGV | 10s | 0.249 | 0.024 | 90.3% | 0.702 | 0.995 |

## Extra analysis files

- subgroup: `work/aq2009gm_full_stream_validation/aq2009gm_full_stream_subgroup.csv`
- uncertainty: `work/aq2009gm_full_stream_validation/aq2009gm_full_stream_uncertainty.csv`
- chunk inventory: `work/aq2009gm_full_stream_validation/chunk_inventory.csv`
- figure: `outputs/figures/ground_motion_audit/aq2009gm_full_stream_panel.png`
