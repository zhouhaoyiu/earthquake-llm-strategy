# Regional GMM Boundary Note

The current package supports classical-reference screening. It does not support a full regional GMPE/GMM superiority claim.

Verified reference layers:

| Layer | Status | Use |
|---|---|---|
| Attenuation-shaped ridge | done | low-parameter distance/magnitude reference |
| OpenQuake BooreEtAl2014 | done | bias-corrected generic reference |
| K-NET Japanese GMM screening | done | Japan-oriented PGA screening |
| ESM regional GMM screening | done | European PGA/PGV screening with magnitude, distance and Vs30 where available |
| Regional GMM readiness audit | done | metadata availability boundary |

Current metadata boundary:

- InstanceGM balanced held-station records join back to metadata and have complete Vs30 in this split.
- InstanceGM focal-mechanism coverage is sparse: 141/5,000 train records and 36/1,000 test records.
- K-NET has source-distance values in the current split.
- K-NET lacks Vs30, rupture distance, and focal-mechanism fields in the approved local package.
- ESM contains usable distance and Vs30 fields for regional screening, but the compact table still uses distance proxies and fixed rake.

ESM screening result:

| Target | Window | Best regional GMM | GMM MAE | Early P+distance+site MAE | Early reduction vs GMM |
|---|---:|---|---:|---:|---:|
| PGA | 2 s | AkkarEtAlRhyp2014 | 0.465 | 0.303 | 34.8% |
| PGA | 5 s | AkkarEtAlRhyp2014 | 0.439 | 0.227 | 48.3% |
| PGA | 10 s | AkkarEtAlRhyp2014 | 0.315 | 0.179 | 43.1% |
| PGV | 2 s | AkkarEtAlRhyp2014 | 0.420 | 0.320 | 23.8% |
| PGV | 5 s | AkkarEtAlRhyp2014 | 0.389 | 0.272 | 30.2% |
| PGV | 10 s | BindiEtAl2014Rhyp | 0.326 | 0.227 | 30.4% |

Manuscript wording:

The early-waveform model improves over attenuation-shaped, Japanese regional, and ESM regional screening references under stated metadata approximations. A fully specified regional GMM comparison still requires curated rupture distance, site terms, and tectonic or focal-mechanism metadata. The current study reports this as a reference boundary, not a complete regional-GMM benchmark.
