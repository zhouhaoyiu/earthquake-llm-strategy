# NC Framing: Cross-Dataset Strong-Motion Early-Window Information and Residual Audit

Date: 2026-06-14

## Working Direction

This project should be written as a cross-dataset strong-motion study centered on early post-P waveform information and residual auditing.

Recommended working title:

**Cross-dataset early waveform information and residual auditing for strong-motion inference**

Alternative titles:

1. **Early waveform constraints on strong-motion residuals across seismic datasets**
2. **Lead-time-dependent strong-motion information in cross-dataset seismic waveforms**
3. **A cross-dataset audit of early strong-motion information and residual structure**

## Central Question

How much hazard-relevant strong-motion information is present in the first seconds after the P arrival, and what residual structure remains after that information is added to source-path-site metadata?

This question links three parts of the current project:

1. a unified waveform-task archive spanning weak-motion, regional, and strong-motion datasets;
2. early-window ground-motion inference for PGA, PGV, and spectral acceleration;
3. residual auditing by distance, magnitude, depth, station metadata, waveform amplitude, and high-residual records.

## Draft Abstract

Rapid hazard assessment depends on information available within the first seconds of an earthquake waveform. Public seismic archives contain millions of labeled waveforms, yet the transferability of early waveform information across weak-motion and strong-motion datasets remains poorly constrained. We assemble a unified benchmark from STEAD, InstanceGM, Iquique, and K-NET, then evaluate early post-P waveform windows for strong-motion inference and residual auditing. Existing phase-picking models provide a label-audit layer across datasets, with stable P picks and dataset-dependent S-phase degradation. For ground-motion targets, adding early waveform features to source-path-site metadata improves log10 prediction errors across InstanceGM PGA, PGV, SA03, SA10, SA30, and K-NET PGA. The gain appears at 1 s after P arrival and increases for several targets at 3 s and 10 s. At 10 s, metadata plus early waveform features reduce MAE by 30.6% for InstanceGM PGA, 44.7% for InstanceGM PGV, and 51.8% for K-NET PGA. Residual audits show near-zero median bias after waveform features, persistent K-NET distance-dependent PGA tails, and repeated InstanceGM high-residual records across multiple targets. These results establish a reproducible cross-dataset framework for early strong-motion information and residual diagnostics.

## Main Claim

Early post-P waveform windows carry measurable, hazard-relevant information beyond standard metadata across independent strong-motion datasets. The remaining residuals are structured enough to support targeted audit of path effects, label quality, and rare waveform-target combinations.

The manuscript should make three claims:

1. Early waveform information improves strong-motion inference across datasets and targets.
2. The gain is lead-time dependent and visible from the first second after P arrival.
3. Residual auditing reveals remaining structure after the model absorbs first-order source-path-site and waveform-amplitude information.

## Claims Currently Supported

Supported by current results:

- The unified archive contains about 2.46 million records across STEAD, InstanceGM, Iquique, and K-NET.
- K-NET conversion provides 22,119 complete Z/N/E strong-motion records.
- Phase baseline pilots run successfully across datasets and expose S-phase transfer issues.
- Early waveform features improve metadata-only HGB baselines at 1 s, 3 s, and 10 s post-P windows.
- The improvement holds for InstanceGM PGA, PGV, SA03, SA10, SA30, and K-NET PGA.
- K-NET PGA shows the strongest window dependence, with MAE reduction rising from 9.4% at 1 s to 51.8% at 10 s.
- InstanceGM PGV shows strong and consistent gains, with MAE reduction rising from 28.1% at 1 s to 44.7% at 10 s.
- Median signed residuals remain near zero after adding early waveform features.
- K-NET retains a distance-dependent PGA residual tail.
- InstanceGM contains repeated high-residual records across multiple targets.

Claims that need more evidence:

- Generalization under held-event and held-station splits.
- Comparison against a classical or non-ergodic ground-motion model.
- Operational early-warning value.
- Superiority of a learned waveform representation.
- Physical interpretation of residuals as source, path, or site effects.

## Figure Plan

### Figure 1: Cross-Dataset Benchmark

Purpose:

Show the archive, datasets, tasks, labels, and waveform windows.

Panels:

- dataset-task matrix for STEAD, InstanceGM, Iquique, and K-NET;
- record counts and available labels;
- P-aligned early windows at 1 s, 3 s, and 10 s;
- targets: phase labels, PGA, PGV, SA03, SA10, SA30.

Message:

The study uses public waveform archives as a cross-task benchmark linking phase labels and strong-motion targets.

### Figure 2: Early-Window Ground-Motion Information

Purpose:

Quantify how much early waveform information improves prediction over metadata.

Panels:

- MAE reduction by window and target;
- q95 residual reduction by window and target;
- combined model MAE by window;
- K-NET PGA distance-tail panel.

Current figure:

`outputs/figures/ground_motion_audit/early_window_residual_evolution_panel.png`

Message:

The first seconds after P arrival add measurable information for strong-motion inference. Longer windows amplify the gain for K-NET PGA and InstanceGM PGV.

### Figure 3: Residual Diagnostics

Purpose:

Show residual structure after adding waveform information.

Panels:

- K-NET PGA residual by source distance;
- InstanceGM residual by source depth;
- InstanceGM residual by early waveform amplitude;
- signed residual and absolute residual summaries.

Current figure:

`outputs/figures/ground_motion_audit/ground_motion_residual_diagnostic_panel.png`

Message:

Waveform features reduce average and tail errors, then residual auditing identifies the remaining structured cases.

### Figure 4: High-Residual Waveform Audit

Purpose:

Show representative records where the model remains wrong.

Panels:

