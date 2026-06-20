# Waveform Encoder Ground-Motion Trial Summary

Date: 2026-06-12

## Question

Can a compact learned waveform encoder beat the current hand-crafted early-window baseline on the 3 s ground-motion task?

Short answer: **not yet.**

The learned encoder pipeline works, but the current supervised CNN does not beat the HistGradientBoosting baseline using hand-crafted early-window features. This is a useful go/no-go result. It keeps the NC route alive, but it weakens any claim that a simple learned waveform encoder is already sufficient.

## Setup

Script:

- `work/scripts/run_waveform_encoder_ground_motion.py`

Outputs:

- Metrics: `work/waveform_encoder_ground_motion_3s_5k_pool/waveform_encoder_ground_motion_results.csv`
- Predictions: `work/waveform_encoder_ground_motion_3s_5k_pool/waveform_encoder_ground_motion_predictions.csv`
- 10 s metrics: `work/waveform_encoder_ground_motion_10s_5k_pool/waveform_encoder_ground_motion_results.csv`
- HGB comparison: `work/waveform_encoder_vs_hgb_3s_10s_comparison.csv`

Configuration:

- Datasets: InstanceGM and K-NET
- Windows: first 3 s and 10 s after P arrival
- Train/test size: 5,000/1,000 records per dataset before target-specific filtering
- Targets: InstanceGM PGA, PGV, SA03, SA10, SA30; K-NET PGA
- Model: compact 1D CNN with avg+max temporal pooling
- Variants: waveform-only, waveform + metadata
- Epochs: 30
- Device: MPS
- Targets: standardized during training and transformed back to `log10` units for reporting

## Main Comparison at 3 s

The table compares the stronger CNN variant, waveform + metadata, against the strongest current HGB baseline, metadata + hand-crafted early-waveform features.

| dataset | target | CNN+metadata MAE | HGB combined MAE | CNN-HGB MAE | CNN+metadata R2 | HGB combined R2 |
|---|---|---:|---:|---:|---:|---:|
| InstanceGM | PGA | 0.361 | 0.243 | +0.118 | 0.626 | 0.822 |
| InstanceGM | PGV | 0.341 | 0.203 | +0.138 | 0.570 | 0.844 |
| InstanceGM | SA03 | 0.319 | 0.239 | +0.080 | 0.675 | 0.820 |
| InstanceGM | SA10 | 0.316 | 0.220 | +0.096 | 0.622 | 0.826 |
| InstanceGM | SA30 | 0.337 | 0.243 | +0.095 | 0.331 | 0.699 |
| K-NET | PGA | 0.198 | 0.178 | +0.020 | 0.609 | 0.688 |

The CNN+metadata variant beats metadata-only HGB for K-NET PGA, with MAE 0.198 versus 0.217. It does not beat the HGB model that includes hand-crafted early-waveform features.

## 10 s Follow-Up

The 10 s window tests whether the 3 s CNN failed because the information window was too short.

| dataset | target | CNN+metadata MAE | HGB combined MAE | CNN-HGB MAE | CNN+metadata R2 | HGB combined R2 |
|---|---|---:|---:|---:|---:|---:|
| InstanceGM | PGA | 0.362 | 0.207 | +0.155 | 0.619 | 0.847 |
| InstanceGM | PGV | 0.351 | 0.165 | +0.187 | 0.547 | 0.863 |
| InstanceGM | SA03 | 0.321 | 0.221 | +0.100 | 0.676 | 0.834 |
| InstanceGM | SA10 | 0.330 | 0.210 | +0.120 | 0.613 | 0.827 |
| InstanceGM | SA30 | 0.351 | 0.242 | +0.109 | 0.288 | 0.680 |
| K-NET | PGA | 0.139 | 0.105 | +0.035 | 0.799 | 0.877 |

