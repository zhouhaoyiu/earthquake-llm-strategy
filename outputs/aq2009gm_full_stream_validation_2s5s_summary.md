# aq2009gm_full_stream AQ2009GM full-manifest chunk-streaming validation

This validation streams every chunk listed in the local SeisBench AQ2009GM chunk manifest. Raw HDF5 and metadata files may be deleted after feature extraction when `--delete-raw` is used; the retained evidence is the compact feature table and generated metrics.

- chunks: 254
- metadata rows: 1246783
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
| event | PGA | 2s | 0.205 | 0.128 | 37.6% | 0.841 | 0.937 |
| event | PGA | 5s | 0.205 | 0.087 | 57.8% | 0.841 | 0.969 |
| event | PGV | 2s | 0.192 | 0.114 | 40.5% | 0.854 | 0.949 |
| event | PGV | 5s | 0.192 | 0.048 | 74.9% | 0.854 | 0.985 |
| station | PGA | 2s | 0.311 | 0.206 | 33.9% | 0.639 | 0.832 |
| station | PGA | 5s | 0.311 | 0.138 | 55.8% | 0.639 | 0.921 |
| station | PGV | 2s | 0.286 | 0.166 | 42.1% | 0.674 | 0.883 |
| station | PGV | 5s | 0.286 | 0.081 | 71.9% | 0.674 | 0.958 |
| time | PGA | 2s | 0.271 | 0.162 | 40.1% | 0.676 | 0.878 |
| time | PGA | 5s | 0.271 | 0.103 | 61.9% | 0.676 | 0.946 |
| time | PGV | 2s | 0.249 | 0.135 | 46.0% | 0.702 | 0.918 |
| time | PGV | 5s | 0.249 | 0.048 | 80.6% | 0.702 | 0.984 |

## Extra analysis files

- subgroup: `work/aq2009gm_full_stream_validation_2s5s/aq2009gm_full_stream_subgroup.csv`
- uncertainty: `work/aq2009gm_full_stream_validation_2s5s/aq2009gm_full_stream_uncertainty.csv`
- chunk inventory: `work/aq2009gm_full_stream_validation_2s5s/chunk_inventory.csv`
- figure: `outputs/figures/ground_motion_audit/aq2009gm_full_stream_2s5s_panel.png`
