# Phase Audit 1000 Summary

Date: 2026-06-18

## Result

Existing phase audit already covers 1,000 records per dataset.

Datasets:

- STEAD
- InstanceGM
- Iquique
- K-NET

Models:

- PhaseNet(STEAD)
- EQTransformer(STEAD)

Outputs:

- Predictions: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/baseline_pilot_1000_stead_models/phase_baseline_pilot_predictions.csv`
- Summary table: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/baseline_pilot_1000_stead_models/phase_error_summary.csv`
- Figure: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/phase_audit/phase_audit_1000_panel.png`

## Main Findings

K-NET P picks are strong after conversion:

- PhaseNet(STEAD): P MAE 0.056 s, missing 3.8%.
- EQTransformer(STEAD): P MAE 0.314 s, missing 14.5%, but median error is only 0.030 s and q95 is 0.153 s.

K-NET S picks have a wider tail:

- PhaseNet(STEAD): S MAE 0.299 s, q95 1.051 s.
- EQTransformer(STEAD): S MAE 0.299 s, q95 1.061 s.

InstanceGM has the largest missing-pick problem:

- P missing: 13.3% for PhaseNet, 18.7% for EQTransformer.
- S missing: 45.2% for PhaseNet, 47.9% for EQTransformer.

Iquique is a transfer-stress dataset:

- P missing is low: 2.2-3.0%.
- S missing is higher: 15.6-16.6%.
- S MAE is 0.423-0.665 s.

STEAD behaves as expected:

- PhaseNet(STEAD) is strong on STEAD: P MAE 0.035 s, S MAE 0.082 s.
- EQTransformer has higher P missing in this run but low S error.

## Paper Use

This supports a label-domain audit layer:

1. K-NET conversion is credible because P picks are stable.
2. S phases expose stronger dataset and label-transfer issues.
3. InstanceGM has substantial missing-pick behavior, especially for S.
4. The phase audit should support the strong-motion story, not replace it.

## Limit

This is enough for a first NC evidence package. A 5,000-record run would improve confidence but is not the next bottleneck unless reviewers demand more scale.
