# PNWAccelerometers Unit Provenance Audit

Date: 2026-06-18

## Local Cache

- Dataset directory: `/Users/yojironoda/.seisbench/datasets/pnwaccelerometers`
- Metadata columns: 36
- Unit-like metadata columns: `[]`
- PGA/PGV-like metadata columns: `[]`
- HDF5 root attrs: `{}`
- HDF5 data_format keys: `['component_order']`
- HDF5 component_order: `ENZ`
- HDF5 unit field present: `False`

## External Provenance Checked

- SeisBench local class `PNWAccelerometers` cites Ni et al. (2023) and defines repository lookup, citation, and license only.
- The PNW-ML README lists `EN (accelerometer)` waveform and metadata files and says the files follow the SeisBench structure.
- The Seismica paper abstract states that the dataset includes high-gain channels and strong-motion EN channels resampled to 100 Hz.

Sources:

- https://github.com/niyiyu/PNW-ML
- https://seismica.library.mcgill.ca/article/view/368

## Conclusion

The local PNWAccelerometers cache supports an accelerometer-channel robustness check, but it does not provide waveform physical units or official PGA/PGV/SA targets. The current target should remain full-record peak horizontal waveform amplitude. It should stay in supplementary robustness material until waveform units and official ground-motion target definitions are documented.
