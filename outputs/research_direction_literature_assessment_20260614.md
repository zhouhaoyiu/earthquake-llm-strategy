# Research Direction Assessment: Seismic Foundation Models and Ground-Motion Tasks

Date: 2026-06-14

## Bottom Line

The direction is still worth doing, but the paper target should be narrowed.

The broad claim "LLM/foundation models for earthquake modeling" is no longer novel enough. Seismic foundation-model papers already exist, and Nature-family earthquake-AI papers have moved toward operational or hazard-relevant tasks: real-time earthquake early warning, wavefield forecasting, multi-station monitoring, and ground-motion generation.

The strongest current route for this project is:

**A cross-dataset seismic waveform benchmark linking phase-picker transfer failures, early-window strong-motion information, and interpretable ground-motion residual structure.**

This route can support a Nature Communications submission if the empirical package becomes larger and cleaner. It should not be presented as earthquake prediction, and it should not claim foundation-model superiority until a learned representation beats strong baselines under held-event, held-station, or cross-dataset evaluation.

## What The Literature Says

### 1. Seismic ML infrastructure is mature

SeisBench exists specifically to standardize seismic ML datasets, pretrained models, data access, and model comparison. This means a paper cannot be novel just because it combines existing waveform datasets or runs existing pickers.

Source: https://arxiv.org/abs/2111.00786

STEAD and INSTANCE are already large, ML-oriented seismic archives. STEAD provides large three-component waveform data for AI, and INSTANCE provides nearly 1.2 million three-component traces from about 50,000 earthquakes plus noise records and metadata. K-NET/KiK-net is an official strong-motion network with about 1,700 Japanese stations and strong-motion records designed to avoid saturation in damaging shaking.

Sources:

- https://github.com/smousavi05/STEAD
- https://essd.copernicus.org/articles/13/5509/2021/
- https://www.kyoshin.bosai.go.jp/en/

Project consequence:

Use the unified local archive as infrastructure for a scientific audit, not as the paper's main novelty.

### 2. Phase picking is crowded

PhaseNet showed that U-Net style models can pick P and S arrivals from three-component waveforms with high accuracy. EQTransformer extended the task to simultaneous detection and phase picking and was published in Nature Communications.

Sources:

- PhaseNet: https://academic.oup.com/gji/article/216/1/261/5129142
- EQTransformer: https://www.nature.com/articles/s41467-020-17591-w

Project consequence:

A phase-picking paper alone is too weak for NC unless it exposes a new cross-dataset failure mode with clear scientific or operational consequences. Our local phase baseline is useful as an audit layer, not as the whole manuscript.

### 3. Foundation-model language has already entered seismology

SeisLM pretrains a seismic waveform foundation model using a self-supervised contrastive objective and reports downstream performance on detection, phase picking, onset regression, and foreshock-aftershock classification.

SeisCLIP uses multimodal contrastive learning between seismic spectra and event information for event classification, location, and focal mechanism tasks.

U-Trans uses self-supervised reconstruction of corrupted waveforms in time and frequency domains and reports gains across earthquake monitoring tasks.

Sources:

- SeisLM: https://arxiv.org/abs/2410.15765
- SeisCLIP: https://arxiv.org/abs/2309.02320
- U-Trans: https://www.nature.com/articles/s41598-026-41454-x

Project consequence:

Do not title the paper as simply "a seismic foundation model." The stronger angle is label-aware, task-aware, and hazard-linked evaluation. A foundation-model component only helps if it improves robustness, calibration, or residual interpretability against serious baselines.

### 4. Nature-family papers reward hazard relevance and system-level validation

Recent Nature-family examples show the level of framing needed:

- EQTransformer: global detection and phase picking with continuous waveform application.
- PLAN: multi-station, multi-task phase picking, association, and location with physical consistency.
- Universal neural networks for EEW: models applied across Japan and California, reporting early location and magnitude estimates within seconds of P arrival.
- WaveCastNet: real-time wavefield forecasting for EEW, with synthetic-to-real validation and rare-event generalization.
- CGM-GM: conditional generative modeling for ground motions, Fourier amplitude spectra, arrivals, durations, and spatially continuous ground-motion behavior.

Sources:

- EQTransformer: https://www.nature.com/articles/s41467-020-17591-w
- PLAN: https://www.nature.com/articles/s43247-023-01188-4
- Universal EEW: https://www.nature.com/articles/s43247-024-01718-8
- WaveCastNet: https://www.nature.com/articles/s41467-025-65435-2
- CGM-GM: https://www.nature.com/articles/s41467-026-70719-2

Project consequence:

NC is realistic only if the paper is hazard-relevant, cross-dataset, and reproducible. A small neural architecture improvement is not enough.

### 5. Ground-motion residuals are a live scientific target

Non-ergodic ground-motion models explicitly model repeatable source, path, and site effects. Recent work uses conditional generative models or scalable Gaussian processes to model spatially varying path/site effects and reduce dependence on simple ergodic assumptions.

Sources:

- CGM-FAS / non-ergodic path effects: https://arxiv.org/abs/2512.19909
- Scalable GP non-ergodic GMM: https://arxiv.org/html/2605.24284v1

