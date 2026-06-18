# Phase Baseline Pilot Summary

Date: 2026-06-11

## Purpose

This pilot checks that the unified manifest can feed existing SeisBench phase pickers and that prediction outputs can be compared against existing P/S labels. It is a pipeline and label-audit sanity check, not manuscript evidence.

## Inputs

- Unified manifest: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/unified_manifest/unified_manifest.csv.gz`
- Runner: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/scripts/run_phase_baseline_pilot.py`
- Python: `/Users/yojironoda/miniforge3/envs/zhy/bin/python`

## Outputs

- Two-model pilot:
  - `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/baseline_pilot/phase_baseline_pilot_predictions.csv`
  - `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/baseline_pilot/phase_baseline_pilot_summary.json`
- Four-model comparison:
  - `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/baseline_pilot_four_models/phase_baseline_pilot_predictions.csv`
  - `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/baseline_pilot_four_models/phase_baseline_pilot_summary.json`
- Worst-case waveform plots:
  - `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/baseline_worst_plots`
  - Plot script: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/scripts/plot_phase_audit_examples.py`

## Four-Model Pilot Setup

- Split: test
- Datasets: STEAD, InstanceGM, Iquique, K-NET
- Records: 20 per dataset, 80 total
- Models: PhaseNet(STEAD), EQTransformer(STEAD), PhaseNet(INSTANCE), EQTransformer(INSTANCE)
- Sample-length filter: 6,000 to 20,000 samples
- Thresholds: P 0.1, S 0.1, EQTransformer detection 0.1
- Failures: 0

## Summary Table

| model | dataset | P matched | P MAE s | P missing | S matched | S MAE s | S missing |
|---|---:|---:|---:|---:|---:|---:|---:|
| phasenet_stead | stead | 20 | 0.025 | 0 | 20 | 0.154 | 0 |
| eqtransformer_stead | stead | 17 | 0.030 | 3 | 20 | 0.177 | 0 |
| phasenet_instance | stead | 16 | 0.058 | 4 | 17 | 0.092 | 3 |
| eqtransformer_instance | stead | 15 | 0.033 | 5 | 17 | 0.075 | 3 |
| phasenet_stead | instancegm | 17 | 0.108 | 3 | 11 | 0.115 | 9 |
| eqtransformer_stead | instancegm | 14 | 0.141 | 6 | 10 | 0.059 | 10 |
| phasenet_instance | instancegm | 19 | 0.262 | 1 | 11 | 0.055 | 9 |
| eqtransformer_instance | instancegm | 18 | 0.242 | 2 | 11 | 0.067 | 9 |
| phasenet_stead | iquique | 20 | 0.147 | 0 | 18 | 0.326 | 2 |
| eqtransformer_stead | iquique | 20 | 0.165 | 0 | 18 | 0.304 | 2 |
| phasenet_instance | iquique | 20 | 0.152 | 0 | 18 | 0.320 | 2 |
| eqtransformer_instance | iquique | 20 | 0.149 | 0 | 18 | 0.282 | 2 |
| phasenet_stead | knet | 19 | 0.054 | 1 | 20 | 0.440 | 0 |
| eqtransformer_stead | knet | 17 | 0.052 | 3 | 20 | 0.417 | 0 |
| phasenet_instance | knet | 19 | 0.048 | 1 | 20 | 0.455 | 0 |
| eqtransformer_instance | knet | 17 | 0.033 | 3 | 20 | 0.423 | 0 |

## Early Observations

P picks are stable across this small sample, including K-NET. K-NET S picks show larger offsets, around 0.4 s MAE in this pilot, even when using INSTANCE-pretrained models.

InstanceGM has many missing S predictions in this small pilot. This may reflect model thresholds, signal characteristics, label conventions, or waveform units. It should be treated as a label-audit question rather than a performance conclusion.

Iquique P picks are recovered reliably in the pilot, while S picks show larger scatter and two missing predictions per model.

The INSTANCE-pretrained models do not simply dominate the STEAD-pretrained models in this sample. That supports evaluating dataset/domain effects explicitly instead of assuming one pretrained weight is universally better.

## Worst-Case Records to Inspect

Largest P errors in the pilot include:

- Iquique `bucket11$600,:3,:16830`, PhaseNet(STEAD), P error 0.73 s
- InstanceGM `bucket458$365,:3,:12000`, PhaseNet(STEAD), P error 0.63 s
- Iquique `bucket4$763,:3,:15978`, EQTransformer(STEAD), P error 0.55 s

Largest S errors include:

- STEAD `bucket279$794,:3,:6000`, EQTransformer(STEAD), S error 1.48 s
- Iquique `bucket2$490,:3,:15441`, EQTransformer(STEAD), S error 1.42 s
- Iquique `bucket2$490,:3,:15441`, PhaseNet(STEAD), S error 1.32 s
- K-NET `KYT0070602181621`, PhaseNet(STEAD), S error 0.96 s
- K-NET `IBR0150507231635`, EQTransformer(STEAD), S error 0.95 s

These records are candidates for waveform visualization and label-quality review.

The first six high-residual waveform plots were generated:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/baseline_worst_plots/instancegm_bucket491_546_3_12000.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/baseline_worst_plots/iquique_bucket2_490_3_15441.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/baseline_worst_plots/stead_bucket279_794_3_6000.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/baseline_worst_plots/knet_KYT0070602181621.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/baseline_worst_plots/iquique_bucket7_778_3_15961.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/baseline_worst_plots/stead_bucket1117_320_3_6000.png`

## Commands

Two-model pilot:

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/run_phase_baseline_pilot.py \
  --per-dataset 20 \
  --min-samples 6000 \
  --max-samples 20000 \
  --models phasenet_stead eqtransformer_stead
```

Four-model comparison:

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/run_phase_baseline_pilot.py \
  --out-dir work/baseline_pilot_four_models \
  --per-dataset 20 \
  --min-samples 6000 \
  --max-samples 20000 \
  --models phasenet_stead eqtransformer_stead phasenet_instance eqtransformer_instance
```

## Next Step

Create waveform plots for the worst-case records with:

- ZNE waveforms
- catalog P/S labels
- PhaseNet and EQTransformer picks
- confidence values

This will distinguish genuine label issues from model-domain failures.
