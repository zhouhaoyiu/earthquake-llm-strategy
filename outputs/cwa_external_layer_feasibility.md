# CWA Official PGA/PGV Layer

Date: 2026-06-21

## Completed layer

- Source: SeisBench CWA benchmark, year 2011.
- Downloaded archive: `merge2011_2014.tar.gz`.
- Extracted files: `metadata_2011.csv` and `waveforms_2011.hdf5`.
- Eligible official PGA/PGV records: 5,882.
- Events: 775.
- Stations: 705.
- Targets: `trace_pga_cmps2` and `trace_pgv_cmps`.
- Raw CWA metadata, HDF5 and tar archive were deleted after feature extraction.

## Result

The retained feature-table validation shows positive early-waveform gains for both official metadata targets under held-event and held-station splits.

| Holdout | Target | 2 s reduction | 5 s reduction |
|---|---|---:|---:|
| event | PGA | 15.3% | 34.9% |
| event | PGV | 16.8% | 41.7% |
| station | PGA | 14.6% | 29.9% |
| station | PGV | 17.7% | 40.3% |

## Evidence boundary

This is now a real CWA official PGA/PGV independent layer, not a feasibility placeholder. It covers one CWA year and should be described as a Taiwan supplementary check, not as full 2011-2021 CWA validation.

## Files

- Summary: `outputs/cwa_official_pga_pgv_summary.md`
- Figure: `outputs/figures/ground_motion_audit/cwa_official_pga_pgv_panel.png`
- Features: `work/cwa_official_layer/cwa_official_features.csv.gz`
- Metrics: `work/cwa_official_layer/cwa_official_comparison.csv`
