# ESM regional GMM screening

This screening layer compares early-window ESM held-station models with bias-corrected OpenQuake GMM candidates on the same train/test rows. Rows without source magnitude are excluded because a GMM requires magnitude. Vs30 is clipped to 150-1500 m/s and missing Vs30 is set to 760 m/s.

Distance mapping: Rjb models use `source_distance_km`; Rhyp and Rrup models use `path_hyp_distance_km`. Rake is fixed to 0 because mechanism metadata are incomplete in the compact table. This is a reviewer-facing classical reference, not a complete engineering GMPE validation.

| Target | Window | Best regional GMM | GMM MAE | Early P+distance+site MAE | Early reduction vs GMM |
|---|---:|---|---:|---:|---:|
| PGA | 2s | AkkarEtAlRhyp2014 | 0.465 | 0.303 | 34.8% |
| PGA | 5s | AkkarEtAlRhyp2014 | 0.439 | 0.227 | 48.3% |
| PGA | 10s | AkkarEtAlRhyp2014 | 0.315 | 0.179 | 43.1% |
| PGV | 2s | AkkarEtAlRhyp2014 | 0.420 | 0.320 | 23.8% |
| PGV | 5s | AkkarEtAlRhyp2014 | 0.389 | 0.272 | 30.2% |
| PGV | 10s | BindiEtAl2014Rhyp | 0.326 | 0.227 | 30.4% |

Interpretation: the comparison uses a stronger classical reference than a median or distance-only baseline. It supports the claim that early P-wave information adds predictive content beyond regional magnitude-distance-site scaling, while the fixed rake, distance proxies and missing-site defaults keep the claim at screening level.

Work CSV: `work/esm_regional_gmm_screening/esm_regional_gmm_screening.csv`
Public CSV: `outputs/esm_regional_gmm_screening.csv`
Figure: `outputs/figures/ground_motion_audit/esm_regional_gmm_screening.png`