K-NET improves substantially at 10 s, from 0.198 to 0.139 MAE for CNN+metadata. The HGB combined baseline also improves, from 0.178 to 0.105. InstanceGM does not show the same CNN gain. Longer windows do not rescue the simple supervised CNN as the central method.

## Interpretation

The current learned encoder is not publication evidence for a foundation-model claim.

The result points to three concrete issues:

1. InstanceGM ground-motion targets are already well explained by metadata plus simple amplitude statistics. A small supervised CNN has not extracted stronger information from the 3 s waveform window.
2. K-NET is more favorable for the CNN. The learned model captures waveform signal, especially at 10 s, but it still trails the hand-crafted combined baseline.
3. The model is trained from scratch on 5,000 records per dataset. This is not the setting where a seismic representation model should be expected to show its main advantage.

## Decision

Decision: **continue the NC route, but do not center the manuscript on this supervised CNN.**

The paper target should remain:

**A label-aware seismic waveform representation for cross-dataset phase and ground-motion tasks.**

The current CNN trial narrows the method requirement. The learned component must use information that the simple hand-crafted baseline does not already capture. A stronger route is:

1. Pretrain the encoder on the unified waveform archive using masked reconstruction, contrastive objectives, or phase-aware self-supervision.
2. Fine-tune jointly on phase, detection, and ground-motion targets.
3. Add label-aware weighting from picker disagreement, missing-pick patterns, and high-residual waveform audits.
4. Test cross-dataset and held-event or held-station transfer, not only within-dataset random samples.
5. Compare against the current HGB combined baseline as a serious baseline, not a weak placeholder.

## Paper-Level Consequence

The NC route is still plausible because the data story and strong-motion baseline are positive:

- unified archive: 2.46 million records
- structured phase-picker failures across datasets
- early waveform features improve ground-motion prediction beyond metadata
- K-NET conversion gives an independent strong-motion dataset

The method claim is now the risk. If the next learned-representation experiment still fails to beat the HGB combined baseline or improve cross-dataset phase robustness, the paper should pivot toward:

**A cross-dataset seismic waveform benchmark and label-audit study linking phase-model failure modes to ground-motion residual structure.**

That pivot could still be publishable, but the NC case would depend more heavily on geophysical residual analysis and less on model novelty.

## Next Experiment

Run a representation experiment that is meaningfully different from the failed supervised CNN:

- Pretraining data: STEAD, InstanceGM, Iquique, K-NET waveforms
- Pretraining objective: masked waveform reconstruction or contrastive prediction across augmented windows
- Fine-tuning tasks:
  - phase picking or phase-time regression
  - detection
  - PGA/PGV/SA regression
- Evaluation:
  - InstanceGM and K-NET PGA against HGB combined baseline
  - InstanceGM PGV/SA targets against HGB combined baseline
  - phase missing rate, tail error, and calibration across STEAD, InstanceGM, Iquique, K-NET
  - event-held-out and station-held-out splits where metadata allow it

Minimum evidence for the NC method claim:

- Beat HGB combined on at least one ground-motion target, or match it while improving cross-dataset phase robustness.
- Show better calibration or lower tail risk under dataset shift.
- Produce residual improvements that can be interpreted by magnitude, distance, depth, station, or dataset.

## Commands

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/run_waveform_encoder_ground_motion.py \
  --out-dir work/waveform_encoder_ground_motion_3s_5k_pool \
  --datasets instancegm knet \
  --targets pga pgv sa03 sa10 sa30 \
  --train-size 5000 \
  --test-size 1000 \
  --early-seconds 3 \
  --epochs 30 \
  --batch-size 256 \
  --max-samples 20000

/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/run_waveform_encoder_ground_motion.py \
  --out-dir work/waveform_encoder_ground_motion_10s_5k_pool \
  --datasets instancegm knet \
  --targets pga pgv sa03 sa10 sa30 \
  --train-size 5000 \
  --test-size 1000 \
  --early-seconds 10 \
  --epochs 30 \
  --batch-size 256 \
  --max-samples 20000
```
