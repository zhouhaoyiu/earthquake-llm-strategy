# Residual mechanism audit

This audit compares the largest 5% of 10 s absolute residuals with all 10 s held-station residuals for the metadata-plus-early-waveform model.

| series | dominant boundary | top shifted covariate | scaled median shift | top-5% underprediction fraction | top-5% median abs residual |
|---|---|---|---:|---:|---:|
| instancegm pga | early_amplitude_boundary | early amp | 0.41 | 0.56 | 0.807 |
| instancegm pgv | strong_motion_tail_boundary | target | 1.02 | 0.64 | 0.692 |
| instancegm sa03 | path_attenuation_boundary | distance | 0.39 | 0.52 | 0.741 |
| instancegm sa10 | early_amplitude_boundary | early amp | 0.53 | 0.50 | 0.644 |
| instancegm sa30 | strong_motion_tail_boundary | target | 1.32 | 0.62 | 0.722 |
| knet pga | path_attenuation_boundary | distance | 0.80 | 0.54 | 0.366 |

Interpretation: large residuals separate into path-attenuation, strong-motion-tail and early-amplitude boundaries. This supports a structured residual claim: some held-station errors are tied to identifiable covariate regimes after the early-window model has used distance and site metadata. The audit reports associations, not causal attribution.

CSV: `outputs/residual_mechanism_audit.csv`
Class CSV: `outputs/residual_mechanism_classes.csv`
Figure: `outputs/figures/ground_motion_audit/residual_mechanism_audit.png`
