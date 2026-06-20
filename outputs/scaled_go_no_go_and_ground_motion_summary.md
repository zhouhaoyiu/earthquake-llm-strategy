# Scaled Go/No-Go and Ground-Motion Baseline Summary

Date: 2026-06-12

## Question

Does the project still look viable after scaling the phase baseline to 1,000 records per dataset and adding multi-window strong-motion baselines?

Short answer: **yes, with a narrowed claim.**

The evidence supports continuing with a Nature Communications-style direction around cross-dataset seismic representation, label/domain audit, and strong-motion transfer. It does not support an "LLM earthquake prediction" claim.

## Phase Baseline at 1,000 Records per Dataset

Inputs:

- Unified manifest: `work/unified_manifest/unified_manifest.csv.gz`
- Script: `work/scripts/run_phase_baseline_pilot.py`
- Output directory: `work/baseline_pilot_1000_stead_models`

Setup:

- Datasets: STEAD, InstanceGM, Iquique, K-NET
- Split: test
- Records: 1,000 per dataset, 4,000 total
- Models: PhaseNet(STEAD), EQTransformer(STEAD)
- Predictions: 8,000 model-record pairs
- Failures: 0
- Sample-length filter: 6,000 to 20,000 samples

### Phase Results

| model | dataset | phase | matched | missing | missing rate | median abs s | MAE s | q95 abs s | >2 s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PhaseNet(STEAD) | STEAD | P | 1000 | 0 | 0.000 | 0.020 | 0.035 | 0.120 | 0 |
| PhaseNet(STEAD) | STEAD | S | 1000 | 0 | 0.000 | 0.032 | 0.082 | 0.340 | 1 |
| EQTransformer(STEAD) | STEAD | P | 858 | 142 | 0.142 | 0.020 | 0.339 | 0.140 | 10 |
| EQTransformer(STEAD) | STEAD | S | 999 | 1 | 0.001 | 0.040 | 0.093 | 0.335 | 0 |
| PhaseNet(STEAD) | InstanceGM | P | 867 | 133 | 0.133 | 0.060 | 0.446 | 0.760 | 12 |
| PhaseNet(STEAD) | InstanceGM | S | 548 | 452 | 0.452 | 0.070 | 0.348 | 0.986 | 9 |
| EQTransformer(STEAD) | InstanceGM | P | 813 | 187 | 0.187 | 0.070 | 0.917 | 1.138 | 28 |
| EQTransformer(STEAD) | InstanceGM | S | 521 | 479 | 0.479 | 0.080 | 0.609 | 1.100 | 11 |
| PhaseNet(STEAD) | Iquique | P | 978 | 22 | 0.022 | 0.090 | 0.473 | 0.630 | 4 |
| PhaseNet(STEAD) | Iquique | S | 834 | 166 | 0.166 | 0.185 | 0.665 | 1.183 | 12 |
| EQTransformer(STEAD) | Iquique | P | 970 | 30 | 0.030 | 0.100 | 0.431 | 0.585 | 6 |
| EQTransformer(STEAD) | Iquique | S | 844 | 156 | 0.156 | 0.180 | 0.423 | 1.217 | 10 |
| PhaseNet(STEAD) | K-NET | P | 962 | 38 | 0.038 | 0.030 | 0.056 | 0.169 | 0 |
| PhaseNet(STEAD) | K-NET | S | 1000 | 0 | 0.000 | 0.110 | 0.299 | 1.051 | 12 |
| EQTransformer(STEAD) | K-NET | P | 855 | 145 | 0.145 | 0.030 | 0.314 | 0.153 | 4 |
| EQTransformer(STEAD) | K-NET | S | 1000 | 0 | 0.000 | 0.110 | 0.299 | 1.061 | 12 |

### Phase Interpretation

The scaled phase baseline supports the earlier diagnosis:

- STEAD is stable, especially for PhaseNet.
- K-NET P picks are strong after BSON-to-HDF5 conversion, which supports the converted K-NET data as usable.
- K-NET S picks are not globally shifted, but the residual tail is wider. This is a domain/label/post-processing audit target.
- Iquique has reliable P recovery and harder S recovery, consistent with regional transfer difficulty.
- InstanceGM has the clearest cross-domain issue: S missing rate around 45-48% and larger tail errors.

This supports the "cross-dataset failure modes and label/domain audit" premise.

## Strong-Motion Baseline

Inputs:

- Script: `work/scripts/run_ground_motion_baseline.py`
- Output directories:
  - `work/ground_motion_baseline_multi_1s`
  - `work/ground_motion_baseline_multi_3s`
  - `work/ground_motion_baseline_multi_10s`
- Comparison CSV: `work/ground_motion_baseline_multi_window_comparison.csv`

Setup:

