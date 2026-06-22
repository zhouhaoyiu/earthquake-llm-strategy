# CWA official PGA/PGV independent layer

## Scope

- Source: SeisBench CWA benchmark, year 2011.
- Eligible official PGA/PGV records: 5,882.
- Feature rows: 11,764.
- Events: 775.
- Stations: 705.
- Targets: `trace_pga_cmps2` and `trace_pgv_cmps` from CWA metadata.
- HDF5 format: measurement=, unit=, component_order=ZNE.
- Raw CWA metadata/HDF5 and downloaded tar are deleted after the run when `--cleanup-raw` is used.

## Metadata + early waveform vs metadata-only

| Holdout | Target | Window | Metadata MAE | Combined MAE | MAE reduction | Metadata R2 | Combined R2 |
|---|---|---:|---:|---:|---:|---:|---:|
| event | PGA | 2s | 0.173 | 0.147 | 15.3% | 0.470 | 0.620 |
| event | PGA | 5s | 0.173 | 0.113 | 34.9% | 0.470 | 0.761 |
| event | PGV | 2s | 0.305 | 0.254 | 16.8% | 0.470 | 0.624 |
| event | PGV | 5s | 0.305 | 0.178 | 41.7% | 0.470 | 0.784 |
| station | PGA | 2s | 0.157 | 0.134 | 14.6% | 0.559 | 0.687 |
| station | PGA | 5s | 0.157 | 0.110 | 29.9% | 0.559 | 0.779 |
| station | PGV | 2s | 0.271 | 0.223 | 17.7% | 0.573 | 0.711 |
| station | PGV | 5s | 0.271 | 0.162 | 40.3% | 0.573 | 0.849 |

## Evidence boundary

This is an official CWA PGA/PGV metadata-target layer from real waveforms. It supports an independent Taiwan check for early-window information.
It is a one-year CWA layer, not a full 2011-2021 CWA benchmark.
Waveform read errors: 0.

## Files

- Comparison: `work/cwa_official_layer/cwa_official_comparison.csv`
- Metrics: `work/cwa_official_layer/cwa_official_metrics.csv`
- Features: `work/cwa_official_layer/cwa_official_features.csv.gz`
- Figure: `outputs/figures/ground_motion_audit/cwa_official_pga_pgv_panel.png`
