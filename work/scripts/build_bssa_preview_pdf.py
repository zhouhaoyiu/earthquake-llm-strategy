#!/usr/bin/env python3
"""Build a BSSA-style review PDF preview from the current manuscript draft."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from PIL import Image as PillowImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as PdfImage
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from build_nc_manuscript_pdf import (
    FIGURE_IMAGES,
    OFFICIAL_ABSTRACT,
    SOURCE,
    clean_inline,
    register_fonts,
    sections,
)


BSSA_MD = Path("outputs/bssa_manuscript_preview_v1.md")
BSSA_PDF = Path("outputs/pdf/bssa_manuscript_preview_v1.pdf")
BODY_SECTIONS = [
    ("Introduction", "Introduction"),
    ("Results", "Results"),
    ("Discussion", "Conclusions"),
    ("Methods", "Methods"),
]
KEY_POINTS = [
    "Early P waves add measurable information for strong-motion prediction at unseen stations.",
    "Regional transfer requires target calibration to keep uncertainty intervals reliable.",
    "Strong-tail audits expose the remaining limit of early-warning predictability.",
]


def polish_for_bssa(text: str) -> str:
    replacements = {
        "We use that joint behaviour to define a predictability boundary rather than a single best model score.": "We use that joint behaviour to define a predictability boundary, the quantity needed for deployment.",
        "We therefore audit a K-NET pre-peak subset where the early horizontal peak remains below 80% of the observed PGA.": "We audit a K-NET pre-peak subset where the early horizontal peak remains below 80% of the observed PGA.",
        "The benchmark therefore reports both the information gain and the records where early P motion leaves large unexplained error.": "The benchmark reports both the information gain and the records where early P motion leaves large unexplained error.",
        "The streaming validation covers all 254 local manifest chunks and retains compact feature tables rather than the raw chunk files.": "The streaming validation covers all 254 local manifest chunks, retains compact feature tables and removes raw chunk files after extraction.",
        "These limitations are part of the proposed benchmark rather than loose ends to hide.": "These limitations define the proposed benchmark.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def bssa_markdown() -> str:
    sec = sections(SOURCE.read_text())
    title = SOURCE.read_text().splitlines()[0].lstrip("# ").strip()
    figure_lines = [
        line.replace("**", "")
        for line in sec["Figure legends"].splitlines()
        if line.strip().startswith("**")
    ]
    parts = [
        f"# {title}",
        "",
        "[Author names]",
        "",
        "[One main affiliation per author]",
        "",
        "Corresponding author: [name, complete postal address, email]",
        "",
        "## Key Points",
        "",
        *[f"- {point}" for point in KEY_POINTS],
        "",
        "## Abstract",
        "",
        OFFICIAL_ABSTRACT,
        "",
    ]
    for source_name, heading in BODY_SECTIONS:
        parts.extend([f"## {heading}", "", sec[source_name], ""])
    parts.extend(
        [
            "## Data and Resources",
            "",
            "This preview uses public strong-motion sources including InstanceGM, K-NET, European Strong-Motion records and AQ2009GM. "
            "Derived feature tables, split manifests, scripts and figure source tables will be released with a clean repository or archival deposit before any submission. "
            "Raw waveform files should be obtained from the original providers. Provider URLs, final access dates and repository DOI are placeholders in this preview and must be completed before submission.",
            "",
            "## Declaration of Competing Interests",
            "",
            "The authors declare no competing interests. This statement must be confirmed by all authors before submission.",
            "",
            "## Acknowledgments",
            "",
            "[To be completed.]",
            "",
            "## References",
            "",
            "References must be completed from the literature manager before submission. Do not fabricate bibliographic entries. Required groups include earthquake early warning, P-wave ground-motion prediction, ground-motion models, conformal prediction, K-NET, InstanceGM, European Strong-Motion records and AQ2009GM.",
            "",
            "## Figures",
            "",
        ]
    )
    for line in figure_lines:
        parts.extend([line, f"Alt text: {line.split('|', 1)[-1].strip()}", ""])
    return polish_for_bssa("\n".join(parts).strip()) + "\n"


def styles() -> dict[str, ParagraphStyle]:
    regular, bold = register_fonts()
    base = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle(
            "BSSATitle",
            parent=base["Title"],
            fontName=bold,
            fontSize=14,
            leading=24,
            alignment=0,
            spaceAfter=12,
        ),
        "Heading": ParagraphStyle(
            "BSSAHeading",
            parent=base["Heading2"],
            fontName=bold,
            fontSize=12,
            leading=24,
            textColor=colors.black,
            spaceBefore=12,
            spaceAfter=0,
        ),
        "Subheading": ParagraphStyle(
            "BSSASubheading",
            parent=base["Heading3"],
            fontName=bold,
            fontSize=12,
            leading=24,
            textColor=colors.black,
            spaceBefore=0,
            spaceAfter=0,
        ),
        "Body": ParagraphStyle(
            "BSSABody",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=12,
            leading=24,
            spaceAfter=0,
        ),
        "Bullet": ParagraphStyle(
            "BSSABullet",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=12,
            leading=24,
            leftIndent=18,
            firstLineIndent=-12,
            spaceAfter=0,
        ),
    }


def image_for(line: str) -> Path | None:
    for prefix, path in FIGURE_IMAGES.items():
        if line.startswith(prefix):
            return path
    return None


def scaled(path: Path) -> PdfImage:
    with PillowImage.open(path) as img:
        width, height = img.size
    scale = min((6.5 * inch) / width, (5.9 * inch) / height)
    return PdfImage(str(path), width=width * scale, height=height * scale)


def story(markdown: str, ss: dict[str, ParagraphStyle]) -> list:
    out = []
    in_figures = False
    first_figure = True
    for raw in markdown.splitlines():
        line = raw.strip()
        if not line:
            out.append(Spacer(1, 0.01 * inch))
        elif line.startswith("# "):
            out.append(Paragraph(clean_inline(line[2:]), ss["Title"]))
        elif line.startswith("## "):
            if line == "## Figures":
                out.append(PageBreak())
                in_figures = True
            out.append(Paragraph(clean_inline(line[3:]), ss["Heading"]))
        elif line.startswith("### "):
            out.append(Paragraph(clean_inline(line[4:]), ss["Subheading"]))
        elif line.startswith("- "):
            out.append(Paragraph(f"&bull; {clean_inline(line[2:])}", ss["Bullet"]))
        else:
            fig = image_for(line)
            if fig:
                if in_figures and not first_figure:
                    out.append(PageBreak())
                first_figure = False
                out.append(scaled(fig))
                out.append(Spacer(1, 0.12 * inch))
                out.append(Paragraph(clean_inline(line.replace(" | ", ". ")), ss["Body"]))
            else:
                out.append(Paragraph(clean_inline(line), ss["Body"]))
    return out


def page_marks(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(4.25 * inch, 0.5 * inch, str(doc.page))
    top = 10.0 * inch
    # ponytail: visual continuous line numbers for review PDF; exact text-line mapping needs LaTeX/Word.
    for idx in range(27):
        canvas.drawRightString(0.75 * inch, top - idx * 24, str((doc.page - 1) * 27 + idx + 1))
    canvas.restoreState()


def main() -> None:
    BSSA_MD.write_text(bssa_markdown())
    BSSA_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(BSSA_PDF),
        pagesize=LETTER,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
        title="BSSA manuscript preview",
    )
    doc.build(story(BSSA_MD.read_text(), styles()), onFirstPage=page_marks, onLaterPages=page_marks)
    text = subprocess.check_output(["pdftotext", str(BSSA_PDF), "-"], text=True)
    info = subprocess.check_output(["pdfinfo", str(BSSA_PDF)], text=True)
    pages = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
    assert "Key Points" in text
    assert "Data and Resources" in text
    assert "Declaration of Competing Interests" in text
    assert "Alt text:" in text
    print(f"wrote {BSSA_MD}")
    print(f"wrote {BSSA_PDF} ({pages.group(1) if pages else '?'} pages)")


if __name__ == "__main__":
    main()
