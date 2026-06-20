#!/usr/bin/env python3
"""Build a single residual and waveform audit packet figure."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("outputs/figures/ground_motion_audit")
INPUTS = [
    ("a", ROOT / "ground_motion_residual_diagnostic_panel.png"),
    ("b", ROOT / "instancegm_repeated_residual_audit_panel.png"),
    ("c", ROOT / "knet_pga_worst_residual_audit_panel.png"),
]
OUT = Path("outputs/figures/figure5_residual_waveform_audit.png")
SUMMARY = Path("outputs/figure5_residual_waveform_audit_summary.md")


def font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    target_width = 2250
    pad = 42
    label_font = font(54)
    title_font = font(72)

    panels = []
    for label, path in INPUTS:
        im = Image.open(path).convert("RGB")
        if im.width != target_width:
            scale = target_width / im.width
            im = im.resize((target_width, round(im.height * scale)), Image.Resampling.LANCZOS)
        panels.append((label, im))

    title_h = 120
    panel_label_h = 58
    total_h = title_h + sum(im.height + panel_label_h + pad for _, im in panels) + pad
    canvas = Image.new("RGB", (target_width + 2 * pad, total_h), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((pad, 24), "Residual and waveform audit", fill="black", font=title_font)
    y = title_h
    for label, im in panels:
        draw.text((pad, y + 8), label, fill="black", font=label_font)
        canvas.paste(im, (pad, y + panel_label_h))
        y += im.height + panel_label_h + pad
    canvas.save(OUT)

    SUMMARY.write_text(
        "\n".join(
            [
                "# Figure 5 Residual And Waveform Audit",
                "",
                "Date: 2026-06-18",
                "",
                "Figure 5 combines the residual diagnostic panel, repeated InstanceGM high-residual waveform cases, and K-NET PGA high-residual waveform cases.",
                "",
                "- The diagnostic panel shows mean and tail error reduction plus residual structure by distance, depth, and early amplitude.",
                "- The InstanceGM audit panel highlights records that recur across high-residual target lists.",
                "- The K-NET audit panel highlights independent PGA high-residual records.",
                "",
                f"Figure: `{OUT}`",
                "",
            ]
        )
    )
    print(f"wrote {OUT}")
    print(f"wrote {SUMMARY}")


if __name__ == "__main__":
    main()
