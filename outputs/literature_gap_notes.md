# Literature Gap Notes for SA/NC Direction

Date: 2026-06-11

## Sources Checked

Primary and near-primary sources checked in this pass:

- SeisLM: https://arxiv.org/abs/2410.15765
- SeisMoLLM: https://arxiv.org/abs/2502.19960
- U-Trans: https://www.nature.com/articles/s41598-026-41454-x
- WaveCastNet: https://www.nature.com/articles/s41467-025-65435-2
- Conditional Generative Modeling for Ground Motion: https://www.nature.com/articles/s41467-026-70719-2
- SeisBench: https://arxiv.org/abs/2111.00786
- INSTANCE: https://essd.copernicus.org/articles/13/5509/2021/
- Label-error study: https://arxiv.org/html/2511.09805v1
- Earthquake Transformer: https://www.nature.com/articles/s41467-020-17591-w

## What the Field Already Has

### 1. Single-station waveform foundation models

SeisLM is the direct competitor. It frames seismic waveforms through self-supervised learning, using a transformer architecture related to Wav2Vec2 and BERT. It reports transfer to event detection, phase picking, onset regression, and foreshock-aftershock classification.

Implication for this project:

Do not claim novelty from "a seismic waveform foundation model" alone. That space is already occupied.

### 2. LLM transfer through waveform tokenization

SeisMoLLM uses waveform tokenization and GPT-2 fine-tuning, with reported results on DiTing and STEAD across back-azimuth, distance, magnitude, phase picking, and first-motion polarity.

Implication for this project:

Using GPT-style language models on tokenized waveforms is no longer a fresh claim. A paper must show why LLM transfer changes the science or produces robust cross-domain behavior.

### 3. Self-supervised reconstruction encoders

U-Trans combines STEAD, TXED, and INSTANCE at about 2.5 million three-component seismograms. It uses corrupted waveform reconstruction, then fine-tunes on downstream earthquake tasks.

Implication for this project:

Self-supervised reconstruction is a baseline, not the central novelty. If used, it needs stronger evaluation and interpretation than task accuracy.

### 4. NC-level ground-motion AI papers

WaveCastNet in Nature Communications forecasts seismic wavefields for earthquake early warning using a sequence-to-sequence framework. It emphasizes real-time forecasting, synthetic-to-real transfer, sparse sensor inputs, uncertainty, and regional wave propagation.

The 2026 Nature Communications ground-motion generative model uses conditional generative modeling for Fourier amplitude spectra and waveform properties, framed around hazard assessment and infrastructure resilience.

Implication for this project:

NC has already accepted AI earthquake papers when they connect to hazard-relevant ground motion, uncertainty, sparse observations, and regional generalization. A phase-picking-only paper would be weak for this target.

### 5. Dataset and benchmark infrastructure

SeisBench already provides a standardized ML framework and public datasets. STEAD and INSTANCE are well-known, large, and heavily used.

Implication for this project:

A new benchmark must add something beyond joining existing datasets. Strong candidates are cross-task transfer, data-quality auditing, physically interpretable residuals, and strong-motion linkage.

### 6. Label quality is now a live issue

Recent work on seismological ML datasets emphasizes label errors and uses model ensembles such as PhaseNet and EQTransformer to flag questionable labels across STEAD, Iquique, INSTANCE, and related datasets.

Implication for this project:

A serious paper should include label-quality auditing. This can become a strength: models that handle noisy labels and report uncertainty are more credible than models that only report best-case scores.

## Best Research Gap

The strongest gap for this local project is:

**A label-aware, cross-task seismic foundation representation that transfers from weak-motion phase information to strong-motion hazard metrics, with physically interpretable source-path-site residuals.**

This gap is attractive because it combines three things current papers usually separate:

- phase picking and event detection
- strong-motion prediction
- dataset quality and cross-domain uncertainty

## Proposed Core Hypotheses

Hypothesis 1:

