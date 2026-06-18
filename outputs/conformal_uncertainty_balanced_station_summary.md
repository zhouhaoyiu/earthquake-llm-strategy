# Conformal Uncertainty: Balanced Held-Station Split

Date: 2026-06-18

## Result

Split-conformal intervals were tested on the 10 s balanced held-station features.

Nominal coverage is 90%.

| dataset | target | test rows | MAE | interval width | coverage |
|---|---|---:|---:|---:|---:|
| InstanceGM | PGA | 1000 | 0.259 | 0.913 | 0.845 |
| InstanceGM | PGV | 1000 | 0.178 | 0.774 | 0.898 |
| InstanceGM | SA03 | 992 | 0.246 | 0.930 | 0.859 |
| InstanceGM | SA10 | 1000 | 0.268 | 0.877 | 0.820 |
| InstanceGM | SA30 | 942 | 0.249 | 0.946 | 0.876 |
| K-NET | PGA | 1000 | 0.113 | 0.545 | 0.925 |

## Interpretation

K-NET PGA is well calibrated under balanced station holdout.

InstanceGM PGV is close to nominal coverage. InstanceGM PGA and spectral acceleration targets under-cover under station transfer, especially SA10.

This should be framed as a residual uncertainty result, not hidden:

**Early waveform features improve point prediction under station holdout, but uncertainty calibration remains target-dependent under station shift.**

## Files

- Script: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/scripts/run_conformal_intervals.py`
- CSV: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_balanced_station_10s/conformal_intervals.csv`

## Command

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/run_conformal_intervals.py \
  --feature-dir work/ground_motion_balanced_station_10s \
  --out work/ground_motion_balanced_station_10s/conformal_intervals.csv
```
