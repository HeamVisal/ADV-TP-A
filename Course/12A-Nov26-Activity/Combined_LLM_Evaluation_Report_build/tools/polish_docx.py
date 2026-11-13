"""Polish the pandoc DOCX: table borders, repeated header rows, header
shading, full-width tables, and a header/footer with page numbers.

Usage: python tools/polish_docx.py input.docx output.docx
Needs: python-docx.
"""

import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

source, target = sys.argv[1], sys.argv[2]
doc = Document(source)


def element(tag, **attrs):
    node = OxmlElement(tag)
    for key, value in attrs.items():
        node.set(qn(f"w:{key}"), value)
    return node


for table in doc.tables:
    tbl_pr = table._tbl.tblPr
    for old in tbl_pr.findall(qn("w:tblBorders")):
        tbl_pr.remove(old)
    borders = element("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        borders.append(
            element(f"w:{side}", val="single", sz="4", space="0", color="C9D1DA")
        )
    tbl_pr.append(borders)
    for old in tbl_pr.findall(qn("w:tblW")):
        tbl_pr.remove(old)
    tbl_pr.append(element("w:tblW", w="5000", type="pct"))  # 100% width
    margins = element("w:tblCellMar")
    for side in ("left", "right"):
        margins.append(element(f"w:{side}", w="80", type="dxa"))
    tbl_pr.append(margins)

    header = table.rows[0]
    tr_pr = header._tr.get_or_add_trPr()
    tr_pr.append(element("w:tblHeader", val="true"))  # repeat on each page
    for row in table.rows:
        row._tr.get_or_add_trPr().append(element("w:cantSplit", val="true"))
    for cell in header.cells:
        tc_pr = cell._tc.get_or_add_tcPr()
        tc_pr.append(element("w:shd", val="clear", color="auto", fill="E8EFF7"))
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(1)
                for run in paragraph.runs:
                    if run.font.size is None:
                        run.font.size = Pt(9)


def add_field(paragraph, code):
    run = paragraph.add_run()
    run._r.append(element("w:fldChar", fldCharType="begin"))
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f" {code} "
    run._r.append(instr)
    run._r.append(element("w:fldChar", fldCharType="separate"))
    run._r.append(OxmlElement("w:t"))
    run._r.append(element("w:fldChar", fldCharType="end"))


grey = RGBColor(0x6B, 0x74, 0x80)
for section in doc.sections:
    head = section.header.paragraphs[0]
    head.text = "Understanding LLM Evaluation: A Practical Guide to Ten Group Topics"
    for run in head.runs:
        run.font.size, run.font.color.rgb = Pt(8), grey
    foot = section.footer.paragraphs[0]
    foot.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    foot.add_run("Page ").font.size = Pt(8)
    add_field(foot, "PAGE")
    foot.add_run(" of ").font.size = Pt(8)
    add_field(foot, "NUMPAGES")
    for run in foot.runs:
        run.font.size, run.font.color.rgb = Pt(8), grey

doc.save(target)
print("Polished", target)
