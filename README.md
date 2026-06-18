# Early Strong-Motion Predictability Benchmark

This repository contains the lightweight evidence package and scripts for the Nature Communications route:

**Cross-regional predictability limits of strong shaking from the first seconds of P waves**

The repository intentionally excludes raw waveform caches and large generated HDF5/manifest files. Reproducibility scripts are in `work/scripts/`; current manuscript, evidence, figures, and verification reports are in `outputs/`.

Run the local evidence verifier from this directory:

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/verify_nc_evidence_package.py
```

Build the empirical predictability-boundary table:

```bash
/Users/yojironoda/miniforge3/envs/zhy/bin/python work/scripts/build_predictability_boundary_table.py
```

Some checks depend on local SeisBench and K-NET data caches that are not redistributed here.
