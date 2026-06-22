#!/usr/bin/env python3
"""Build lightweight PDF drafts from the NC manuscript markdown."""

from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image as PdfImage
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer
from PIL import Image as PillowImage


SOURCE = Path("outputs/nc_manuscript_main_v1.md")
OFFICIAL_MD = Path("outputs/nc_manuscript_nc_official_format_v1.md")
PDFS = [
    Path("outputs/pdf/nc_manuscript_main_v1.pdf"),
    Path("outputs/pdf/nc_manuscript_nc_official_template_v1.pdf"),
]
OFFICIAL_PDF = Path("outputs/pdf/nc_manuscript_nc_official_format_v1.pdf")
OFFICIAL_ABSTRACT = (
    "Earthquake early warning depends on the first seconds of the P wave. "
    "Those seconds can reveal source, path and site response, but the cross-regional limit for forecasting damaging ground motion is unclear. "
    "We build a public event-station benchmark for PGA, PGV and spectral acceleration using 1, 2, 3, 5 and 10 s windows after P arrival. "
    "Across 2,460,425 manifest records, early-waveform features reduce held-station error relative to source-path baselines, including 35.5% for InstanceGM PGA, 52.6% for InstanceGM PGV and 49.9% for K-NET PGA at 10 s. "
    "Independent AQ2009GM, CWA and ESM checks keep this pattern, and gains remain positive in bootstrap, source-path support and strongest-motion subsets. "
    "Regional transfer exposes the boundary: source-region conformal intervals under-cover target regions, and target-domain calibration restores coverage with wide intervals. "
    "The result is a measurable curve linking P-window length, tail risk and regional uncertainty."
)
OFFICIAL_SECTIONS = [
    ("Introduction", "Introduction"),
    ("Results", "Results"),
    ("Discussion", "Discussion"),
    ("Methods", "Methods"),
    ("Data availability", "Data Availability"),
    ("Code availability", "Code Availability"),
    ("References", "References"),
    ("Acknowledgements", "Acknowledgements"),
    ("Author contributions", "Author Contributions"),
    ("Competing interests", "Competing Interests"),
    ("Figure legends", "Figures"),
]
FIGURE_IMAGES = {
    "Figure 1 |": Path("outputs/figures/figure1_dataset_task_matrix.png"),
    "Figure 2 |": Path("outputs/figures/figure2_early_window_performance.png"),
    "Figure 3 |": Path("outputs/figures/figure3_heldout_generalization.png"),
    "Figure 4 |": Path("outputs/figures/figure4_classical_uncertainty.png"),
    "Figure 5 |": Path("outputs/figures/figure5_residual_waveform_audit.png"),
    "Figure 6 |": Path("outputs/figures/figure6_phase_label_audit.png"),
    "Figure 7 |": Path("outputs/figures/nc_core_predictability_boundary.png"),
    "Extended Data Figure 1 |": Path("outputs/figures/extended_waveform_case_audit.png"),
    "Extended Data Figure 2 |": Path("outputs/figures/ground_motion_audit/residual_mechanism_audit.png"),
}


def register_fonts() -> tuple[str, str]:
    regular = "/System/Library/Fonts/Supplemental/Arial.ttf"
    bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    if Path(regular).exists() and Path(bold).exists():
        pdfmetrics.registerFont(TTFont("NCArial", regular))
        pdfmetrics.registerFont(TTFont("NCArialBold", bold))
        return "NCArial", "NCArialBold"
    return "Helvetica", "Helvetica-Bold"


def clean_inline(text: str) -> str:
    text = text.replace("`", "")
    parts = re.split(r"(\*\*.*?\*\*)", text)
    out = []
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            escaped = html.escape(part[2:-2])
            escaped = re.sub(r"\^([0-9,*]+)", r"<super>\1</super>", escaped)
            out.append(f"<b>{escaped}</b>")
        else:
            escaped = html.escape(part)
            escaped = re.sub(r"\^([0-9,*]+)", r"<super>\1</super>", escaped)
            out.append(escaped)
    return "".join(out)


def figure_image_for(line: str) -> Path | None:
    plain = line.replace("**", "")
    for prefix, path in FIGURE_IMAGES.items():
        if plain.startswith(prefix):
            return path
    return None


def scaled_image(path: Path) -> PdfImage:
    with PillowImage.open(path) as img:
        width, height = img.size
    max_width = 6.5 * inch
    max_height = 7.4 * inch
    scale = min(max_width / width, max_height / height)
    return PdfImage(str(path), width=width * scale, height=height * scale)