Project consequence:

Our residual-audit result is not a side plot. It is one of the more publishable parts: early waveform features reduce mean and tail errors, while remaining residuals expose distance-dependent K-NET PGA tails and repeated InstanceGM outliers.

## Fit With Our Current Evidence

Confirmed local positives:

- Unified manifest across STEAD, InstanceGM, Iquique, and K-NET has about 2.46 million records.
- K-NET conversion gives 22,119 complete Z/N/E strong-motion records.
- Existing phase models run across datasets and show structured transfer issues, especially for S phases.
- Strong-motion HGB baselines show that early post-P waveform windows improve log10 PGA/PGV/SA prediction beyond metadata.
- The 10 s metadata + early-waveform baseline reduces MAE by 30.6% for InstanceGM PGA, 44.7% for InstanceGM PGV, and 51.8% for K-NET PGA.
- The same 10 s baseline reduces q95 tail error across all tested targets.

Current negatives:

- Simple supervised CNN does not beat HGB with hand-crafted early-window features.
- Naive masked waveform reconstruction pretraining does not improve ground-motion downstream performance.
- We do not yet have a foundation-model result that can be claimed as a method contribution.

Interpretation:

The current evidence supports an NC benchmark-and-residual-science route. It does not yet support an NC foundation-model-method route.

## Recommended NC Story

Working title:

**Cross-dataset seismic waveform learning reveals phase-label transfer failures and early strong-motion information**

Central claim:

Public seismic waveform archives contain reusable early waveform information for hazard-relevant ground-motion tasks, but pretrained phase models and labels fail in structured ways across weak-motion, strong-motion, and regional datasets. A cross-dataset audit can quantify these failures and expose residual source-path-site structure that standard metadata baselines miss.

Core figures:

1. Dataset map and task matrix: STEAD, InstanceGM, Iquique, K-NET; phase, detection, PGA/PGV/SA.
2. Phase baseline transfer heatmap: P/S error and missing-pick rate by dataset.
3. Early-window ground-motion gains: 1 s, 3 s, 10 s windows; metadata-only versus metadata + waveform.
4. Residual diagnostics: K-NET distance-tail, InstanceGM repeated outliers, signed/absolute residual structure.
5. Waveform audit panels for selected residual cases.

Optional method figure:

Add a label-aware or contrastive representation only if it beats HGB in a scientifically meaningful split.

## What Would Make It NC-Ready

Minimum empirical package:

1. Scale phase baseline beyond the pilot sample, ideally 5,000 records per dataset or full feasible test sets.
2. Add event-held-out and station-held-out splits for ground-motion tasks.
3. Repeat residual analysis for 1 s, 3 s, and 10 s windows.
4. Add uncertainty or calibration metrics, not only MAE/R2.
5. Verify K-NET units and metadata definitions from official documentation before manuscript use.
6. Add a serious classical GMM or non-ergodic reference where feasible, at least for PGA/PGV comparison.
7. Make the data-processing and split definitions fully reproducible.

Method route requirement:

A learned representation must improve at least one of these:

- held-event or held-station generalization;
- cross-dataset transfer;
- calibration or tail error;
- residual interpretability;
- performance under limited labels.

Without that, the paper should not claim a new foundation model.

## Journal Judgment

Nature / Science main journals:

Not supported by current evidence. That level would require a broad scientific discovery, operational-scale validation, or a new observation about earthquake physics or hazard systems.

Science Advances:

Possible only after stronger method evidence or a broader cross-region result. The current pilot package is not enough.

Nature Geoscience:

Possible only if residual structure leads to a real geoscience insight about source, path, site, or regional wave propagation. A machine-learning benchmark alone is unlikely to fit.

Nature Communications:

The most realistic top target. The paper must be framed as cross-dataset seismic waveform learning with hazard relevance and reproducible residual science.

Communications Earth & Environment / Scientific Reports / Seismica / SRL:

Good backup targets if the final contribution remains mainly benchmark/audit rather than a new robust method.

## Recommended Next Step

Run the safest next experiment:

**Repeat the residual analysis for 1 s and 3 s windows, then build a single combined figure showing how residual structure changes as the early waveform window grows.**

This directly strengthens the NC story because it turns the current baseline into a lead-time-dependent physical diagnostic. It also avoids spending more compute on a weak representation objective before the paper's empirical spine is complete.

After that, test one targeted representation:

**Event/station contrastive pretraining with amplitude-preserving waveform inputs and phase-aware labels.**

Do not repeat raw masked reconstruction unless the objective is changed.

## Claims To Avoid

- "Earthquake prediction."
- "Foundation model solves seismic monitoring."
- "LLM understands earthquakes."
- "Operational EEW performance."
- "General ground-motion generation."
- "Physical causality from residual correlations."

Use proportional wording:

- "early waveform information improves hazard-relevant ground-motion inference in these datasets";
- "phase-model errors are structured under dataset shift";
- "residual tails identify audit targets consistent with source-path-site or label-quality effects";
- "learned representations remain a hypothesis until they beat strong baselines under robust splits."