Self-supervised pretraining on mixed weak-motion and strong-motion archives improves out-of-domain transfer for phase picking and event detection under dataset, network, and region shifts.

Hypothesis 2:

A waveform representation trained across STEAD, InstanceGM, Iquique, and K-NET contains information useful for PGA, PGV, and spectral acceleration prediction after controlling for magnitude, distance, and site proxies.

Hypothesis 3:

Label-aware training and ensemble-based label auditing improve calibration and reduce failure rates in cross-dataset tests.

Hypothesis 4:

The learned embedding organizes residuals by physically meaningful variables such as magnitude, hypocentral distance, source depth, station/network identity, and site proxies.

## NC Manuscript Shape

Suggested title:

**A label-aware seismic foundation representation for cross-dataset phase and ground-motion tasks**

Main message:

Public seismic archives can support a compact, reproducible waveform foundation representation when data quality, cross-dataset transfer, and hazard-relevant strong-motion targets are evaluated together.

What must be shown:

- K-NET conversion is reproducible.
- Baselines include PhaseNet, EQTransformer, GPD, and compact neural baselines.
- The proposed model improves transfer or calibration on at least two independent held-out datasets.
- Strong-motion results include residual analysis against source, path, and site variables.
- Label-quality auditing changes either training weights, confidence calibration, or error interpretation.

Why this fits NC:

It is a clear Earth-science and hazard-relevant contribution. The paper can be important to seismology specialists even if it does not claim a universal earthquake predictor.

## SA Upgrade Path

To justify Science Advances, the paper needs a broader result:

**Weak-motion representations learned at scale reveal transferable physical structure that improves hazard-relevant strong-motion inference across networks.**

Extra evidence needed:

- Leave-region-out or leave-network-out results that are strong enough to change the main conclusion.
- Embedding analyses that align with accepted physical variables.
- Robust uncertainty estimates under distribution shift.
- Demonstration that the model helps when labels are sparse or noisy.

Without this extra layer, SA will likely read the work as a strong ML-seismology paper with narrower audience.

## What Not To Claim

Do not claim earthquake prediction.

Do not claim a general seismic foundation model unless the model is evaluated across tasks and datasets.

Do not claim physical discovery from embedding plots alone.

Do not claim operational early warning readiness from offline benchmarks.

Do not claim superiority over WaveCastNet-style wavefield forecasting or conditional ground-motion generation unless a direct comparable experiment exists.

## Differentiation From Existing Papers

Against SeisLM:

- Add strong-motion targets and source-path-site residual analysis.
- Add label-quality auditing.
- Add K-NET external validation.

Against SeisMoLLM:

- Avoid making GPT transfer the main novelty.
- Emphasize seismic-domain evidence, calibration, and physical interpretation.

Against U-Trans:

- Use reconstruction as one baseline.
- Focus on cross-task transfer and strong-motion metrics.

Against WaveCastNet:

- Do not compete on dense wavefield forecasting.
- Position this project around station waveform archives, public datasets, and transfer to engineering metrics.

Against conditional ground-motion generation:

- Do not compete on generating full future earthquake ground motions.
- Position this project around representation learning and interpretable transfer from observed records.

## Next Experiment To Run First

Run a small, publishable pilot:

1. Convert K-NET BSON into a stable manifest and waveform store.
2. Create a unified manifest for STEAD, InstanceGM, Iquique, and K-NET.
3. Run PhaseNet and EQTransformer as label-audit models on subsets.
4. Train a compact masked-autoencoder or contrastive waveform encoder on STEAD plus InstanceGM samples.
5. Fine-tune on:
   - STEAD phase picking
   - Iquique phase picking
   - K-NET phase picking
   - InstanceGM PGA/PGV/SA
6. Report:
   - in-domain scores
   - cross-domain degradation
   - confidence calibration
   - residuals by magnitude, distance, depth, station, and network

This pilot decides whether the NC route is real. The SA route should wait for evidence from this pilot.
