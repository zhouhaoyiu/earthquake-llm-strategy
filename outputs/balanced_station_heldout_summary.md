# Balanced Held-Station Ground-Motion Summary

Date: 2026-06-18

## Result

Balanced held-station split fixes the narrow InstanceGM station test.

The split holds out 50 stations for InstanceGM and 50 stations for K-NET. Group overlap is zero.

| dataset | target | test rows | metadata MAE | combined MAE | MAE reduction | combined R2 |
|---|---|---:|---:|---:|---:|---:|
| InstanceGM | PGA | 1000 | 0.392 | 0.253 | 35.5% | 0.799 |
| InstanceGM | PGV | 1000 | 0.372 | 0.176 | 52.6% | 0.858 |
| InstanceGM | SA03 | 992 | 0.327 | 0.242 | 26.0% | 0.814 |
| InstanceGM | SA10 | 1000 | 0.331 | 0.262 | 20.9% | 0.785 |
| InstanceGM | SA30 | 942 | 0.343 | 0.248 | 27.8% | 0.683 |
| K-NET | PGA | 1000 | 0.222 | 0.111 | 49.9% | 0.875 |

## Interpretation

This is stronger than the previous held-station result because the test set covers many stations instead of two large InstanceGM stations.

The early waveform claim now holds under:

- random split;
- held-event split;
- balanced held-station split.

The strongest targets remain K-NET PGA and InstanceGM PGV. The spectral acceleration targets also improve under balanced station holdout, including SA10, which was neutral in the earlier narrow station split.

## Files

- Results: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_balanced_station_10s/ground_motion_heldout_results.csv`
- Split info: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_balanced_station_10s/ground_motion_heldout_split_info.csv`
- Figure: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit/balanced_station_heldout_panel.png`

## Command

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/run_ground_motion_heldout_baseline.py \
  --out-dir work/ground_motion_balanced_station_10s \
  --holdouts station \
  --station-test-groups 50 \
  --early-seconds 10 \
  --train-size 5000 \
  --test-size 1000 \
  --targets pga pgv sa03 sa10 sa30 \
  --max-samples 20000
```
