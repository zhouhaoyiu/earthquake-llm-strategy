# Science Advances / Nature Communications Strategy

Date: 2026-06-11

## Recommendation

Use **Nature Communications** as the primary target and **Science Advances** as the stretch target.

The current local assets already support a serious Nature Communications-style paper: a high-quality original study with importance to seismology, earthquake engineering, and seismic machine learning. Science Advances becomes realistic if the results establish a broader cross-disciplinary message: a seismic foundation representation that connects weak-motion phase information, strong-motion hazard metrics, and cross-network generalization.

Official fit checks:

- Nature Communications describes itself as an open-access multidisciplinary journal for high-quality research in biological, physical, chemical, and Earth sciences, with papers representing important advances of significance to specialists within each field.
- Nature Communications publishes original research as Articles, with flexible initial formatting; it suggests main text up to about 5,000 words, abstracts up to 200 words, and up to 10 display items.
- Science Advances describes its mission around expert peer review and vetted open-access research across science. Its author pages emphasize clear initial submissions, concise writing, and abstracts that explain why the research was done, what was found, and why the results are important.

## Working Manuscript Concept

### Primary NC Version

Title draft:

**A generalizable seismic waveform foundation model for phase and ground-motion tasks across regional networks**

Central claim:

A compact waveform foundation model trained on public seismic archives learns transferable representations that improve phase picking, event detection, and ground-motion estimation across weak-motion and strong-motion datasets.

Evidence required:

- STEAD pretraining and internal validation
- Iquique regional transfer
- InstanceGM ground-motion prediction
- K-NET conversion and transfer validation
- Comparisons with PhaseNet, EQTransformer, GPD, CNN/Transformer baselines
- Calibration, uncertainty, and error analysis across regions and magnitude ranges

This version can be accepted even if the main contribution is method plus evidence, provided the cross-dataset validation is strong and the model behavior is interpretable enough for domain readers.

### SA Stretch Version

Title draft:

**A transferable seismic foundation representation links phase information and strong-motion hazard metrics**

Central claim:

Seismic waveform representations learned without task-specific labels preserve physically meaningful source, path, and site information, enabling transfer across phase picking and strong-motion prediction tasks.

Extra evidence required:

- Strong source-path-site disentanglement analysis
- Clear physical interpretation of learned embeddings
- Robust transfer under leave-region, leave-network, and leave-event-family splits
- Demonstrated value beyond a single specialist task
- A broad framing that connects AI foundation models to earthquake hazard assessment

This version needs stronger scientific insight than a performance leaderboard.

## Data Plan

### Confirmed Core Datasets

- STEAD: 1,265,657 traces; phase picking and event/noise detection
- InstanceGM: 1,159,249 traces; PGA, PGV, spectral acceleration, phase labels
- Iquique: 13,400 traces; regional transfer and sequence-style validation
- K-NET raw BSON: 22,119 records, 1,528 events, 921 stations, M2.8-M8.0

### Immediate Data Work

1. Convert K-NET BSON into reproducible `.npy` or HDF5 waveform files.
2. Produce a `knet_manifest.csv` with event, station, channel, P/S picks, magnitude, depth, distance, PGA, sampling rate, and split.
3. Define one unified schema across STEAD, InstanceGM, Iquique, and K-NET.
4. Freeze splits before model tuning.
5. Save dataset checksums and conversion logs.

## Model Plan

Baseline models:

- PhaseNet
- EQTransformer
- GPD
- Small CNN
- Small Transformer or Conformer

Proposed model:

- Compact seismic waveform encoder
- Masked reconstruction or contrastive pretraining
- Multi-task heads for detection, P/S picking, PGA/PGV/SA prediction
- Metadata-conditioning branch for source, path, and site variables where available

Keep the first model small enough to train repeatedly on M4 Max with MPS. Scale only after the evaluation pipeline is stable.

## Experiment Matrix

### Task 1: Phase Picking

Datasets:

- STEAD
- Iquique
- K-NET after conversion

Metrics:

- P/S pick MAE
- precision, recall, F1 under fixed tolerance windows
- calibration of pick confidence
- failure cases by SNR, magnitude, distance, station network

### Task 2: Event Detection

Datasets:

- STEAD event/noise
- K-NET detection labels after conversion

Metrics:

- AUROC
- AUPRC
- F1
- false alarm rate
- missed event rate

### Task 3: Strong-Motion Prediction

Datasets:

- InstanceGM
- K-NET

Targets:

