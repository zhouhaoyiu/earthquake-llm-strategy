# ESM Waveform-Level P-Onset Spot Audit

This audit compares the ESM theoretical P-onset estimate with a waveform-level onset proxy computed from local ACC.AP streams.
The proxy is an automated envelope threshold detector, not a manual or catalog P pick.

| Field | Value |
|---|---:|
| Requested samples | 200 |
| Processed samples | 200 |
| Detected onset proxies | 105 |
| High-confidence proxies | 86 |
| Search half-width | 8 s |

| subset | n | median delta s | median abs s | q90 abs s | q95 abs s | frac abs <=2s | frac abs <=5s |
|---|---:|---:|---:|---:|---:|---:|---:|
| all detected | 105 | 1.037 | 1.572 | 4.331 | 6.580 | 0.600 | 0.914 |
| high confidence | 86 | 0.960 | 1.223 | 3.338 | 3.960 | 0.674 | 0.988 |

Interpretation:
- The result is a waveform-level timing sanity check for ESM, not a replacement for manual P picks.
- If the high-confidence absolute offsets remain within a few seconds, ESM can stay as an external transfer-domain check with explicit onset-proxy wording.
- Records without a detected proxy or with low peak-to-noise should stay outside lead-time claims.

Files:
- `outputs/esm_waveform_p_pick_spotcheck.csv`
- `outputs/esm_waveform_p_pick_spotcheck.json`
- `outputs/figures/ground_motion_audit/esm_waveform_p_pick_spotcheck.png`
