# Residual persistence audit

This audit uses existing 1 s, 3 s and 10 s metadata-plus-early-waveform residual tables. It does not retrain models.

| dataset | target | n_records | n_top5_10s | persistent_top5_fraction | sign_stable_top5_fraction | high1_resolved_fraction | top5_10s_underprediction_fraction | top5_10s_median_distance_km | all_median_distance_km | top5_10s_median_abs_residual | all_median_abs_residual_10s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| instancegm | pga | 999 | 50 | 0.620 | 1.000 | 0.320 | 0.560 | 36.579 | 43.195 | 0.807 | 0.138 |
| instancegm | pgv | 1000 | 50 | 0.680 | 1.000 | 0.280 | 0.640 | 30.043 | 43.175 | 0.692 | 0.100 |
| instancegm | sa03 | 985 | 50 | 0.500 | 1.000 | 0.440 | 0.520 | 65.159 | 43.336 | 0.741 | 0.163 |
| instancegm | sa10 | 1000 | 50 | 0.520 | 0.980 | 0.420 | 0.500 | 32.098 | 43.175 | 0.644 | 0.151 |
| instancegm | sa30 | 945 | 48 | 0.625 | 0.958 | 0.312 | 0.625 | 33.317 | 42.960 | 0.722 | 0.190 |
| knet | pga | 1000 | 50 | 0.200 | 0.980 | 0.740 | 0.540 | 87.797 | 51.085 | 0.366 | 0.079 |

Interpretation:

- K-NET PGA keeps 20.0% of its 10 s top-tail residuals in the top 5% at both 1 s and 3 s.
- 74.0% of K-NET PGA 1 s top-tail residuals leave the top 5% by 10 s.
- The remaining K-NET PGA 10 s tail is farther than the full set by 36.7 km in median distance.

Files:
- `outputs/residual_persistence_audit.csv`
- `outputs/figures/ground_motion_audit/residual_persistence_audit.png`