- PGA
- PGV
- SA at selected periods

Metrics:

- MAE and RMSE in log space
- residuals by magnitude, distance, depth, Vs30 or station proxy
- calibration and uncertainty
- comparison with simple metadata-only models

### Task 4: Cross-Domain Transfer

Splits:

- train on STEAD, test on Iquique
- train on STEAD, test on K-NET phase labels
- train on InstanceGM, test on K-NET ground-motion labels
- leave-network-out validation inside each dataset

This is the central evidence for NC. It becomes SA-level only if the transfer pattern exposes a general scientific principle.

## Figure Plan

Figure 1: Dataset map and task design  
Show STEAD, InstanceGM, Iquique, and K-NET roles. Keep it conceptual and data-grounded.

Figure 2: Model architecture  
Show waveform encoder, self-supervised pretraining, task heads, and metadata branch.

Figure 3: Phase picking and detection results  
Compare against PhaseNet, EQTransformer, GPD, and compact baselines.

Figure 4: Strong-motion prediction results  
Show PGA/PGV/SA performance and residual structure.

Figure 5: Cross-dataset transfer  
Show degradation and recovery across datasets and networks.

Figure 6: Physical interpretation  
Embedding structure by magnitude, distance, depth, site proxy, and station network.

Figure 7: Uncertainty and failure modes  
Show where the model should not be trusted.

Supplementary:

- preprocessing details
- dataset schemas
- hyperparameters
- ablations
- statistical tests
- extra transfer tables

## Minimum Evidence Bar

For Nature Communications:

- Reproducible K-NET conversion
- Clean unified manifests
- Strong baseline comparison
- Cross-dataset transfer that beats or matches specialist models
- Error analysis that domain readers can trust
- Uncertainty or calibration results
- Clear release plan for code, manifests, and trained weights if licensing allows

For Science Advances:

- All NC evidence
- Stronger physical interpretation
- Clear source-path-site or hazard-relevant insight
- Cross-task transfer that changes how readers think about seismic representation learning
- A manuscript written for readers outside phase picking

## Main Risk Register

Risk: performance improvement is small.  
Response: emphasize generalization, calibration, and interpretability only if supported by results.

Risk: K-NET conversion introduces hidden preprocessing bias.  
Response: write a deterministic converter, preserve raw metadata, log every dropped record.

Risk: foundation-model language outpaces the experiment.  
Response: use "foundation representation" only if pretraining, transfer, and multi-task evaluation are actually done.

Risk: InstanceGM and K-NET target definitions differ.  
Response: document units, filters, windows, and label construction before cross-dataset comparisons.

Risk: model learns dataset identity.  
Response: run leave-dataset and leave-network tests; visualize embeddings colored by dataset and physical variables.

## First 10-Day Execution Plan

Day 1-2:

- Build K-NET converter and manifest.
- Verify waveform shapes, units, sampling rates, P/S labels, PGA fields.

Day 3:

- Build unified manifest schema.
- Create fixed train/dev/test split files.

Day 4-5:

- Run cached SeisBench baselines on STEAD/Iquique where directly supported.
- Run simple CNN/Transformer baselines on K-NET and InstanceGM subsets.

Day 6-7:

- Train first compact self-supervised encoder on STEAD plus InstanceGM samples.
- Save checkpoints and training logs.

Day 8:

- Fine-tune task heads for phase picking, detection, and strong-motion prediction.

Day 9:

- Run cross-dataset transfer tests.
- Generate first result tables.

Day 10:

- Decide target:
  - NC route if transfer and calibration are solid.
  - SA route only if embedding analysis gives a physical insight.
  - Specialist journal route if results are useful but narrow.

## Draft Abstract Skeleton

Seismic networks record weak and strong ground motions across heterogeneous sensors, regions, and event populations. Current deep-learning models often perform well within a training dataset, yet their behavior across phase picking and ground-motion tasks remains difficult to compare. We assemble a public multi-dataset benchmark spanning STEAD, InstanceGM, Iquique, and K-NET, and train a compact waveform foundation model with self-supervised objectives and task-specific heads. Across phase picking, event detection, and ground-motion estimation, the model improves cross-dataset transfer and produces calibrated uncertainty under regional and network shifts. Representation analyses show that the learned embedding organizes waveforms by physically meaningful source, path, and site variables. These results provide a reproducible route for using foundation models in seismic monitoring and earthquake hazard workflows.

This abstract is a target shape, not a claim of completed results.
