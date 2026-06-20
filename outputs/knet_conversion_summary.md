# K-NET Conversion Summary

Date: 2026-06-11

## Inputs

- Raw directory: `/Users/yojironoda/Downloads/s7rk7bj3zn-1/knet_1530`
- Header BSON: `/Users/yojironoda/Downloads/s7rk7bj3zn-1/knet_1530/header.bson`
- Accelerogram BSON: `/Users/yojironoda/Downloads/s7rk7bj3zn-1/knet_1530/accelerogram.bson`
- Converter: `work/scripts/convert_knet_bson.py`
- Python: `/Users/yojironoda/miniforge3/envs/zhy/bin/python`

## Outputs

- Full manifest: `work/knet_converted/knet_full_manifest.csv`
- Full HDF5 waveform file: `work/knet_converted/knet_full_waveforms.hdf5`
- Full conversion report: `work/knet_converted/knet_full_convert_report.json`
- Sample manifest/HDF5/report are also in `work/knet_converted`.

The full HDF5 file is kept under `work/` because it is a 2.0 GB intermediate data product.

## Verified Results

- Manifest rows: 22,119
- HDF5 records: 22,119
- Accelerogram components processed: 66,357
- Complete records with `UD`, `NS`, and `EW`: 22,119
- Component mapping: `UD -> Z`, `NS -> N`, `EW -> E`
- Output component order: `ZNE`
- Split counts:
  - train: 17,447
  - val: 2,490
  - test: 2,182
- P picks: 21,141 records
- S picks: 22,119 records
- Magnitude range: 2.8 to 8.0
- Sample count range per component: 3,000 to 113,600
- Median sample count per component: 11,900
- HDF5 readback check: passed on short, median-length, and longest records

## Format

The HDF5 file uses variable-length per-record datasets:

- Group: `/waveforms`
- Record key pattern: `/waveforms/<record_id>`
- Dataset shape: `(3, n_samples)`
- Dimension order: `CW`
- Component order: `ZNE`

The manifest includes an `hdf5_key` column so each row can directly load its waveform dataset.

## Important Notes

The raw K-NET records are not uniform 119-second windows. A fixed-size conversion would either truncate long records or waste large amounts of space. The final converter preserves each record's original sample length.

The waveform unit is marked `gal_unverified`. It is consistent with the acceleration/PGA context, but the exact unit and scaling should be checked against K-NET documentation before publication.

The split is event-based using a deterministic hash of `event_id`, so traces from the same event stay in the same split.

## Command

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/convert_knet_bson.py \
  --input-dir /Users/yojironoda/Downloads/s7rk7bj3zn-1/knet_1530 \
  --out-dir work/knet_converted \
  --mode full \
  --progress 10000
```
