# Cross-region Transfer Window Scan

This summary combines the 1, 3, and 10 s cross-region early-waveform transfer checks.

| Window | Zero-shot median ratio | Offset-calibrated median ratio |
|---:|---:|---:|
| 1s | 1.49 | 1.40 |
| 3s | 1.74 | 1.65 |
| 10s | 2.84 | 2.26 |

Interpretation:
- All cross-domain rows remain worse than target-domain training.
- The median transfer penalty increases from 1 s to 10 s, indicating that longer-window amplitude structure is more region- and measurement-system dependent.
- Offset calibration helps at every window but does not remove the transfer boundary.

Files:
- `work/cross_region_waveform_transfer_window_scan.csv`
- `outputs/figures/ground_motion_audit/cross_region_waveform_transfer_window_scan.png`
