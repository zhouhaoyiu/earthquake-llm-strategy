# Feature-group ablation summary

This audit combines existing held-out metrics. It does not retrain models.

## InstanceGM and K-NET held-station

| Window | Comparison | Median reduction | Range |
|---:|---|---:|---:|
| 1s | metadata_plus_p_vs_metadata | 20.2% | 11.3 to 40.1% |
| 1s | metadata_vs_median | 40.6% | 26.5 to 47.7% |
| 1s | p_waveform_vs_median | 29.6% | 21.7 to 42.7% |
| 2s | metadata_plus_p_vs_metadata | 21.2% | 13.7 to 40.7% |
| 2s | metadata_vs_median | 40.6% | 26.5 to 47.7% |
| 2s | p_waveform_vs_median | 34.7% | 25.6 to 47.3% |
| 3s | metadata_plus_p_vs_metadata | 22.9% | 16.7 to 41.6% |
| 3s | metadata_vs_median | 40.6% | 26.5 to 47.7% |
| 3s | p_waveform_vs_median | 36.3% | 27.8 to 49.2% |
| 5s | metadata_plus_p_vs_metadata | 24.8% | 18.8 to 45.4% |
| 5s | metadata_vs_median | 40.6% | 26.5 to 47.7% |
| 5s | p_waveform_vs_median | 39.2% | 32.9 to 53.2% |
| 10s | metadata_plus_p_vs_metadata | 31.6% | 20.9 to 52.6% |
| 10s | metadata_vs_median | 40.6% | 26.5 to 47.7% |
| 10s | p_waveform_vs_median | 43.7% | 35.4 to 60.5% |

## ESM information increments

| Holdout | Window | Comparison | Median reduction |
|---|---:|---|---:|
| event | 1s | distance_added_to_p | 19.4% |
| event | 1s | p_distance_site_vs_median | 45.2% |
| event | 1s | p_waveform_vs_median | 25.4% |
| event | 1s | site_added_to_p_distance | 9.1% |
| event | 2s | distance_added_to_p | 8.3% |
| event | 2s | p_distance_site_vs_median | 49.3% |
| event | 2s | p_waveform_vs_median | 39.2% |
| event | 2s | site_added_to_p_distance | 9.0% |
| event | 3s | distance_added_to_p | 3.0% |
| event | 3s | p_distance_site_vs_median | 52.8% |
| event | 3s | p_waveform_vs_median | 46.5% |
| event | 3s | site_added_to_p_distance | 9.0% |
| event | 5s | distance_added_to_p | 4.5% |
| event | 5s | p_distance_site_vs_median | 57.0% |
| event | 5s | p_waveform_vs_median | 52.0% |
| event | 5s | site_added_to_p_distance | 6.1% |
| event | 10s | distance_added_to_p | 6.4% |
| event | 10s | p_distance_site_vs_median | 65.9% |
| event | 10s | p_waveform_vs_median | 59.6% |
| event | 10s | site_added_to_p_distance | 9.6% |
| station | 1s | distance_added_to_p | 27.9% |
| station | 1s | p_distance_site_vs_median | 45.9% |
| station | 1s | p_waveform_vs_median | 25.4% |
| station | 1s | site_added_to_p_distance | -0.7% |
| station | 2s | distance_added_to_p | 8.7% |
| station | 2s | p_distance_site_vs_median | 35.5% |
| station | 2s | p_waveform_vs_median | 28.0% |
| station | 2s | site_added_to_p_distance | 1.7% |
| station | 3s | distance_added_to_p | 6.8% |
| station | 3s | p_distance_site_vs_median | 49.6% |
| station | 3s | p_waveform_vs_median | 45.8% |
| station | 3s | site_added_to_p_distance | 0.0% |
| station | 5s | distance_added_to_p | 3.8% |
| station | 5s | p_distance_site_vs_median | 47.4% |
| station | 5s | p_waveform_vs_median | 43.1% |
| station | 5s | site_added_to_p_distance | 3.6% |
| station | 10s | distance_added_to_p | 1.7% |
| station | 10s | p_distance_site_vs_median | 66.2% |
| station | 10s | p_waveform_vs_median | 62.1% |
| station | 10s | site_added_to_p_distance | 8.4% |

## AQ2009GM metadata plus P-window

| Holdout | Window | Median reduction |
|---|---:|---:|
| event | 2s | 39.0% |
| event | 5s | 66.3% |
| station | 2s | 38.0% |
| station | 5s | 63.8% |
| time | 2s | 43.1% |
| time | 5s | 71.2% |

Interpretation: early P-window features add information beyond metadata in the main held-station benchmark and AQ2009GM. In ESM, distance gives a large additional gain over P-only features. Site metadata gives a smaller, split- and window-dependent increment, including near-zero or slightly negative station-held increments in short windows. This supports feature-group wording in the manuscript without claiming that site effects are fully solved.

Files:
- `outputs/feature_group_ablation_table.csv`
- `outputs/figures/ground_motion_audit/feature_group_ablation.png`
