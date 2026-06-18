# OpenQuake Reference Summary

Date: 2026-06-18

## Result

OpenQuake is now usable in the `zhy` environment.

Installed missing geospatial dependencies:

- `fiona`
- `rtree`
- `rasterio`
- `geopandas`

`openquake.hazardlib` imports successfully.

## Reference

Model:

- `BooreEtAl2014`
- PGA, PGV, SA03, SA10, SA30 where labels are available
- output converted from `ln(g)` to `log10(cm/s^2)`
- train-set median bias correction

Approximations:

- `source_distance_km` used as an `Rjb` proxy
- `rake = 0`
- missing Vs30 set to 760 m/s

These approximations make this a weak reference, not a final GMPE implementation.

## Balanced Held-Station Comparison

| dataset | target | Boore2014 MAE | metadata HGB MAE | metadata + waveform MAE | combined R2 | combined reduction vs Boore2014 |
|---|---|---:|---:|---:|---:|---:|
| InstanceGM | PGA | 0.399 | 0.392 | 0.253 | 0.799 | 36.6% |
| InstanceGM | PGV | 0.434 | 0.372 | 0.176 | 0.858 | 59.4% |
| InstanceGM | SA03 | 0.374 | 0.327 | 0.242 | 0.814 | 35.4% |
| InstanceGM | SA10 | 0.411 | 0.331 | 0.262 | 0.785 | 36.4% |
| InstanceGM | SA30 | 0.477 | 0.343 | 0.248 | 0.683 | 48.0% |
| K-NET | PGA | 0.282 | 0.222 | 0.111 | 0.875 | 60.6% |

## Interpretation

The early waveform model clearly outperforms this bias-corrected OpenQuake reference on the balanced held-station split.

Use cautiously:

**This is enough for a first classical-reference check. It is not enough to claim superiority over a regionally tuned GMPE/GMM.**

## Files

- Script: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/scripts/run_openquake_pga_reference.py`
- OpenQuake output: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_balanced_station_10s/openquake_reference.csv`
- Comparison: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/ground_motion_balanced_station_10s/openquake_comparison.csv`
- Figure: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/figures/ground_motion_audit/openquake_reference_panel.png`
