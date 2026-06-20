# Regional GMM Boundary Note

The current package supports classical-reference screening. It does not support a full regional GMPE/GMM superiority claim.

Verified reference layers:

| Layer | Status | Use |
|---|---|---|
| Attenuation-shaped ridge | done | low-parameter distance/magnitude reference |
| OpenQuake BooreEtAl2014 | done | bias-corrected generic reference |
| K-NET Japanese GMM screening | done | Japan-oriented PGA screening |
| Regional GMM readiness audit | done | metadata availability boundary |

Current metadata boundary:

- InstanceGM balanced held-station records join back to metadata and have complete Vs30 in this split.
- InstanceGM focal-mechanism coverage is sparse: 141/5,000 train records and 36/1,000 test records.
- K-NET has source-distance values in the current split.
- K-NET lacks Vs30, rupture distance, and focal-mechanism fields in the approved local package.

Manuscript wording:

The early-waveform model improves over attenuation-shaped and screened OpenQuake references under stated metadata approximations. A fully specified regional GMM comparison requires curated rupture distance, site terms, and tectonic or focal-mechanism metadata. The current study reports this as a reference boundary, not a complete regional-GMM benchmark.
