# Attenuation-Shaped Reference Summary

Date: 2026-06-18

This reference uses a simple ridge model with magnitude, log10 hypocentral-distance shape, depth, and log10 Vs30 where available. It is fitted on the balanced held-station training features and evaluated on the same held-station test split as the main 10 s model. InstanceGM has Vs30 in this split; K-NET does not, so the K-NET attenuation reference is not site-corrected.

| Dataset | Target | Attenuation MAE | Metadata HGB MAE | Metadata + early MAE | Reduction vs attenuation |
|---|---|---:|---:|---:|---:|
| InstanceGM | PGA | 0.377 | 0.392 | 0.253 | 33.0% |
| InstanceGM | PGV | 0.362 | 0.372 | 0.176 | 51.2% |
| InstanceGM | SA03 | 0.296 | 0.327 | 0.242 | 18.2% |
| InstanceGM | SA10 | 0.317 | 0.331 | 0.262 | 17.5% |
| InstanceGM | SA30 | 0.363 | 0.343 | 0.248 | 31.7% |
| K-NET | PGA | 0.230 | 0.222 | 0.111 | 51.6% |

Interpretation: the early waveform model improves over a low-parameter attenuation-shaped reference across all tested held-station targets. This is a baseline check, not a replacement for a fully specified regional GMM.

CSV: `work/ground_motion_balanced_station_10s/attenuation_reference.csv`
