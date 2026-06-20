# K-NET Japan GMM Reference Summary

Date: 2026-06-18

This screening reference evaluates OpenQuake Japanese or Japan-derived GMMs on the balanced held-station K-NET PGA split. Predictions use source distance as an Rrup proxy, missing Vs30 defaults, and train-set median bias correction.

Best candidate reference: Kanno2006Shallow, MAE 0.242, R2 0.490.
Current metadata plus early-waveform K-NET held-station MAE: 0.111.

Interpretation: this is a stronger classical screening check for K-NET than a single generic BooreEtAl2014 reference, while still limited by distance, Vs30, and tectonic-class approximations.

CSV: `work/ground_motion_balanced_station_10s/knet_japan_gmm_reference.csv`
