# PNW Accelerometer Peak-Amplitude Baseline

Date: 2026-06-21

## Position

This is an independent SeisBench accelerometer robustness check. It is not publication-ready PGA evidence because the local PNWAccelerometers HDF5 file records `component_order=ENZ` but no waveform unit field. The target is full-record peak horizontal waveform amplitude.

## Data and splits

- Usable earthquake accelerometer records: 5,981
- Held-event: train 4,000, test 1,000, test events 552, overlap=0
- Held-station: train 4,000, test 1,000, test stations 40, overlap=0

## Results

| holdout | window | metadata MAE | combined MAE | reduction | combined R2 |
|---|---:|---:|---:|---:|---:|
| event | 2s | 0.239 | 0.191 | 20.1% | 0.857 |
| event | 5s | 0.239 | 0.097 | 59.4% | 0.936 |
| event | 10s | 0.239 | 0.036 | 85.0% | 0.978 |
| station | 2s | 0.361 | 0.220 | 39.2% | 0.788 |
| station | 5s | 0.361 | 0.115 | 68.0% | 0.909 |
| station | 10s | 0.361 | 0.034 | 90.5% | 0.980 |

## Interpretation

The 2 s and 5 s results support the same qualitative pattern in a separate accelerometer dataset: early waveform amplitude adds information beyond source-path metadata under both held-event and held-station splits. The 10 s results are very strong and should be interpreted cautiously because the full-record peak can already fall inside that window.

Figure: `outputs/figures/ground_motion_audit/pnw_accelerometer_peak_panel.png`
Reduction table: `outputs/pnw_accelerometer_peak_reduction_summary.csv`
