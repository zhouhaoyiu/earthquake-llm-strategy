# Earthquake LLM/Foundation Model Data Audit and Strategy

Date: 2026-06-11
Workspace: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy`

## Scope Checked

- SeisBench cache: `/Users/yojironoda/.seisbench`
- Downloaded K-NET package: `/Users/yojironoda/Downloads/s7rk7bj3zn-1`
- Python environment: `/Users/yojironoda/miniforge3/envs/zhy/bin/python`

No files under `/Users/yojironoda/Desktop/simple` were inspected.

## Local Compute

- Machine: MacBook Pro, Apple M4 Max
- CPU cores: 14
- GPU cores: 32, Metal/MPS available through PyTorch
- Memory: 36 GB
- Disk free: about 240 GiB on the data volume during inspection
- `zhy` environment: `seisbench`, `obspy`, `torch`, `h5py`, `numpy`, `pandas`, and `sklearn` are available
- PyTorch: 2.5.1, MPS available, CUDA unavailable

This is suitable for dataset conversion, strong baselines, compact self-supervised pretraining, transfer learning, and ablation studies. It is not suitable for training a large foundation model from scratch without aggressive sampling and model-size control.

## Confirmed SeisBench Cache

Total cache size: about 247 GB.

| Dataset | Disk size | SeisBench length | Metadata rows | Waveform format | Main value |
|---|---:|---:|---:|---|---|
| STEAD | 85 GB | 1,265,657 | 1,265,657 | 3 component, 6000 samples, 100 Hz, float32 | Large-scale phase picking and event/noise representation learning |
| InstanceGM | 157 GB | 1,159,249 | 1,159,249 | 3 component, 12000 samples, float32 | Strong-motion prediction, PGA/PGV/SA targets, engineering metrics |
| Iquique | 5 GB | 13,400 | 13,400 | 3 component, about 16k samples, float64 | Regional transfer, temporal split, aftershock/sequence-style validation |

STEAD full metadata:

- Split: train 1,075,808; test 126,566; dev 63,283
- Categories: earthquake_local 1,030,231; noise 235,426
- P and S picks: 1,030,231 records each
- Magnitude range in labeled earthquake records: -0.5 to 7.9

InstanceGM full metadata:

- Split: train 699,980; test 344,242; dev 115,027
- P arrivals: 1,159,249 records
- S arrivals: 713,883 records
- PGA/PGV/SA fields are broadly populated
- Magnitude range: 0.0 to 6.5

Iquique full metadata:

- Split: train 8,040; test 4,020; dev 1,340
- P arrivals: 13,327 records
- S arrivals: 11,361 records

Cached SeisBench models:

- EQTransformer: STEAD and INSTANCE variants
- PhaseNet: STEAD and INSTANCE variants
- GPD: INSTANCE variant

These provide immediate baselines for phase picking and cross-dataset transfer tests.

## Downloaded K-NET Package

Current stable content:

- `/Users/yojironoda/Downloads/s7rk7bj3zn-1/knet_1530/header.bson`
- `/Users/yojironoda/Downloads/s7rk7bj3zn-1/knet_1530/accelerogram.bson`
- metadata JSON files for both BSON collections

Zip listing confirms the package contains these four files only.

Header BSON sample statistics:

- Records: 22,119
- Events: 1,528
- Stations: 921
- Years: 1997-2006
- Magnitude range: 2.8 to 8.0
- P labels: 21,141 records
- S labels: 22,119 records

Current note: earlier shell output briefly showed converted folders under this path, including `stead_converted` and `knet_1530/converted`, but the stable current directory state only contains the raw BSON package. Any converted-manifest result should be regenerated before being treated as evidence.

## Research Opportunity Assessment

The strongest local-data opportunity is not "accurate earthquake prediction." The defensible direction is a waveform foundation model or multimodal seismic representation model evaluated on phase picking, event/noise discrimination, cross-region transfer, strong-motion targets, and out-of-domain robustness.

### Track A: Foundation Representation for Seismic Waveforms

Use STEAD for large-scale self-supervised pretraining, then evaluate on:

- STEAD phase picking and event/noise detection
- Iquique regional transfer
- K-NET P/S labels after conversion
- InstanceGM strong-motion targets

Scientific claim level: method and representation learning contribution. This is feasible locally if the model is compact and experiments are carefully controlled.

Target journals after strong evidence: Nature Communications, Science Advances, possibly Nature Machine Intelligence depending on novelty and validation breadth. Nature/Science main journal would require a clear scientific discovery, not only a better model.

### Track B: Physics-Aware Strong-Motion Model

Use InstanceGM and K-NET to predict or condition PGA, PGV, and spectral acceleration with waveform encoders plus source, path, and site metadata. The key scientific angle is whether learned representations separate source, path, and site effects under cross-region tests.

Scientific claim level: engineering seismology and hazard-relevant modeling. This may be stronger than phase picking alone because it connects to ground-motion physics and practical hazard metrics.

Target journals after strong evidence: Nature Communications, Science Advances, Earthquake Engineering journals, possibly Nature Geoscience only if the model yields interpretable geophysical insight across regions.

### Track C: Cross-Dataset Generalization Benchmark

Build a benchmark spanning STEAD, InstanceGM, Iquique, and K-NET:

- Same backbone
- Same preprocessing contract
- Leave-region/dataset-out tests
- Phase picking, detection, and strong-motion heads
- Calibration and uncertainty metrics

Scientific claim level: reproducible benchmark and generalization study. This is publishable if the benchmark reveals failure modes in current models and shows a principled fix.

Target journals after strong evidence: Science Advances or Nature Communications are more realistic than Nature/Science.

## Immediate Next Steps

1. Regenerate K-NET converted manifests and waveform arrays from the raw BSON files in a reproducible script.
2. Create a unified manifest schema for STEAD, InstanceGM, Iquique, and K-NET.
3. Run cached PhaseNet/EQTransformer/GPD baselines before adding a new model.
4. Train a compact self-supervised waveform encoder on STEAD plus InstanceGM.
5. Evaluate transfer in this order: STEAD internal split, Iquique transfer, K-NET transfer, InstanceGM engineering targets.
6. Report calibration, uncertainty, and cross-domain degradation, not only accuracy.

## Integrity Boundary

At this stage, the confirmed evidence is local data availability and environment readiness. There is not yet evidence of a new scientific discovery or top-journal-level performance. Any manuscript claim must wait for reproducible baselines, statistically sound comparisons, and held-out cross-domain validation.
