# Held-Out Ground-Motion Baseline Summary

Date: 2026-06-15

## Question

Do the 10 s early post-P waveform features still improve strong-motion inference when the train/test split holds out entire events or entire stations?

Short answer: **yes for the main early-window claim, with target-specific limits.**

The held-event results are strong across all InstanceGM targets and K-NET PGA. The held-station results remain strong for InstanceGM PGA, InstanceGM PGV, InstanceGM SA30, and K-NET PGA, weaker for InstanceGM SA03, and nearly neutral for InstanceGM SA10.

## Setup

Script:

- `work/scripts/run_ground_motion_heldout_baseline.py`

Outputs:

- Results: `work/ground_motion_heldout_10s/ground_motion_heldout_results.csv`
- Split info: `work/ground_motion_heldout_10s/ground_motion_heldout_split_info.csv`
- Summary JSON: `work/ground_motion_heldout_10s/ground_motion_heldout_summary.json`

Model:

- HGB metadata-only baseline
- HGB metadata plus 10 s early waveform features
- Targets in log10 units
- Train size: 5,000 records per dataset/split before target-specific filtering
- Test size: 1,000 records per dataset/split before target-specific filtering

The split uses `event_id` for held-event and `station_network_code.station_code` for held-station. All group overlaps are zero.

## Split Integrity

| dataset | holdout | eligible rows | eligible groups | train rows | test rows | train groups | test groups | group overlap |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| InstanceGM | event | 1,159,223 | 54,008 | 5,000 | 1,000 | 4,598 | 51 | 0 |
| InstanceGM | station | 1,159,223 | 631 | 5,000 | 1,000 | 444 | 2 | 0 |
| K-NET | event | 21,839 | 1,528 | 5,000 | 1,000 | 1,290 | 70 | 0 |
| K-NET | station | 21,839 | 908 | 5,000 | 1,000 | 739 | 43 | 0 |

Note: InstanceGM held-station is strict but narrow because the 1,000-record test sample is drawn from only two large held-out stations. This should be reported as a limitation.

## Main Result

The table compares metadata-only HGB against metadata plus 10 s early waveform features.

| dataset | holdout | target | test rows | metadata MAE | combined MAE | MAE reduction | combined R2 |
|---|---|---|---:|---:|---:|---:|---:|
| InstanceGM | event | PGA | 998 | 0.312 | 0.191 | 38.8% | 0.875 |
| InstanceGM | event | PGV | 998 | 0.313 | 0.155 | 50.4% | 0.895 |
| InstanceGM | event | SA03 | 987 | 0.287 | 0.223 | 22.5% | 0.842 |
| InstanceGM | event | SA10 | 997 | 0.282 | 0.212 | 24.7% | 0.855 |
| InstanceGM | event | SA30 | 932 | 0.298 | 0.224 | 24.9% | 0.723 |
| InstanceGM | station | PGA | 1000 | 0.437 | 0.316 | 27.6% | 0.599 |
| InstanceGM | station | PGV | 1000 | 0.339 | 0.172 | 49.2% | 0.858 |
| InstanceGM | station | SA03 | 999 | 0.324 | 0.292 | 9.8% | 0.699 |
| InstanceGM | station | SA10 | 1000 | 0.209 | 0.208 | 0.3% | 0.777 |
| InstanceGM | station | SA30 | 865 | 0.220 | 0.183 | 16.9% | 0.581 |
| K-NET | event | PGA | 1000 | 0.238 | 0.108 | 54.5% | 0.869 |
| K-NET | station | PGA | 1000 | 0.211 | 0.109 | 48.4% | 0.886 |

## Interpretation

The held-event result strengthens the core claim. For InstanceGM, every target improves under event-held-out evaluation. For K-NET, held-event PGA improves from 0.238 to 0.108 MAE, close to the random-split 10 s result.

The held-station result is more nuanced. K-NET PGA remains strong with 43 held-out stations. InstanceGM PGV remains very strong, and PGA still improves substantially. SA03 and SA30 improve modestly. SA10 shows almost no held-station gain in this sample.

This changes the manuscript claim in a useful way:

**Early waveform information is robust under held-event evaluation and remains valuable under held-station evaluation, but station generalization is target-dependent for spectral acceleration.**

## Paper Consequence

This is a major upgrade over the random-split baseline. It directly addresses the most likely reviewer concern: event or station leakage.

The NC route is stronger after this experiment. The paper can now present:

1. random split as a baseline;
2. held-event as the main generalization test;
3. held-station as a stricter station-transfer test;
4. target-specific limits for spectral acceleration.

Do not overstate the result. The strongest claims are K-NET PGA, InstanceGM PGV, and InstanceGM held-event across all targets. InstanceGM held-station SA10 should be described as a weak or neutral case.

## Method Note

During implementation, the first held-event split exposed an indexing bug: shuffling the array returned by `Index.to_numpy()` could mutate the Pandas index backing `value_counts`, causing group-size accounting to mismatch selected group labels. The script now copies the group labels before shuffling:

```python
groups = np.array(group_sizes.index.tolist(), dtype=object)
```

The final split integrity table confirms `group_overlap = 0` for every dataset and holdout type.

## Command

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/run_ground_motion_heldout_baseline.py \
  --out-dir work/ground_motion_heldout_10s \
  --early-seconds 10 \
  --train-size 5000 \
  --test-size 1000 \
  --targets pga pgv sa03 sa10 sa30 \
  --max-samples 20000
```