def build_story(text: str, styles: dict[str, ParagraphStyle]) -> list:
    story = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if story and isinstance(story[-1], PageBreak):
                continue
            story.append(Spacer(1, 0.07 * inch))
            continue
        if line.startswith("# "):
            story.append(Paragraph(clean_inline(line[2:]), styles["Title"]))
            story.append(Spacer(1, 0.15 * inch))
        elif line.startswith("## "):
            if line == "## Figures":
                story.append(PageBreak())
                continue
            story.append(Spacer(1, 0.10 * inch))
            story.append(Paragraph(clean_inline(line[3:]), styles["Heading2"]))
        elif line.startswith("### "):
            story.append(Spacer(1, 0.06 * inch))
            story.append(Paragraph(clean_inline(line[4:]), styles["Heading3"]))
        elif line.startswith("- "):
            story.append(Paragraph(f"&bull; {clean_inline(line[2:])}", styles["Bullet"]))
        elif re.match(r"^\d+\. ", line):
            story.append(Paragraph(clean_inline(line), styles["Bullet"]))
        else:
            figure_path = figure_image_for(line)
            if figure_path:
                if story and not isinstance(story[-1], PageBreak):
                    story.append(PageBreak())
                story.append(Paragraph(clean_inline(line), styles["Body"]))
                story.append(Spacer(1, 0.08 * inch))
                story.append(scaled_image(figure_path))
            else:
                story.append(Paragraph(clean_inline(line), styles["Body"]))
    return story


def make_styles() -> dict[str, ParagraphStyle]:
    regular, bold = register_fonts()
    base = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle(
            "NCTitle",
            parent=base["Title"],
            fontName=bold,
            fontSize=18,
            leading=22,
            alignment=0,
            spaceAfter=8,
        ),
        "Heading2": ParagraphStyle(
            "NCHeading2",
            parent=base["Heading2"],
            fontName=bold,
            fontSize=13,
            leading=16,
            textColor=colors.black,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "Heading3": ParagraphStyle(
            "NCHeading3",
            parent=base["Heading3"],
            fontName=bold,
            fontSize=11,
            leading=14,
            textColor=colors.black,
            spaceBefore=6,
            spaceAfter=3,
        ),
        "Body": ParagraphStyle(
            "NCBody",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=9.3,
            leading=12.2,
            spaceAfter=4,
        ),
        "Bullet": ParagraphStyle(
            "NCBullet",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=9.3,
            leading=12.2,
            leftIndent=14,
            firstLineIndent=-10,
            spaceAfter=3,
        ),
    }


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(7.5 * inch, 0.45 * inch, f"{doc.page}")
    canvas.restoreState()


def build_pdf(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(path),
        pagesize=LETTER,
        rightMargin=0.85 * inch,
        leftMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.7 * inch,
        title="NC manuscript draft",
    )
    story = build_story(SOURCE.read_text(), make_styles())
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def sections(markdown: str) -> dict[str, str]:
    matches = list(re.finditer(r"^## (.+)$", markdown, re.MULTILINE))
    out: dict[str, str] = {}
    for idx, match in enumerate(matches):
        start = match.end() + 1
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(markdown)
        out[match.group(1)] = markdown[start:end].strip()
    return out


def front_matter(markdown: str) -> str:
    abstract = re.search(r"^## Abstract$", markdown, re.MULTILINE)
    if not abstract:
        return ""
    lines = markdown[: abstract.start()].splitlines()[1:]
    return "\n".join(line for line in lines).strip()


def build_official_markdown() -> str:
    source = SOURCE.read_text()
    title = source.splitlines()[0].lstrip("# ").strip()
    front = front_matter(source)
    sec = sections(source)
    parts = [
        f"# {title}",
        "",
        front,
        "",
        "## Abstract",
        "",
        OFFICIAL_ABSTRACT,
        "",
    ]
    for source_name, heading in OFFICIAL_SECTIONS:
        parts.extend([f"## {heading}", "", sec[source_name], ""])
    return "\n".join(parts).strip() + "\n"


def build_official_pdf() -> None:
    OFFICIAL_MD.write_text(build_official_markdown())
    path = OFFICIAL_PDF
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(path),
        pagesize=LETTER,
        rightMargin=0.85 * inch,
        leftMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.7 * inch,
        title="Nature Communications official format draft",
    )
    story = build_story(OFFICIAL_MD.read_text(), make_styles())
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    for path in PDFS:
        build_pdf(path)
        text = subprocess.check_output(["pdftotext", str(path), "-"], text=True)
        assert "coverage gaps of 0.432 and 0.602" in text
        assert "under-cover target regions" in text
        info = subprocess.check_output(["pdfinfo", str(path)], text=True)
        pages = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
        print(f"wrote {path} ({pages.group(1) if pages else '?'} pages)")
    build_official_pdf()
    text = subprocess.check_output(["pdftotext", str(OFFICIAL_PDF), "-"], text=True)
    assert "A public-data boundary for forecasting strong shaking" in text
    assert "measurable curve" in text
    assert text.index("References") < text.index("Acknowledgements")
    assert "Figure 8 |" not in text
    assert "Figure legends" not in text
    assert r"\hat" not in text
    info = subprocess.check_output(["pdfinfo", str(OFFICIAL_PDF)], text=True)
    pages = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
    print(f"wrote {OFFICIAL_MD}")
    print(f"wrote {OFFICIAL_PDF} ({pages.group(1) if pages else '?'} pages)")


if __name__ == "__main__":
    main()
