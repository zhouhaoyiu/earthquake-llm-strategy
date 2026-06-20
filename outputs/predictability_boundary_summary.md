# Predictability Boundary Summary

This file is generated from existing figure tables. It does not add new model runs.

## Main Boundary Table

| Dataset | Target | Random 10 s MAE | Held-event MAE | Held-station MAE | Robust held-out gain % | Coverage | Coverage gap to 90% | Boundary note |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| instancegm | pga | 0.207 | 0.191 | 0.253 | 35.5 | 0.845 | -0.055 | strong point gain; uncertainty remains target-dependent |
| instancegm | pgv | 0.165 | 0.155 | 0.176 | 50.4 | 0.898 | -0.002 | strong point gain; uncertainty remains target-dependent |
| instancegm | sa03 | 0.221 | 0.223 | 0.242 | 22.5 | 0.859 | -0.041 | useful point gain; boundary set by held-station residuals |
| instancegm | sa10 | 0.210 | 0.212 | 0.262 | 20.9 | 0.820 | -0.080 | useful point gain; boundary set by held-station residuals |
| instancegm | sa30 | 0.242 | 0.224 | 0.248 | 24.9 | 0.876 | -0.024 | useful point gain; boundary set by held-station residuals |
| knet | pga | 0.105 | 0.108 | 0.111 | 49.9 | 0.925 | 0.025 | strong gain with calibrated station-shift interval |

## Manuscript Use

- Strongest robust held-out gain: instancegm pgv, 50.4%.
- Weakest robust held-out gain: instancegm sa10, 20.9%.
- Under-coverage targets at nominal 90%: instancegm:pga, instancegm:pgv, instancegm:sa03, instancegm:sa10, instancegm:sa30.
- Use the table to state empirical predictability boundaries: early windows improve point prediction, while held-station residuals and conformal coverage define the present limit.

## AQ2009GM Supplement

- AQ2009GM full-manifest chunk-streaming 10 s minimum held-out gain: PGA 62.5%, PGV 86.7%.
- This is a full-manifest streaming validation over the local SeisBench AQ2009GM chunk list; raw HDF5 files are not retained.

## Cross-Region Transfer Boundary

- Early-waveform-only transfer was tested across InstanceGM, K-NET, and AQ2009GM using held-out target-domain test records.
- Zero-shot cross-region transfer has a median MAE ratio of 2.84 relative to target-domain training.
- Target-train offset calibration lowers the median ratio to 2.26, so simple target-domain calibration helps but does not remove the boundary.
- The same transfer check now covers 1, 3, and 10 s early windows:

| Window | Zero-shot median ratio | Target-train offset-calibrated median ratio |
|---:|---:|---:|
| 1 s | 1.49 | 1.40 |
| 3 s | 1.74 | 1.65 |
| 10 s | 2.84 | 2.26 |

- The transfer penalty increases with window length, indicating that later early-window amplitude structure carries more regional and measurement-system dependence.
- This supports a bounded claim: early P-window information is useful within curated public strong-motion domains, while direct regional transfer is limited by waveform measurement, target scale, and dataset shift.
