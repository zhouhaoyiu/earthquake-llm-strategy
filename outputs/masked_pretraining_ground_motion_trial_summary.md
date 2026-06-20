# Masked Pretraining Ground-Motion Trial Summary

Date: 2026-06-12

## Question

Does masked waveform reconstruction pretraining improve the learned ground-motion encoder?

Short answer: **no for the current design.**

The pretraining run completed and learned a modest reconstruction signal. The downstream ground-motion results are weaker than both the scratch CNN and the HGB baseline with hand-crafted early-window features. This rules out naive masked reconstruction as the next NC method.

## Setup

Script:

- `work/scripts/run_masked_pretrain_ground_motion.py`

Outputs:

- Metrics: `work/masked_pretrain_ground_motion_10s_3k_5k/masked_pretrain_ground_motion_results.csv`
- Predictions: `work/masked_pretrain_ground_motion_10s_3k_5k/masked_pretrain_ground_motion_predictions.csv`
- Comparison: `work/masked_pretrain_vs_scratch_hgb_10s_comparison.csv`

Pretraining:

- Datasets: STEAD, InstanceGM, Iquique, K-NET
- Samples: 3,000 records per dataset, 12,000 total
- Window: first 10 s after P arrival, resampled to 1,000 samples
- Objective: reconstruct masked waveform blocks
- Epochs: 8
- Device: MPS

Fine-tuning:

- Datasets: InstanceGM and K-NET
- Train/test size: 5,000/1,000 per dataset before target-specific filtering
- Targets: InstanceGM PGA, PGV, SA03, SA10, SA30; K-NET PGA
- Variants: pretrained waveform-only, pretrained waveform + metadata

## Pretraining Signal

Masked reconstruction validation MSE improved from 0.913 at epoch 1 to 0.877 at epoch 8.

This shows that the model learned some waveform structure. The improvement is modest, and the downstream test decides whether it is useful for the paper claim.

## Downstream Result

The table compares the strongest masked-pretrain variant, pretrained CNN + metadata, against the scratch CNN + metadata and HGB metadata + hand-crafted early waveform baseline.

| dataset | target | masked pretrain MAE | scratch CNN MAE | HGB combined MAE | pretrain-HGB MAE | masked pretrain R2 | HGB combined R2 |
|---|---|---:|---:|---:|---:|---:|---:|
| InstanceGM | PGA | 0.518 | 0.362 | 0.207 | +0.311 | 0.404 | 0.847 |
| InstanceGM | PGV | 0.463 | 0.351 | 0.165 | +0.298 | 0.383 | 0.863 |
| InstanceGM | SA03 | 0.770 | 0.321 | 0.221 | +0.549 | -101.654 | 0.834 |
| InstanceGM | SA10 | 0.494 | 0.330 | 0.210 | +0.285 | 0.244 | 0.827 |
| InstanceGM | SA30 | 0.422 | 0.351 | 0.242 | +0.180 | 0.068 | 0.680 |
| K-NET | PGA | 0.142 | 0.139 | 0.105 | +0.038 | 0.796 | 0.877 |

The SA03 R2 failure comes from an unstable extreme prediction in one InstanceGM test record. Even without that outlier, the masked-pretrain model trails HGB by a wide margin.

## Interpretation

The current pretraining objective is not aligned with the ground-motion task.

Three likely reasons:

1. Raw masked reconstruction rewards local waveform completion, while PGA/PGV/SA depend strongly on amplitude envelopes, peaks, source-path-site variables, and target-specific frequency response.
2. Cross-dataset amplitude scales differ strongly. A single reconstruction scaler across STEAD, InstanceGM, Iquique, and K-NET may dilute the InstanceGM amplitude structure needed for strong-motion regression.
3. The fine-tuning objective remains within-dataset random sampling. It does not yet test the setting where a representation model should have the clearest advantage: cross-dataset, held-event, or held-station transfer.

## Decision

Decision: **do not use naive masked reconstruction as the NC method.**

The NC route remains possible because the data audit and HGB baselines are strong. The learned-representation route now requires a more targeted mechanism:

- phase-aware pretraining using P/S arrivals and picker disagreement;
- contrastive learning across augmented windows from the same event or station;
- multi-task training over phase, detection, and ground-motion heads;
- explicit amplitude-preserving inputs plus source-path-site metadata;
- evaluation under event-held-out and station-held-out splits.

The current evidence supports a stricter paper strategy:

**Use HGB and scratch CNN as serious baselines, and only claim representation learning if the next model improves cross-dataset robustness, calibration, or residual structure.**

## Next Step

The most useful next experiment is not another raw reconstruction run. It should be one of:

1. **Phase-aware pretraining:** predict masked P/S neighborhood structure and use picker-disagreement weights.
2. **Event/station contrastive pretraining:** pull together windows from the same event or station and push apart unrelated records.
3. **Residual-centered modeling:** keep HGB as the prediction engine and analyze residual structure by magnitude, distance, depth, station, and dataset.

For the NC route, option 1 is the best method route. Option 3 is the safest benchmark-and-science route.

## Commands

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/run_masked_pretrain_ground_motion.py \
  --out-dir work/masked_pretrain_ground_motion_10s_3k_5k \
  --pretrain-size-per-dataset 3000 \
  --finetune-datasets instancegm knet \
  --targets pga pgv sa03 sa10 sa30 \
  --train-size 5000 \
  --test-size 1000 \
  --early-seconds 10 \
  --pretrain-epochs 8 \
  --epochs 30 \
  --pretrain-batch-size 256 \
  --batch-size 256 \
  --max-samples 20000
```
