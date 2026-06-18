# Unified Manifest Summary

Date: 2026-06-11

## Files

- Unified manifest: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/unified_manifest/unified_manifest.csv.gz`
- Summary JSON: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/unified_manifest/unified_manifest_summary.json`
- Builder script: `/Users/yojironoda/Documents/Codex/2026-06-11/earthquake-llm-strategy/work/scripts/build_unified_manifest.py`

The manifest is stored under `work/` because it is an intermediate data product. The compressed CSV is about 135 MB.

## Scope

The unified manifest combines four local waveform sources:

| Dataset | Rows | Phase rows | Detection rows | Ground-motion rows |
|---|---:|---:|---:|---:|
| STEAD | 1,265,657 | 1,030,231 | 1,265,657 | 0 |
| InstanceGM | 1,159,249 | 1,159,249 | 1,159,249 | 1,159,223 |
| Iquique | 13,400 | 13,400 | 13,400 | 0 |
| K-NET | 22,119 | 22,119 | 22,119 | 22,119 |
| Total | 2,460,425 | 2,224,999 | 2,460,425 | 1,181,342 |

Split counts:

- STEAD: train 1,075,808; val 63,283; test 126,566
- InstanceGM: train 699,980; val 115,027; test 344,242
- Iquique: train 8,040; val 1,340; test 4,020
- K-NET: train 17,447; val 2,490; test 2,182

## Schema

The manifest includes:

- identity: `global_id`, `dataset`, `record_id`, `event_id`
- split: `original_split`, `split`
- HDF5 location: `waveform_store`, `hdf5_key`, `hdf5_index`, `sample_start`, `sample_stop`
- waveform metadata: `component_order`, `dimension_order`, `n_components`, `n_samples`, `sampling_rate_hz`
- phase labels: `p_pick_sample`, `s_pick_sample`, `p_pick_sec`, `s_pick_sec`
- source/path/site metadata: magnitude, depth, location, distance, station location, station elevation, Vs30 when available
- strong-motion targets: `pga_cmps2`, `pgv_cmps`, `sa03_cmps2`, `sa10_cmps2`, `sa30_cmps2`
- task flags: `has_phase_task`, `has_detection_task`, `has_ground_motion_task`
- provenance: `source_metadata_path`, `unit_notes`

## Read Rule

For K-NET:

```python
arr = h5[row.hdf5_key][:, sample_start:sample_stop]
```

For SeisBench HDF5 datasets:

```python
arr = h5[row.hdf5_key][int(row.hdf5_index), :, sample_start:sample_stop]
```

This slicing is required. Iquique bucket rows can be longer than the specific `trace_name` window.

## Validation

Checks completed:

- Total rows: 2,460,425
- No missing `global_id`, `waveform_store`, `hdf5_key`, `n_samples`, `component_order`, or `split`
- HDF5 readback passed for STEAD, InstanceGM, Iquique, and K-NET
- Iquique readback correctly returns the sliced window length
- K-NET readback uses variable-length HDF5 records and all 22,119 records have complete `ZNE` components

## Caveats

K-NET `pga_gal` is treated as `pga_cmps2` because 1 gal equals 1 cm/s/s, but the raw package documentation should still be checked before publication.

InstanceGM waveforms and targets are preserved from the SeisBench cache. Downstream scripts should verify any unit conversion before comparing directly with K-NET.

The current manifest is an experimental index, not a published dataset release. Before manuscript use, add checksums and a frozen version tag.
