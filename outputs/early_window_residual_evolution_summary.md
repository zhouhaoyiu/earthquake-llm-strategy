# Early-Window Residual Evolution Summary

Date: 2026-06-14

Residual definition: predicted log10 target minus observed log10 target.

The table compares metadata-only HGB against metadata plus early waveform features across 1 s, 3 s, and 10 s post-P windows.

| window_s | dataset | target | mae_log10_target_metadata | mae_log10_target_combined | mae_reduction_pct | q95_abs_residual_metadata | q95_abs_residual_combined | q95_reduction_pct | r2_log10_target_combined |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | instancegm | pga | 0.299 | 0.251 | 15.985 | 0.769 | 0.664 | 13.640 | 0.819 |
| 3 | instancegm | pga | 0.299 | 0.243 | 18.916 | 0.769 | 0.691 | 10.196 | 0.822 |
| 10 | instancegm | pga | 0.299 | 0.207 | 30.645 | 0.769 | 0.664 | 13.647 | 0.847 |
| 1 | instancegm | pgv | 0.298 | 0.214 | 28.071 | 0.790 | 0.582 | 26.336 | 0.829 |
| 3 | instancegm | pgv | 0.298 | 0.203 | 31.923 | 0.790 | 0.541 | 31.524 | 0.844 |
| 10 | instancegm | pgv | 0.298 | 0.165 | 44.704 | 0.790 | 0.497 | 37.151 | 0.863 |
| 1 | instancegm | sa03 | 0.273 | 0.250 | 8.476 | 0.708 | 0.641 | 9.433 | 0.807 |
| 3 | instancegm | sa03 | 0.273 | 0.239 | 12.425 | 0.708 | 0.637 | 10.015 | 0.820 |
| 10 | instancegm | sa03 | 0.273 | 0.221 | 18.960 | 0.708 | 0.619 | 12.564 | 0.834 |
| 1 | instancegm | sa10 | 0.286 | 0.225 | 21.361 | 0.716 | 0.582 | 18.668 | 0.815 |
| 3 | instancegm | sa10 | 0.286 | 0.220 | 23.053 | 0.716 | 0.556 | 22.305 | 0.826 |
| 10 | instancegm | sa10 | 0.286 | 0.210 | 26.822 | 0.716 | 0.552 | 22.930 | 0.827 |
| 1 | instancegm | sa30 | 0.306 | 0.246 | 19.642 | 0.781 | 0.592 | 24.266 | 0.693 |
| 3 | instancegm | sa30 | 0.306 | 0.243 | 20.656 | 0.781 | 0.588 | 24.778 | 0.699 |
| 10 | instancegm | sa30 | 0.306 | 0.242 | 20.860 | 0.781 | 0.593 | 24.026 | 0.680 |
| 1 | knet | pga | 0.217 | 0.197 | 9.420 | 0.534 | 0.485 | 9.074 | 0.630 |
| 3 | knet | pga | 0.217 | 0.178 | 17.943 | 0.534 | 0.447 | 16.285 | 0.688 |
| 10 | knet | pga | 0.217 | 0.105 | 51.755 | 0.534 | 0.304 | 42.982 | 0.877 |

Interpretation:

1. Early waveform information improves mean and tail residuals at every tested window.
2. Longer windows generally provide larger gains, especially for K-NET PGA and InstanceGM PGV.
3. The 1 s window already adds signal, which supports a lead-time-dependent interpretation rather than a full-record leakage explanation.
4. K-NET PGA retains a distance-dependent residual tail after waveform features, making it a strong residual-audit target.
