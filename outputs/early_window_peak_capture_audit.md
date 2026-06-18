# Early-Window Peak-Capture Audit

Date: 2026-06-18

This audit compares early-window horizontal peak amplitude (`h_early_absmax`) with the full-record PGA target in the existing random-split test feature tables.

## Key Results

- K-NET 1 s: median early/target ratio 1.43; fraction >= 0.8 is 0.698.
- K-NET 10 s: median early/target ratio 2.02; fraction >= 0.8 is 0.947.
- InstanceGM 10 s direct amplitude ratio median is 0.000287, indicating that waveform amplitudes and PGA targets are not on a directly comparable scale in the local feature table.

## Interpretation

K-NET PGA results should be framed as early-window strong-motion information, with a clear note that 10 s windows often contain target-scale horizontal amplitudes. The 1 s and 3 s windows remain important for lead-time-sensitive interpretation. InstanceGM should not use direct early/target amplitude ratios without unit reconciliation; its evidence should rely on held-out prediction, residual, and calibration metrics.

CSV: `outputs/early_window_peak_capture_audit.csv`