- repeated InstanceGM high-residual records across PGA, PGV, and SA targets;
- K-NET PGA worst cases with observed and predicted log10 PGA;
- waveform panels normalized only for visual inspection;
- metadata annotations for magnitude, distance, depth, and station.

Current figures:

- `outputs/figures/ground_motion_audit/instancegm_repeated_residual_audit_panel.png`
- `outputs/figures/ground_motion_audit/knet_pga_worst_residual_audit_panel.png`

Message:

Residual tails are inspectable waveform and metadata cases, not only aggregate errors.

### Figure 5: Phase-Label Audit

Purpose:

Use existing phase pickers as a label-domain diagnostic.

Panels:

- P and S error by dataset;
- missing-pick rate by dataset and phase;
- high-error waveform examples;
- connection between phase-label difficulty and strong-motion audit cases where available.

Current status:

The pilot supports feasibility. A larger run is needed before this becomes manuscript evidence.

Message:

Phase labels and pretrained pickers expose dataset-dependent waveform and label conventions that should be accounted for in strong-motion modeling.

## Results Structure

### Result 1: A unified cross-dataset waveform-task benchmark

Task:

Describe the datasets and why they create a useful contrast: weak-motion phase labels, regional transfer, strong-motion targets, and independent Japanese strong-motion records.

Evidence:

- STEAD, InstanceGM, Iquique, K-NET;
- 2.46 million unified manifest records;
- K-NET converted to 22,119 complete Z/N/E records;
- InstanceGM supplies PGA, PGV, and spectral acceleration targets.

Writing angle:

The benchmark joins datasets through task contrast and label audit, not through dataset size alone.

### Result 2: Early waveform windows improve strong-motion inference

Task:

Report metadata-only versus metadata plus early waveform HGB results at 1 s, 3 s, and 10 s.

Evidence:

- All tested targets improve at every window.
- K-NET PGA: 9.4%, 17.9%, 51.8% MAE reduction at 1 s, 3 s, 10 s.
- InstanceGM PGV: 28.1%, 31.9%, 44.7% MAE reduction.
- InstanceGM PGA: 16.0%, 18.9%, 30.6% MAE reduction.

Writing angle:

The first post-P second already contains predictive information. Longer windows increase information for several targets, with the strongest response in K-NET PGA and InstanceGM PGV.

### Result 3: Tail errors shrink while median bias remains small

Task:

Show q95 absolute residual reduction and median signed residual.

Evidence:

- K-NET PGA q95 reduction reaches 43.0% at 10 s.
- InstanceGM PGV q95 reduction reaches 37.2% at 10 s.
- InstanceGM SA30 q95 reduction stays near 24% across windows.
- Combined models have near-zero median signed residuals in the 10 s analysis.

Writing angle:

The waveform contribution improves average error and residual tails. The near-zero median residual makes the remaining tail cases useful for audit.

### Result 4: Residual structure identifies audit targets

Task:

Explain what remains after the combined model absorbs metadata and early waveform features.

Evidence:

- K-NET PGA absolute residual correlates with source distance after waveform features.
- The farthest K-NET distance bin remains elevated.
- Repeated InstanceGM high-residual records appear across PGA, PGV, and spectral acceleration targets.

Writing angle:

Residuals become a diagnostic object. They identify cases for label review, waveform inspection, and source-path-site analysis.

### Result 5: Phase-label transfer provides a second audit layer

Task:

Use phase-picking baselines to show dataset-domain effects.

Evidence:

- Existing pickers run across all datasets with zero failures in the pilot.
- P picks are stable in K-NET after conversion.
- S picks show larger offsets or missing predictions in InstanceGM, Iquique, and K-NET.

Writing angle:

Phase-picking models provide an independent label-domain check. The phase section should support the audit framework, not dominate the paper.

## Method Positioning

Primary method:

- P-aligned early-window feature extraction;
- HGB metadata-only baseline;
- HGB metadata plus early waveform features;
- residual metrics, binned residual diagnostics, and waveform-level audit panels.

Model choices:

Use HGB as a strong tabular baseline because it performs well with mixed metadata and compact waveform statistics. It gives a serious reference for future learned encoders.

Foundation-model component:

Keep this as optional. Current simple CNN and masked reconstruction results do not support a method-centered claim. A future encoder should be tested through held-event, held-station, cross-dataset, limited-label, calibration, or tail-error evaluations.

## Nature Communications Fit

The NC case depends on four strengths:

1. Independent datasets with different domains and instrumentation.
2. Hazard-relevant targets: PGA, PGV, and spectral acceleration.
3. Lead-time-dependent early waveform evidence.
4. Residual audit that produces interpretable, inspectable cases.

The current package is promising. It needs larger phase audit, stronger split design, and a reference ground-motion comparison before submission.

## Manuscript Limits

Avoid these claims:

- earthquake prediction;
- operational early warning readiness;
- learned foundation-model superiority;
- physical causality from residual correlation;
- general ground-motion generation.

Use these claims:

- early post-P waveform information improves strong-motion inference in these datasets;
- residual tails shrink after waveform features are added;
- remaining errors expose distance-dependent and repeated high-residual cases;
- cross-dataset phase and ground-motion labels can be audited within one reproducible benchmark.

## Immediate Next Steps

1. Scale phase baseline to at least 5,000 records per dataset where feasible.
2. Add event-held-out and station-held-out splits for InstanceGM and K-NET.
3. Verify K-NET acceleration units and PGA definition against official documentation.
4. Add a classical GMM or non-ergodic reference for PGA where feasible.
5. Convert current figures into publication-style panels with consistent typography and concise captions.
6. Write the Introduction around early strong-motion information and residual audit, with foundation models appearing only as context.
