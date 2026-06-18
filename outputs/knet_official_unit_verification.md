# K-NET Official Unit Verification

Date: 2026-06-17

## Finding

The local K-NET `pga_gal` target can be treated as `cm/s^2` for ground-motion regression because **1 gal = 1 cm/s^2**.

Official documentation support:

- NIED K-NET CSV format: acceleration waveform physical values are recorded in **gal**.
- NIED FAQ: `1 gal = 1 cm/s^2`.
- NIED K-NET ASCII format: maximum acceleration is computed from acceleration time series values after subtracting the average offset over the full data length.

## Local Consequence

The unified manifest mapping:

```text
K-NET pga_gal -> pga_cmps2
```

is scientifically reasonable.

Keep the caveat that local BSON package provenance and any preprocessing steps should be described clearly in Methods.

## Files Affected

Current local notes still contain conservative wording:

- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/scripts/convert_knet_bson.py`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/scripts/build_unified_manifest.py`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/knet_conversion_summary.md`
- `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/outputs/unified_manifest_summary.md`

Do not rewrite raw HDF5 attributes in place. If publication-ready conversion is needed, rerun conversion with updated attrs and a citation note.

## Sources

- NIED K-NET CSV format: https://www.kyoshin.bosai.go.jp/en/knetcsv/
- NIED K-NET ASCII format: https://www.kyoshin.bosai.go.jp/en/knetascii/
- NIED FAQ: https://www.kyoshin.bosai.go.jp/en/faq/
- NIED K-NET/KiK-net overview: https://www.kyoshin.bosai.go.jp/en/
