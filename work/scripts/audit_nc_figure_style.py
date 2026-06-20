#!/usr/bin/env python3
"""Build a lightweight style audit for the current NC main figures."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


FIGURES = [
    ("Figure 1", Path("outputs/figures/figure1_dataset_task_matrix.png")),
    ("Figure 2", Path("outputs/figures/figure2_early_window_performance.png")),
    ("Figure 3", Path("outputs/figures/figure3_heldout_generalization.png")),
    ("Figure 4", Path("outputs/figures/figure4_classical_uncertainty.png")),
    ("Figure 5", Path("outputs/figures/figure5_residual_waveform_audit.png")),
    ("Figure 6", Path("outputs/figures/figure6_phase_label_audit.png")),
    ("Figure 7", Path("outputs/figures/nc_core_predictability_boundary.png")),
]
OUT_CSV = Path("outputs/nc_figure_style_audit.csv")
OUT_MD = Path("outputs/nc_figure_style_audit.md")
OUT_CONTACT = Path("outputs/figures/nc_main_figure_contact_sheet.png")


def main() -> None:
    rows = []
    thumbs = []
    for label, path in FIGURES:
        im = Image.open(path).convert("RGB")
        rows.append(
            {
                "figure": label,
                "path": str(path),
                "width_px": im.width,
                "height_px": im.height,
                "aspect_ratio": round(im.width / im.height, 3),
                "sha256_12": hashlib.sha256(path.read_bytes()).hexdigest()[:12],
            }
        )
        thumbs.append((label, path, im))

    out = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)
    build_contact_sheet(thumbs)
    write_summary(out)

    assert len(out) == 7
    assert out["width_px"].min() >= 1000
    assert OUT_CONTACT.exists()
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_CONTACT}")


def build_contact_sheet(thumbs: list[tuple[str, Path, Image.Image]]) -> None:
    OUT_CONTACT.parent.mkdir(parents=True, exist_ok=True)
    cell_w, cell_h = 760, 560
    pad, title_h = 28, 34
    cols = 2
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell_w + (cols + 1) * pad, rows * cell_h + (rows + 1) * pad), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for idx, (label, path, im) in enumerate(thumbs):
        r, c = divmod(idx, cols)
        x = pad + c * (cell_w + pad)
        y = pad + r * (cell_h + pad)
        draw.text((x, y), f"{label}: {path.name}", fill=(20, 20, 20), font=font)
        max_w, max_h = cell_w, cell_h - title_h
        scale = min(max_w / im.width, max_h / im.height)
        thumb = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))))
        tx = x + (max_w - thumb.width) // 2
        ty = y + title_h + (max_h - thumb.height) // 2
        sheet.paste(thumb, (tx, ty))
        draw.rectangle((x, y + title_h, x + max_w, y + cell_h), outline=(220, 220, 220), width=1)
    sheet.save(OUT_CONTACT)


def write_summary(out: pd.DataFrame) -> None:
    lines = [
        "# NC Figure Style Audit",
        "",
        "This audit records the current main-figure files after the redraw pass and provides a contact sheet for publication-style review.",
        "",
        "| Figure | Width | Height | Aspect | File |",
        "|---|---:|---:|---:|---|",
    ]
    for row in out.itertuples(index=False):
        lines.append(f"| {row.figure} | {row.width_px} | {row.height_px} | {row.aspect_ratio:.3f} | `{row.path}` |")
    lines.extend(
        [
            "",
            "Submission style target:",
            "- Use one sans-serif font family and consistent panel-title sizing across Figures 1-7.",
            "- Keep panel labels at the upper-left and avoid axis-title overlap.",
            "- Export final bitmap figures at >= 2000 px width or as vector/PDF where possible.",
            "- Keep Figure 7 as the style reference for compact line panels.",
            "",
            "Files:",
            f"- `{OUT_CSV}`",
            f"- `{OUT_CONTACT}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
