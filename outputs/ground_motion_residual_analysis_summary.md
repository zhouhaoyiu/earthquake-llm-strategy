# Ground-Motion Residual Analysis Summary

Date: 2026-06-12

## Question

Does the strongest current baseline leave interpretable residual structure that can support a Nature Communications route?

Short answer: **yes, as a benchmark-and-residual-science route.**

The 10 s HGB metadata + early-waveform baseline reduces both average error and tail error across InstanceGM and K-NET. The remaining residuals are mostly weakly correlated with single variables, which means the combined model has already absorbed much of the first-order source-path-site and early-waveform structure. The residual tails still identify useful audit targets: K-NET far-distance PGA cases and repeated InstanceGM outliers across PGA, PGV, and spectral acceleration.

## Setup

Script:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/scripts/analyze_ground_motion_residuals.py`

Inputs:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_baseline_multi_10s`

Outputs:

- Metrics: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_residuals_10s/ground_motion_residual_metrics.csv`
- Per-record predictions: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_residuals_10s/ground_motion_residual_predictions.csv`
- Metric deltas: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_residuals_10s/ground_motion_residual_metric_deltas.csv`
- Binned residuals: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_residuals_10s/ground_motion_residual_bins.csv`
- Correlations: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_residuals_10s/ground_motion_residual_correlations.csv`
- Worst cases: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_residuals_10s/ground_motion_residual_worst_cases.csv`
- Plots: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_residuals_10s/plots`
- Figure-ready audit panels: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit`

Residual definition:

`residual = predicted log10 target - observed log10 target`

Positive residuals are overprediction. Negative residuals are underprediction.

## Main Result

The table compares metadata-only HGB against metadata + 10 s early-waveform HGB.

| dataset | target | metadata MAE | combined MAE | MAE reduction | metadata q95 abs | combined q95 abs | q95 reduction | combined R2 | median signed residual |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| InstanceGM | PGA | 0.299 | 0.207 | 30.6% | 0.769 | 0.664 | 13.6% | 0.847 | 0.006 |
| InstanceGM | PGV | 0.298 | 0.165 | 44.7% | 0.790 | 0.497 | 37.2% | 0.863 | 0.014 |
| InstanceGM | SA03 | 0.273 | 0.221 | 19.0% | 0.708 | 0.619 | 12.6% | 0.834 | -0.008 |
| InstanceGM | SA10 | 0.286 | 0.210 | 26.8% | 0.716 | 0.552 | 22.9% | 0.827 | 0.010 |
| InstanceGM | SA30 | 0.306 | 0.242 | 20.9% | 0.781 | 0.593 | 24.0% | 0.680 | 0.019 |
| K-NET | PGA | 0.217 | 0.105 | 51.8% | 0.534 | 0.304 | 43.0% | 0.877 | 0.016 |

The combined model is nearly unbiased in the median for all targets. The strongest tail-error reductions occur for K-NET PGA and InstanceGM PGV.

## Residual Structure

After adding early waveform features, residual correlations with single variables are modest.

Largest signed-residual correlations:

| dataset | target | variable | corr residual | corr abs residual |
|---|---|---|---:|---:|
| InstanceGM | PGV | vec early RMS | -0.100 | 0.106 |
| K-NET | PGA | vec early RMS | 0.097 | 0.112 |
| K-NET | PGA | year | -0.091 | 0.029 |
| InstanceGM | PGV | vec early absmax | -0.080 | 0.087 |
| InstanceGM | SA30 | vec early RMS | -0.067 | 0.110 |

Largest absolute-residual correlations:

| dataset | target | variable | corr abs residual |
|---|---|---|---:|
| K-NET | PGA | source distance | 0.254 |
| InstanceGM | PGA | source depth | 0.166 |
| K-NET | PGA | source magnitude | 0.115 |
| K-NET | PGA | vec early RMS | 0.112 |
| InstanceGM | SA30 | vec early RMS | 0.110 |

Interpretation:

1. K-NET retains a distance-dependent PGA tail. The farthest distance bin has MAE 0.160 log10, compared with 0.078-0.111 in nearer bins.
2. InstanceGM residuals have weaker single-variable structure. The repeated high residuals are more likely linked to outlier labels, local site/path effects, or rare waveform-target combinations.
3. Early waveform features reduce residual tails while preserving near-zero median bias. This is a strong baseline and a useful diagnostic tool.

## Worst-Case Audit Targets

Repeated InstanceGM cases appear across PGA, PGV, and SA30 worst-case lists:

- `instancegm:bucket116$67,:3,:12000`
- `instancegm:bucket1110$989,:3,:12000`
- `instancegm:bucket148$566,:3,:12000`
- `instancegm:bucket180$747,:3,:12000`
- `instancegm:bucket245$406,:3,:12000`

These should be plotted directly from waveform and metadata. They may indicate target-label anomalies, severe local site/path effects, or rare source-path-site combinations.

K-NET worst cases show both large underprediction of strong PGA and overprediction at longer distances:

- `knet:NIG0190508031638`
- `knet:IBR0150507231635`
- `knet:FKS0080405080910`
- `knet:FKO0039903091253`
- `knet:HKD0530505190133`

These are suitable for a residual-audit figure because K-NET is independent of InstanceGM and has different instrumentation and magnitude-distance coverage.

## Figure Panels

Figure-ready panels were generated:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit/instancegm_repeated_residual_audit_panel.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit/knet_pga_worst_residual_audit_panel.png`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit/ground_motion_residual_diagnostic_panel.png`

The panels show 10 s post-P Z/N/E waveforms and residuals for selected audit records. The plotted waveforms are normalized within each record for visual comparison; metadata retain the original vector early-window amplitude.

## Paper Consequence

The residual analysis strengthens the NC fallback route:

**A cross-dataset seismic waveform benchmark and label-audit study linking phase-model failure modes to ground-motion residual structure.**

This route no longer depends on a learned foundation model beating HGB in the first round. It can be built around:

1. unified waveform-task archive across STEAD, InstanceGM, Iquique, and K-NET;
2. structured phase-picker failures under dataset shift;
3. strong HGB evidence that early waveform information reduces average and tail ground-motion errors;
4. residual audit identifying distance-dependent K-NET PGA tails and repeated InstanceGM outliers;
5. targeted waveform and metadata panels for high-residual records.

The method route remains possible, but the current evidence favors residual-science as the more reliable NC storyline.

## Next Step

Build a figure-ready audit packet:

1. plot waveforms and metadata for repeated InstanceGM worst cases;
2. plot K-NET worst cases with magnitude, distance, depth, PGA, prediction, and residual;
3. create binned residual panels for K-NET distance and InstanceGM depth/amplitude;
4. run the same residual analysis for 1 s and 3 s windows to show how residual structure changes with information window.

## Command

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/analyze_ground_motion_residuals.py \
  --feature-dir work/ground_motion_baseline_multi_10s \
  --out-dir work/ground_motion_residuals_10s \
  --feature-sets metadata_only metadata_plus_early_waveform \
  --bins 5

/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/plot_ground_motion_audit_panels.py \
  --out-dir outputs/figures/ground_motion_audit
```
