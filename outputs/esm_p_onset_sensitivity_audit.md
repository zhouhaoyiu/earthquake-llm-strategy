# ESM P-Onset Sensitivity Audit

This audit uses the retained ESM compact feature table generated with `theoretical_vp_6kmps`. It does not create new waveform features and does not replace catalog/manual P picks.

Rows audited: 134,250. Unique event-station records: 26,850.

| Vp km/s | Window | Valid fraction among retained rows | Median shift vs 6 km/s | q95 absolute shift |
|---:|---:|---:|---:|---:|
| 5.5 | 1s | 0.9998 | 2.517s | 4.594s |
| 5.5 | 2s | 0.9997 | 2.517s | 4.594s |
| 5.5 | 3s | 0.9997 | 2.517s | 4.594s |
| 5.5 | 5s | 0.9996 | 2.517s | 4.594s |
| 5.5 | 10s | 0.9989 | 2.517s | 4.594s |
| 6.0 | 1s | 0.9999 | 0.000s | 0.000s |
| 6.0 | 2s | 0.9998 | 0.000s | 0.000s |
| 6.0 | 3s | 0.9998 | 0.000s | 0.000s |
| 6.0 | 5s | 0.9997 | 0.000s | 0.000s |
| 6.0 | 10s | 0.9991 | 0.000s | 0.000s |
| 6.5 | 1s | 0.9955 | -2.130s | 3.887s |
| 6.5 | 2s | 0.9955 | -2.130s | 3.887s |
| 6.5 | 3s | 0.9954 | -2.130s | 3.887s |
| 6.5 | 5s | 0.9952 | -2.130s | 3.887s |
| 6.5 | 10s | 0.9948 | -2.130s | 3.887s |

All-Vp retained-window fraction:

| Window | Fraction valid under 5.5/6.0/6.5 km/s |
|---:|---:|
| 1s | 0.9953 |
| 2s | 0.9952 |
| 3s | 0.9952 |
| 5s | 0.9951 |
| 10s | 0.9944 |

Interpretation:
- Changing Vp from 6.0 to 5.5 km/s delays the theoretical P onset by a median 2.52 s.
- Changing Vp from 6.0 to 6.5 km/s advances it by a median 2.13 s.
- The retained-row definition is stable under these plausible velocities, with all-window valid fractions above 0.99.
- The timing shift is large relative to 1-2 s windows, so ESM remains an external strong-motion supplement and transfer-domain check, not a catalog-P lead-time proof.

Files:
- `outputs/esm_p_onset_sensitivity_audit.csv`
