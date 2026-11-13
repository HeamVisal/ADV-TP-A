"""Create tools/reference.docx: the Word style template used by pandoc.

Run once (or after changing styles):  python tools/make_reference_docx.py
Needs: pypandoc_binary, python-docx.
"""

import subprocess
from pathlib import Path

import pypandoc
from docx import Document
from docx.enum.text import WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor

TOOLS = Path(__file__).resolve().parent
OUT = TOOLS / "reference.docx"
ACCENT = RGBColor(0x1F, 0x4E, 0x79)
BODY_FONT, HEAD_FONT, CODE_FONT = "Cambria", "Calibri", "Courier New"
KHMER_FONT = "Khmer UI"  # complex-script font; Word substitutes if missing

default = subprocess.run(
    [pypandoc.get_pandoc_path(), "--print-default-data-file", "reference.docx"],
    capture_output=True,
    check=True,
).stdout
OUT.write_bytes(default)
doc = Document(OUT)


def set_fonts(style, latin, size=None, bold=None, color=None, italic=None):
    font = style.font
    font.name = latin
    if size:
        font.size = Pt(size)
    if bold is not None:
        font.bold = bold
    if italic is not None:
        font.italic = italic
    if color is not None:
        font.color.rgb = color
    rpr = style.element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia"):
        fonts.set(qn(attr), latin)
    fonts.set(qn("w:cs"), KHMER_FONT)
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        fonts.attrib.pop(qn(attr), None)


def shade(style, fill):
    ppr = style.element.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    ppr.append(shd)


def left_border(style, color, size=12):
    ppr = style.element.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    for key, value in (
        ("val", "single"),
        ("sz", str(size)),
        ("space", "6"),
        ("color", color),
    ):
        left.set(qn(f"w:{key}"), value)
    borders.append(left)
    ppr.append(borders)


styles = doc.styles
NAMES = {s.name for s in styles}
for name, kind in (
    ("Source Code", 1),
    ("Block Text", 1),
    ("Table Caption", 1),
    ("Compact", 1),
    ("First Paragraph", 1),
    ("Title", 1),
    ("Subtitle", 1),
    ("Verbatim Char", 2),
):
    if name not in NAMES:
        styles.add_style(name, kind)  # 1 = paragraph style, 2 = character style
for name in ("Normal", "Body Text", "First Paragraph", "Compact"):
    if name in [s.name for s in styles]:
        set_fonts(styles[name], BODY_FONT, size=10.5)
        pf = styles[name].paragraph_format
        pf.space_after = Pt(5)
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        pf.line_spacing = 1.12
styles["Compact"].paragraph_format.space_after = Pt(2)

for level, size in ((1, 18), (2, 13.5), (3, 11.5)):
    style = styles[f"Heading {level}"]
    set_fonts(style, HEAD_FONT, size=size, bold=True, color=ACCENT)
    style.paragraph_format.space_before = Pt(14 if level > 1 else 0)
    style.paragraph_format.space_after = Pt(5)
    style.paragraph_format.keep_with_next = True
styles["Heading 1"].paragraph_format.page_break_before = True

set_fonts(styles["Title"], HEAD_FONT, size=26, bold=True, color=ACCENT)
styles["Title"].paragraph_format.space_before = Pt(90)
styles["Title"].paragraph_format.space_after = Pt(12)
set_fonts(styles["Subtitle"], BODY_FONT, size=13, color=RGBColor(0x56, 0x60, 0x6B))
styles["Subtitle"].paragraph_format.space_after = Pt(18)

# Code blocks and inline code.
set_fonts(styles["Source Code"], CODE_FONT, size=8.5)
styles["Source Code"].paragraph_format.space_after = Pt(0)
shade(styles["Source Code"], "F5F6F8")
left_border(styles["Source Code"], "8AA4C0")
set_fonts(styles["Verbatim Char"], CODE_FONT, size=9)

# Callouts (Markdown block quotes).
set_fonts(styles["Block Text"], BODY_FONT, size=10)
shade(styles["Block Text"], "F4F7FB")
left_border(styles["Block Text"], "1F4E79", size=18)

# Captions above tables.
set_fonts(
    styles["Table Caption"],
    HEAD_FONT,
    size=9,
    italic=True,
    color=RGBColor(0x56, 0x60, 0x6B),
)
styles["Table Caption"].paragraph_format.keep_with_next = True

# Table of contents heading and entries.
toc_heading = (
    styles.add_style("TOC Heading", 1)
    if "TOC Heading" not in [s.name for s in styles]
    else styles["TOC Heading"]
)
set_fonts(toc_heading, HEAD_FONT, size=16, bold=True, color=ACCENT)
toc_heading.paragraph_format.page_break_before = True
toc_heading.paragraph_format.space_after = Pt(10)
for level in (1, 2):
    name = f"TOC {level}"
    style = (
        styles[name] if name in [s.name for s in styles] else styles.add_style(name, 1)
    )
    set_fonts(style, HEAD_FONT, size=10 if level == 1 else 9, bold=level == 1)
    style.paragraph_format.left_indent = Mm(0 if level == 1 else 6)
    style.paragraph_format.space_after = Pt(1 if level == 2 else 2)
    style.paragraph_format.space_before = Pt(4 if level == 1 else 0)

# A4 page with 20 mm / 18 mm margins.
for section in doc.sections:
    section.page_width, section.page_height = Mm(210), Mm(297)
    section.top_margin = section.bottom_margin = Mm(20)
    section.left_margin = section.right_margin = Mm(18)

doc.save(OUT)
print("Wrote", OUT)
