# Ground-Motion Multi-Window Baseline Summary

Date: 2026-06-12

## Question

Do the 1 s, 3 s, and 10 s early waveform windows support the Nature Communications route?

Short answer: **yes, for the narrowed NC target.**

The result is stronger than the first PGA-only check. Across InstanceGM, early waveform information improves prediction beyond metadata for PGA, PGV, and spectral acceleration targets. Across K-NET, the same pattern holds for PGA. This supports a paper centered on transferable seismic waveform representation and hazard-relevant ground-motion inference. The learned-representation claim still requires direct evidence against simpler waveform features.

## Setup

Inputs:

- Script: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/scripts/run_ground_motion_baseline.py`
- Comparison CSV: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_baseline_multi_window_comparison.csv`
- Full metric CSV: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_baseline_multi_window_summary.csv`

Datasets:

- InstanceGM: PGA, PGV, SA03, SA10, SA30
- K-NET: PGA

Sampling:

- Train size: 5,000 records per dataset before target-specific filtering
- Test size: 1,000 records per dataset before target-specific filtering
- Windows: first 1 s, 3 s, and 10 s after the P arrival
- Model: HistGradientBoostingRegressor
- Target scale: `log10`

Feature sets:

- median baseline
- metadata-only
- early-waveform-only
- metadata + early waveform

The early-waveform features are computed only from the selected post-P window. Full-waveform peak features are not used, to avoid direct target leakage.

## Main Result

Comparison below reports metadata-only versus metadata + early waveform.

| window s | dataset | target | metadata MAE | combined MAE | MAE change | MAE reduction | metadata R2 | combined R2 | R2 gain | test rows |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | InstanceGM | PGA | 0.299 | 0.251 | -0.048 | 16.0% | 0.746 | 0.819 | 0.073 | 999 |
| 3 | InstanceGM | PGA | 0.299 | 0.243 | -0.057 | 18.9% | 0.746 | 0.822 | 0.076 | 999 |
| 10 | InstanceGM | PGA | 0.299 | 0.207 | -0.092 | 30.6% | 0.746 | 0.847 | 0.101 | 999 |
| 1 | InstanceGM | PGV | 0.298 | 0.214 | -0.084 | 28.1% | 0.663 | 0.829 | 0.166 | 1000 |
| 3 | InstanceGM | PGV | 0.298 | 0.203 | -0.095 | 31.9% | 0.663 | 0.844 | 0.182 | 1000 |
| 10 | InstanceGM | PGV | 0.298 | 0.165 | -0.133 | 44.7% | 0.663 | 0.863 | 0.201 | 1000 |
| 1 | InstanceGM | SA03 | 0.273 | 0.250 | -0.023 | 8.5% | 0.764 | 0.807 | 0.043 | 985 |
| 3 | InstanceGM | SA03 | 0.273 | 0.239 | -0.034 | 12.4% | 0.764 | 0.820 | 0.056 | 985 |
| 10 | InstanceGM | SA03 | 0.273 | 0.221 | -0.052 | 19.0% | 0.764 | 0.834 | 0.070 | 985 |
| 1 | InstanceGM | SA10 | 0.286 | 0.225 | -0.061 | 21.4% | 0.691 | 0.815 | 0.124 | 1000 |
| 3 | InstanceGM | SA10 | 0.286 | 0.220 | -0.066 | 23.1% | 0.691 | 0.826 | 0.135 | 1000 |
| 10 | InstanceGM | SA10 | 0.286 | 0.210 | -0.077 | 26.8% | 0.691 | 0.827 | 0.136 | 1000 |
| 1 | InstanceGM | SA30 | 0.306 | 0.246 | -0.060 | 19.6% | 0.492 | 0.693 | 0.201 | 945 |
| 3 | InstanceGM | SA30 | 0.306 | 0.243 | -0.063 | 20.7% | 0.492 | 0.699 | 0.207 | 945 |
| 10 | InstanceGM | SA30 | 0.306 | 0.242 | -0.064 | 20.9% | 0.492 | 0.680 | 0.187 | 945 |
| 1 | K-NET | PGA | 0.217 | 0.197 | -0.020 | 9.4% | 0.542 | 0.630 | 0.088 | 1000 |
| 3 | K-NET | PGA | 0.217 | 0.178 | -0.039 | 17.9% | 0.542 | 0.688 | 0.146 | 1000 |
| 10 | K-NET | PGA | 0.217 | 0.105 | -0.112 | 51.8% | 0.542 | 0.877 | 0.335 | 1000 |

## Interpretation

The result gives a clear positive baseline:

1. InstanceGM shows consistent gains for all five ground-motion targets.
2. K-NET independently supports the same PGA pattern.
3. Shorter windows already carry signal. The 1 s window improves all targets, which matters because it is harder to dismiss as a full-record proxy.
4. The 10 s window gives the largest gain. This should be treated as a lead-time-dependent result, because it can include more of the developing strong-motion signal.
5. SA30 has the weakest absolute R2 among InstanceGM targets, but the waveform gain remains visible at all windows.

The baseline supports a representation-learning paper if the learned encoder improves on metadata + hand-crafted waveform features or yields better robustness/calibration under dataset shift.

## NC Go/No-Go

Decision: **continue toward Nature Communications.**

The case is now stronger than a pure phase-picking benchmark. The current evidence supports an NC manuscript around:

**A label-aware seismic waveform representation for cross-dataset phase and ground-motion tasks.**

The paper should use three linked empirical facts:

1. Public waveform archives can be unified into a cross-task benchmark with 2.46 million records.
2. Existing phase pickers show reproducible dataset-specific failure modes.
3. Early waveform information improves hazard-relevant ground-motion prediction beyond source-path-site metadata.

The missing piece is the learned representation. Without it, the work is a strong benchmark and audit study, but the central method claim remains incomplete.

## Next Experiment

The next experiment should train a compact learned waveform encoder using the same unified manifest.

Minimum viable encoder:

- Input: ZNE waveform window
- Encoder: compact 1D CNN or small Conformer
- Heads:
  - phase/detection head for phase tasks
  - ground-motion regression head for PGA, PGV, SA03, SA10, SA30
- Metadata fusion: compare waveform-only, metadata-only, and waveform + metadata
- Splits: preserve dataset identity; test cross-dataset robustness

Minimum result needed for the NC route:

- Match or beat metadata + hand-crafted waveform features on at least one strong-motion target.
- Improve at least one phase robustness metric or calibration metric under dataset shift.
- Preserve interpretable residual analysis by magnitude, distance, depth, station, and dataset.

## Commands Used

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/run_ground_motion_baseline.py \
  --out-dir work/ground_motion_baseline_multi_1s \
  --train-size 5000 \
  --test-size 1000 \
  --early-seconds 1 \
  --targets pga pgv sa03 sa10 sa30 \
  --max-samples 20000

/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/run_ground_motion_baseline.py \
  --out-dir work/ground_motion_baseline_multi_3s \
  --train-size 5000 \
  --test-size 1000 \
  --early-seconds 3 \
  --targets pga pgv sa03 sa10 sa30 \
  --max-samples 20000

/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/run_ground_motion_baseline.py \
  --out-dir work/ground_motion_baseline_multi_10s \
  --train-size 5000 \
  --test-size 1000 \
  --early-seconds 10 \
  --targets pga pgv sa03 sa10 sa30 \
  --max-samples 20000
```