- Datasets: InstanceGM and K-NET
- Targets: InstanceGM PGA, PGV, SA03, SA10, SA30; K-NET PGA
- Train size: 5,000 per dataset
- Test size: 1,000 per dataset
- Models: median baseline and HistGradientBoostingRegressor
- Feature sets:
  - metadata-only: magnitude, depth, distance, station elevation, Vs30 when available, year, sample count
  - early-waveform-only: features from first 1 s, 3 s, or 10 s after P arrival
  - metadata + early waveform
- Full-waveform peak features were not used, to avoid PGA label leakage.

### Ground-Motion Results

| window s | dataset | target | metadata MAE | combined MAE | MAE reduction | metadata R2 | combined R2 |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | InstanceGM | PGA | 0.299 | 0.251 | 16.0% | 0.746 | 0.819 |
| 3 | InstanceGM | PGA | 0.299 | 0.243 | 18.9% | 0.746 | 0.822 |
| 10 | InstanceGM | PGA | 0.299 | 0.207 | 30.6% | 0.746 | 0.847 |
| 1 | InstanceGM | PGV | 0.298 | 0.214 | 28.1% | 0.663 | 0.829 |
| 3 | InstanceGM | PGV | 0.298 | 0.203 | 31.9% | 0.663 | 0.844 |
| 10 | InstanceGM | PGV | 0.298 | 0.165 | 44.7% | 0.663 | 0.863 |
| 1 | InstanceGM | SA03 | 0.273 | 0.250 | 8.5% | 0.764 | 0.807 |
| 3 | InstanceGM | SA03 | 0.273 | 0.239 | 12.4% | 0.764 | 0.820 |
| 10 | InstanceGM | SA03 | 0.273 | 0.221 | 19.0% | 0.764 | 0.834 |
| 1 | InstanceGM | SA10 | 0.286 | 0.225 | 21.4% | 0.691 | 0.815 |
| 3 | InstanceGM | SA10 | 0.286 | 0.220 | 23.1% | 0.691 | 0.826 |
| 10 | InstanceGM | SA10 | 0.286 | 0.210 | 26.8% | 0.691 | 0.827 |
| 1 | InstanceGM | SA30 | 0.306 | 0.246 | 19.6% | 0.492 | 0.693 |
| 3 | InstanceGM | SA30 | 0.306 | 0.243 | 20.7% | 0.492 | 0.699 |
| 10 | InstanceGM | SA30 | 0.306 | 0.242 | 20.9% | 0.492 | 0.680 |
| 1 | K-NET | PGA | 0.217 | 0.197 | 9.4% | 0.542 | 0.630 |
| 3 | K-NET | PGA | 0.217 | 0.178 | 17.9% | 0.542 | 0.688 |
| 10 | K-NET | PGA | 0.217 | 0.105 | 51.8% | 0.542 | 0.877 |

### Ground-Motion Interpretation

This is the strongest positive signal so far.

For InstanceGM, adding early waveform features to metadata improves every tested target across every tested window. The 1 s window already improves PGA, PGV, SA03, SA10, and SA30. The 10 s window gives larger gains, with the strongest effects for PGV and K-NET PGA.

For K-NET, the same pattern holds for PGA across 1 s, 3 s, and 10 s windows.

This supports the idea that waveform information adds useful hazard-relevant signal beyond source/path/site metadata. The result is still a baseline built from hand-crafted early-window features. The 10 s results should be framed as window-dependent information gain, not as an operational warning claim.

## Updated Go/No-Go Decision

Decision: **Go for the narrowed NC route.**

The scaled checks support three parts of the revised paper:

1. Cross-dataset phase models have structured, measurable failure modes.
2. Strong-motion data are usable in the same unified workflow.
3. Early waveform information improves ground-motion prediction beyond metadata-only baselines across InstanceGM targets and K-NET PGA.

This is enough to continue toward:

**A label-aware seismic waveform representation for cross-dataset phase and ground-motion tasks.**

Science Advances would require a broader geophysical or hazard-relevant insight beyond engineering performance.

## Next Required Evidence

1. Scale phase audit to 5,000 records per dataset or full test sets where feasible.
2. Add calibration metrics and missing-pick analysis alongside MAE.
3. Train a compact learned waveform encoder and compare against these hand-crafted early-window features.
4. Analyze source-path-site residuals by magnitude, distance, depth, station, network, and event.
5. Add calibration and uncertainty metrics for both phase and ground-motion outputs.

## Commands

Phase baseline:

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/run_phase_baseline_pilot.py \
  --out-dir work/baseline_pilot_1000_stead_models \
  --per-dataset 1000 \
  --min-samples 6000 \
  --max-samples 20000 \
  --models phasenet_stead eqtransformer_stead
```

Strong-motion baseline:

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/run_ground_motion_baseline.py \
  --out-dir work/ground_motion_baseline_multi_3s \
  --train-size 5000 \
  --test-size 1000 \
  --early-seconds 3 \
  --targets pga pgv sa03 sa10 sa30 \
  --max-samples 20000
```
