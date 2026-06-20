#!/usr/bin/env python3
"""Audit local PNWAccelerometers unit provenance."""

from __future__ import annotations

from pathlib import Path

import h5py
import pandas as pd


DATASET_DIR = Path("/Users/yojironoda/.seisbench/datasets/pnwaccelerometers")
OUT = Path("outputs/pnw_unit_provenance_audit.md")


def main() -> None:
    metadata = pd.read_csv(DATASET_DIR / "metadata.csv", nrows=5)
    unit_cols = [c for c in metadata.columns if "unit" in c.lower()]
    gm_cols = [c for c in metadata.columns if c.lower() in {"pga", "pgv"} or "pga" in c.lower() or "pgv" in c.lower()]
    with h5py.File(DATASET_DIR / "waveforms.hdf5", "r") as h5:
        root_attrs = dict(h5.attrs)
        data_format_keys = list(h5["data_format"].keys())
        component_order = h5["data_format/component_order"][()].decode()
        has_unit = "unit" in data_format_keys or "unit" in root_attrs

    lines = [
        "# PNWAccelerometers Unit Provenance Audit",
        "",
        "Date: 2026-06-18",
        "",
        "## Local Cache",
        "",
        f"- Dataset directory: `{DATASET_DIR}`",
        f"- Metadata columns: {len(metadata.columns)}",
        f"- Unit-like metadata columns: `{unit_cols}`",
        f"- PGA/PGV-like metadata columns: `{gm_cols}`",
        f"- HDF5 root attrs: `{root_attrs}`",
        f"- HDF5 data_format keys: `{data_format_keys}`",
        f"- HDF5 component_order: `{component_order}`",
        f"- HDF5 unit field present: `{has_unit}`",
        "",
        "## External Provenance Checked",
        "",
        "- SeisBench local class `PNWAccelerometers` cites Ni et al. (2023) and defines repository lookup, citation, and license only.",
        "- The PNW-ML README lists `EN (accelerometer)` waveform and metadata files and says the files follow the SeisBench structure.",
        "- The Seismica paper abstract states that the dataset includes high-gain channels and strong-motion EN channels resampled to 100 Hz.",
        "",
        "Sources:",
        "",
        "- https://github.com/niyiyu/PNW-ML",
        "- https://seismica.library.mcgill.ca/article/view/368",
        "",
        "## Conclusion",
        "",
        "The local PNWAccelerometers cache supports an accelerometer-channel robustness check, but it does not provide waveform physical units or official PGA/PGV/SA targets. The current target should remain full-record peak horizontal waveform amplitude. It should stay in supplementary robustness material until waveform units and official ground-motion target definitions are documented.",
        "",
    ]
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
