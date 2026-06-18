# Go/No-Go Trial: 200 Records per Dataset

Date: 2026-06-12

## Purpose

This trial tests whether the project has a real empirical signal beyond a small smoke test. It is still not manuscript evidence. The goal is to decide whether the direction is worth scaling.

## Setup

- Manifest: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/unified_manifest/unified_manifest.csv.gz`
- Runner: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/scripts/run_phase_baseline_pilot.py`
- Output directory: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/baseline_pilot_200_stead_models`
- Datasets: STEAD, InstanceGM, Iquique, K-NET
- Split: test
- Sample: 200 records per dataset, 800 records total
- Models: PhaseNet(STEAD), EQTransformer(STEAD)
- Sample-length filter: 6,000 to 20,000 samples
- Model-record predictions: 1,600
- Runtime: feasible on local M4 Max
- Failures: 0

## Main Metrics

| model | dataset | phase | matched | missing | missing rate | median signed error s | MAE s | q95 abs error s | >2 s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phasenet_stead | STEAD | P | 200 | 0 | 0.000 | -0.010 | 0.028 | 0.080 | 0 |
| phasenet_stead | STEAD | S | 200 | 0 | 0.000 | -0.010 | 0.082 | 0.263 | 0 |
| eqtransformer_stead | STEAD | P | 175 | 25 | 0.125 | -0.010 | 0.286 | 0.116 | 1 |
| eqtransformer_stead | STEAD | S | 199 | 1 | 0.005 | -0.010 | 0.088 | 0.295 | 0 |
| phasenet_stead | InstanceGM | P | 169 | 31 | 0.155 | -0.020 | 0.989 | 0.726 | 5 |
| phasenet_stead | InstanceGM | S | 113 | 87 | 0.435 | 0.020 | 0.307 | 0.984 | 1 |
| eqtransformer_stead | InstanceGM | P | 156 | 44 | 0.220 | -0.040 | 1.332 | 1.995 | 8 |
| eqtransformer_stead | InstanceGM | S | 102 | 98 | 0.490 | 0.020 | 1.543 | 1.619 | 4 |
| phasenet_stead | Iquique | P | 198 | 2 | 0.010 | -0.090 | 0.170 | 0.579 | 0 |
| phasenet_stead | Iquique | S | 162 | 38 | 0.190 | -0.095 | 0.304 | 1.058 | 1 |
| eqtransformer_stead | Iquique | P | 194 | 6 | 0.030 | -0.100 | 0.177 | 0.557 | 0 |
| eqtransformer_stead | Iquique | S | 163 | 37 | 0.185 | -0.130 | 0.328 | 1.236 | 1 |
| phasenet_stead | K-NET | P | 192 | 8 | 0.040 | -0.030 | 0.062 | 0.160 | 0 |
| phasenet_stead | K-NET | S | 200 | 0 | 0.000 | -0.050 | 0.318 | 0.961 | 3 |
| eqtransformer_stead | K-NET | P | 173 | 27 | 0.135 | -0.010 | 0.547 | 0.168 | 1 |
| eqtransformer_stead | K-NET | S | 200 | 0 | 0.000 | -0.045 | 0.318 | 0.940 | 3 |

## Interpretation

The project is feasible enough to continue. The engineering pipeline works across four datasets, and the model failures are structured rather than random.

The strongest positive signal is not a new high-accuracy picker. The signal is cross-dataset behavior:

- STEAD is easy for PhaseNet(STEAD), as expected.
- K-NET P picks are strong with PhaseNet(STEAD), despite being converted from raw BSON.
- K-NET S picks are always detected in this sample but have a wider residual tail.
- Iquique P picks are reliable; Iquique S picks show more missing predictions and larger scatter.
- InstanceGM is the hardest dataset: many missing S predictions and several extreme P/S mismatches.

This supports a label/domain audit direction. It does not support a claim that a generic foundation model already solves seismic picking.

## What This Means for the Paper Direction

Proceed with the project only if the next stage is framed as:

**cross-dataset seismic representation, label quality, uncertainty, and strong-motion transfer.**

Do not frame it as:

**LLM earthquake prediction** or **another phase picker with slightly better accuracy**.

The current evidence points to a real research problem: existing pretrained pickers behave differently across weak-motion, strong-motion, regional, and converted K-NET records. That behavior can be studied and improved with label-aware and physics-aware representation learning.

## High-Residual Examples

Generated review plots:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/baseline_200_worst_plots/knet_OKY0020010082051.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/baseline_200_worst_plots/instancegm_bucket800_256_3_12000.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/baseline_200_worst_plots/instancegm_bucket1037_871_3_12000.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/baseline_200_worst_plots/stead_bucket529_404_3_6000.png`

The K-NET worst P example appears to be an EQTransformer late false pick; PhaseNet picks the early P correctly. This suggests model/post-processing failure rather than unusable K-NET labels.

The InstanceGM extreme example shows late high-energy arrivals in a long, low-magnitude waveform. This supports explicit long-window and low-SNR failure analysis.

## Go/No-Go Decision

Decision: **Go, but narrow the claim.**

Continue if the next stage is:

1. scale baseline to 1,000-5,000 records per dataset;
2. add confidence calibration and missing-pick analysis;
3. inspect high-residual records by dataset and event;
4. add ground-motion baselines for InstanceGM and K-NET;
5. evaluate whether waveform representations improve strong-motion prediction or calibration.

Stop or downgrade if:

- failures reduce to ordinary phase-picking tuning;
- strong-motion prediction shows no waveform contribution beyond metadata;
- label/domain analysis does not reveal a reproducible pattern.

## Command

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/run_phase_baseline_pilot.py \
  --out-dir work/baseline_pilot_200_stead_models \
  --per-dataset 200 \
  --min-samples 6000 \
  --max-samples 20000 \
  --models phasenet_stead eqtransformer_stead
```
