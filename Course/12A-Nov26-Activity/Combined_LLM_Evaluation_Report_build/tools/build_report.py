"""Build tools for Combined_LLM_Evaluation_Report.md.

The Markdown file is the single editable source. This script:

  toc      rewrite the clickable table of contents inside the Markdown
  fmt      format the ```python blocks with `ruff format`
  widths   set table column proportions (pandoc dash counts) from content
  code     extract each chapter's ```python blocks into code/chNN_*.py
  check    compare each "Executed output" block with outputs/chNN_*.txt
  sync     replace "Executed output" blocks with the real outputs
  links    check internal #links against the generated heading ids
  html     write build/report.html (MathML, page-number placeholders)
  pdf      print the HTML to PDF twice, filling in TOC page numbers
  docx     write the Word file with a real TOC field (see update_docx.py)

Typical use from the build folder (see README.md):
  python tools/build_report.py toc code
  python tools/run_examples.py
  python tools/build_report.py check html pdf docx
"""

import difflib
import html
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

BUILD = Path(__file__).resolve().parent.parent  # ..._build/
ACTIVITY = BUILD.parent  # 12A-Nov26-Activity/
SOURCE = ACTIVITY / "Combined_LLM_Evaluation_Report.md"
PDF_OUT = ACTIVITY / "Combined_LLM_Evaluation_Report.pdf"
DOCX_OUT = ACTIVITY / "Combined_LLM_Evaluation_Report.docx"
WORK = BUILD / "build"
CODE = BUILD / "code"
OUTPUTS = BUILD / "outputs"
TOOLS = BUILD / "tools"

TOC_START, TOC_END = "<!-- TOC START -->", "<!-- TOC END -->"
CODE_NAMES = {
    1: "ch01_exact_match",
    2: "ch02_accuracy",
    3: "ch03_precision_recall_f1",
    4: "ch04_bleu",
    5: "ch05_rouge",
    6: "ch06_meteor",
    7: "ch07_bertscore",
    8: "ch08_wer",
    9: "ch09_cer",
    10: "ch10_compare",
}
FENCE = re.compile(r"^```(\w*)\s*$")


# --------------------------------------------------------------------------
# Markdown helpers
# --------------------------------------------------------------------------
def read_source():
    return SOURCE.read_text(encoding="utf-8")


def iter_lines_outside_code(text):
    """Yield (index, line, in_code) for every line."""
    in_code = False
    for i, line in enumerate(text.split("\n")):
        if FENCE.match(line):
            in_code = not in_code
            yield i, line, True
            continue
        yield i, line, in_code


def gfm_id(title, seen):
    """GitHub-style heading id (also used by pandoc's gfm_auto_identifiers)."""
    plain = re.sub(r"`([^`]*)`", r"\1", title)
    plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", plain)
    plain = plain.lower()
    plain = "".join(
        ch for ch in plain if ch in " -_" or unicodedata.category(ch)[0] in "LNM"
    )
    slug = plain.replace(" ", "-")
    base, n = slug, 0
    while slug in seen:
        n += 1
        slug = f"{base}-{n}"
    seen.add(slug)
    return slug


def headings(text):
    """Return a list of (level, title, id) for ATX headings."""
    seen, result = set(), []
    for _, line, in_code in iter_lines_outside_code(text):
        if in_code:
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if m:
            title = m.group(2)
            result.append((len(m.group(1)), title, gfm_id(title, seen)))
    return result


def toc_entries(text):
    """Entries after the 'Table of Contents' heading; skip the title and TOC."""
    entries, started = [], False
    for level, title, hid in headings(text):
        if title == "Table of Contents":
            started = True
            continue
        if not started or level > 2:
            continue
        entries.append((level, title, hid))
    # Front-matter H2 sections before the first H1 are shown at top level.
    first_h1 = next(i for i, e in enumerate(entries) if e[0] == 1)
    return [(1 if i < first_h1 else lvl, t, h) for i, (lvl, t, h) in enumerate(entries)]


def cmd_toc():
    text = read_source()
    lines = []
    for level, title, hid in toc_entries(text):
        indent = "  " if level == 2 else ""
        lines.append(f"{indent}- [{title}](#{hid})")
    block = TOC_START + "\n\n" + "\n".join(lines) + "\n\n" + TOC_END
    new = re.sub(
        re.escape(TOC_START) + r".*?" + re.escape(TOC_END), block, text, flags=re.DOTALL
    )
    SOURCE.write_text(new, encoding="utf-8")
    print(f"TOC: {len(lines)} entries")


def chapter_sections(text):
    """Split the Markdown into {chapter_number: chapter_text}."""
    parts, current, buf = {}, None, []
    for _, line, in_code in iter_lines_outside_code(text):
        m = None if in_code else re.match(r"^# Chapter (\d+):", line)
        if not in_code and line.startswith("# ") and not m:
            if current is not None:
                parts[current] = "\n".join(buf)
            current, buf = None, []
            continue
        if m:
            if current is not None:
                parts[current] = "\n".join(buf)
            current, buf = int(m.group(1)), []
        if current is not None:
            buf.append(line)
    if current is not None:
        parts[current] = "\n".join(buf)
    return parts


def fenced_blocks(chapter_text):
    """Return a list of (language, content, preceding_paragraph)."""
    blocks, lines = [], chapter_text.split("\n")
    i = 0
    while i < len(lines):
        m = FENCE.match(lines[i])
        if m and m.group(1):
            lang, j = m.group(1), i + 1
            while not FENCE.match(lines[j]):
                j += 1
            k = i - 1
            while k >= 0 and not lines[k].strip():
                k -= 1
            blocks.append((lang, "\n".join(lines[i + 1 : j]), lines[k], (i, j)))
            i = j + 1
        else:
            i += 1
    return blocks


def cmd_code():
    CODE.mkdir(exist_ok=True)
    for number, chapter in chapter_sections(read_source()).items():
        code = [b[1] for b in fenced_blocks(chapter) if b[0] == "python"]
        if not code:
            continue
        name = CODE_NAMES[number]
        header = (
            f'"""Chapter {number} code, extracted from '
            f"Combined_LLM_Evaluation_Report.md.\n\nEdit the report, "
            f'then run: python tools/build_report.py code\n"""\n\n'
        )
        (CODE / f"{name}.py").write_text(
            header + "\n\n\n".join(code) + "\n", encoding="utf-8"
        )
        print(f"{name}.py: {len(code)} block(s)")


def output_blocks():
    """Yield (chapter, block_text, expected_output_file, line_span)."""
    for number, chapter in chapter_sections(read_source()).items():
        for lang, content, before, span in fenced_blocks(chapter):
            if lang == "text" and "Executed output" in before:
                m = re.search(r"`code/(ch\d\d_\w+)\.py`", before)
                yield number, content, OUTPUTS / f"{m.group(1)}.txt", span


def _norm(text):
    return "\n".join(line.rstrip() for line in text.strip("\n").split("\n"))


def cmd_check():
    problems = 0
    for number, content, out_file, _ in output_blocks():
        actual = _norm(out_file.read_text(encoding="utf-8"))
        if _norm(content) != actual:
            problems += 1
            print(f"Chapter {number}: output block differs from {out_file.name}")
            for line in difflib.unified_diff(
                _norm(content).split("\n"), actual.split("\n"), lineterm=""
            ):
                print("   ", line)
        else:
            print(f"Chapter {number}: output matches {out_file.name}")
    if problems:
        sys.exit(1)


def cmd_sync():
    text = read_source()
    for number, content, out_file, _ in output_blocks():
        actual = _norm(out_file.read_text(encoding="utf-8"))
        if _norm(content) != actual:
            old = "```text\n" + content + "\n```"
            assert text.count(old) == 1, f"block not unique in chapter {number}"
            text = text.replace(old, "```text\n" + actual + "\n```")
            print(f"Chapter {number}: replaced output block")
    SOURCE.write_text(text, encoding="utf-8")


def cmd_fmt():
    """Format every ```python block in the report with `ruff format`."""
    text = read_source()
    count = 0

    def repl(match):
        nonlocal count
        result = subprocess.run(
            ["ruff", "format", "-"],
            input=match.group(1),
            text=True,
            capture_output=True,
            check=True,
        )
        count += result.stdout != match.group(1)
        return "```python\n" + result.stdout + "```"

    text = re.sub(r"```python\n(.*?)```", repl, text, flags=re.DOTALL)
    SOURCE.write_text(text, encoding="utf-8")
    print(f"Formatted python blocks; {count} changed")


def _cell_text(cell):
    cell = re.sub(r"\$[^$]*\$", "xxxxxxxx", cell)  # formulas: rough width
    cell = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell)
    return re.sub(r"[*`]", "", cell).strip()


def cmd_widths():
    """Set pandoc column widths (dash counts) from the cell contents."""
    lines = read_source().split("\n")
    in_code, i, changed = False, 0, 0
    while i < len(lines):
        if FENCE.match(lines[i]):
            in_code = not in_code
        sep = re.fullmatch(r"\|(\s*:?-+:?\s*\|)+", lines[i].strip())
        if not in_code and sep and i > 0 and lines[i - 1].startswith("|"):
            rows, j = [lines[i - 1]], i + 1
            while j < len(lines) and lines[j].startswith("|"):
                rows.append(lines[j])
                j += 1
            cells = [
                [_cell_text(c) for c in r.strip().strip("|").split(" | ")] for r in rows
            ]
            ncol = len(cells[0])
            # Absolute minimum (mm) = longest unbreakable word, bold-safe,
            # plus cell padding; remaining width is shared by content size.
            text_mm, char_mm, pad_mm = 176.0, 1.8, 5.0
            mins, weights = [], []
            for c in range(ncol):
                col = [r[c] for r in cells if c < len(r)]
                words = [w for cell in col for w in cell.split()] or ["x"]
                mins.append(min(40.0, max(len(w) for w in words) * char_mm + pad_mm))
                lens = [len(cell) for cell in col]
                weights.append(0.45 * max(lens) + 0.55 * sum(lens) / len(lens))
            spare = max(0.0, text_mm - sum(mins))
            total_w = sum(weights) or 1.0
            widths = [m + spare * w / total_w for m, w in zip(mins, weights)]
            dashes = ["-" * max(3, round(w)) for w in widths]  # 1 dash ~ 1 mm
            new = "|" + "|".join(dashes) + "|"
            if lines[i] != new:
                lines[i], changed = new, changed + 1
            i = j
            continue
        i += 1
    SOURCE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Column widths updated in {changed} tables")


def cmd_links():
    text = read_source()
    ids = {h[2] for h in headings(text)}
    bad = 0
    for _, line, in_code in iter_lines_outside_code(text):
        if in_code:
            continue
        for target in re.findall(r"\]\(#([^)]+)\)", line):
            if target not in ids:
                bad += 1
                print("Broken internal link:", target)
    print(f"Internal links checked; {bad} broken")
    if bad:
        sys.exit(1)


# --------------------------------------------------------------------------
# Pandoc conversion
# --------------------------------------------------------------------------
def pandoc(args, input_text):
    import pypandoc  # provided by the pypandoc_binary package

    exe = pypandoc.get_pandoc_path()
    result = subprocess.run(
        [exe, *args], input=input_text, text=True, capture_output=True, check=False
    )
    if result.returncode != 0 or result.stderr.strip():
        print(result.stderr)
    if result.returncode != 0:
        sys.exit(result.returncode)
    return result.stdout


READER = "markdown+gfm_auto_identifiers-implicit_figures"


def split_title(text):
    """Return (title, subtitle, rest) from the first lines of the Markdown."""
    lines = text.split("\n")
    assert lines[0].startswith("# ")
    title = lines[0][2:].strip()
    subtitle = lines[2].strip().strip("*")
    return title, subtitle, "\n".join(lines[3:])


def html_toc(text, pages=None):
    items = []
    for level, title, hid in toc_entries(text):
        label = re.sub(r"`([^`]*)`", r"<code>\1</code>", html.escape(title))
        page = str(pages.get(hid, "?")) if pages else "000"
        items.append(
            f'<li class="toc-l{level}"><a href="#{hid}">'
            f'<span class="toc-text">{label}</span><span class="toc-dots">'
            f'</span><span class="toc-page">{page}</span></a></li>'
        )
    return (
        '<nav class="toc" aria-label="Table of contents"><ul>\n'
        + "\n".join(items)
        + "\n</ul></nav>"
    )


def cmd_html(pages=None):
    WORK.mkdir(exist_ok=True)
    text = read_source()
    title, subtitle, body = split_title(text)
    toc_html = html_toc(text, pages)
    # Chrome's MathML puts no space after operator names such as "log".
    body = re.sub(r"\\(log|ln) (?=[a-zA-Z\\])", r"\\\1\\, ", body)
    body = re.sub(
        re.escape(TOC_START) + r".*?" + re.escape(TOC_END),
        lambda _: "```{=html}\n" + toc_html + "\n```",
        body,
        flags=re.DOTALL,
    )
    front = (
        '```{=html}\n<header class="titlepage"><h1 class="title">'
        f'{html.escape(title)}</h1><p class="subtitle">'
        f"{html.escape(subtitle)}</p></header>\n```\n"
    )
    out = pandoc(
        [
            "-f",
            READER,
            "-t",
            "html5",
            "--standalone",
            "--mathml",
            "--syntax-highlighting=tango",
            "--metadata",
            f"title={title}",
            "--metadata",
            "lang=en",
            "--template",
            str(TOOLS / "template.html"),
            "--css",
            "report.css",
        ],
        front + body,
    )
    out = keep_with_next(out)
    (WORK / "report.html").write_text(out, encoding="utf-8")
    (WORK / "report.css").write_text(
        (TOOLS / "report.css").read_text(encoding="utf-8"), encoding="utf-8"
    )
    print("HTML written:", WORK / "report.html")


def keep_with_next(page_html):
    """Wrap headings and label paragraphs with the block that follows them,
    so a page break cannot separate them (see .keep in report.css)."""
    from bs4 import BeautifulSoup  # pip install beautifulsoup4

    soup = BeautifulSoup(page_html, "html.parser")
    blocks = {"p", "table", "div", "ul", "ol", "pre", "blockquote"}

    def is_label(tag):
        if tag.name != "p":
            return False
        text = tag.get_text(" ", strip=True)
        strong = tag.find("strong")
        starts = strong is not None and text.startswith(strong.get_text())
        return starts and (
            text.endswith(":") or text in {"Answers", "Practice questions"}
        )

    for tag in list(soup.find_all(["h2", "h3", "p"])):
        if tag.name == "p" and not is_label(tag):
            continue
        if tag.get("id") == "table-of-contents" or tag.find_parent("nav"):
            continue
        nxt = tag.find_next_sibling()
        if nxt is None or nxt.name not in blocks:
            continue
        wrapper = soup.new_tag("div", attrs={"class": "keep"})
        tag.insert_before(wrapper)
        wrapper.append(tag.extract())
        wrapper.append(nxt.extract())
    return str(soup)


def print_pdf(target):
    subprocess.run(
        ["node", str(TOOLS / "print_pdf.cjs"), str(WORK / "report.html"), str(target)],
        check=True,
    )


def heading_pages(pdf_path, wanted_ids):
    """Map heading ids to 1-based page numbers using PDF named destinations."""
    import pymupdf as fitz

    doc = fitz.open(pdf_path)
    names = doc.resolve_names()
    pages = {}
    for hid in wanted_ids:
        if hid in names:
            pages[hid] = names[hid]["page"] + 1
    return pages, doc.page_count


def cmd_pdf():
    text = read_source()
    wanted = [hid for _, _, hid in toc_entries(text)]
    cmd_html(pages=None)
    first = WORK / "pass1.pdf"
    print_pdf(first)
    pages, count = heading_pages(first, wanted)
    missing = [w for w in wanted if w not in pages]
    if missing:
        print("No page found for:", missing)
        sys.exit(1)
    cmd_html(pages=pages)
    print_pdf(PDF_OUT)
    check_pages, count2 = heading_pages(PDF_OUT, wanted)
    if check_pages != pages or count2 != count:
        print("Page numbers changed between passes; run pdf again.")
        sys.exit(1)
    (WORK / "toc_pages.json").write_text(json.dumps(pages, indent=1))
    print(f"PDF written: {PDF_OUT} ({count2} pages)")


def cmd_docx():
    WORK.mkdir(exist_ok=True)
    text = read_source()
    title, subtitle, body = split_title(text)
    toc_field = (TOOLS / "toc_field.xml").read_text(encoding="utf-8")
    body = re.sub(
        re.escape(TOC_START) + r".*?" + re.escape(TOC_END),
        lambda _: "```{=openxml}\n" + toc_field + "\n```",
        body,
        flags=re.DOTALL,
    )
    body = body.replace(
        "## Table of Contents\n",
        '::: {custom-style="TOC Heading"}\nTable of Contents\n:::\n',
        1,
    )
    front = (
        f'::: {{custom-style="Title"}}\n{title}\n:::\n\n'
        f'::: {{custom-style="Subtitle"}}\n{subtitle}\n:::\n'
    )
    raw = WORK / "pandoc.docx"
    pandoc(
        [
            "-f",
            READER,
            "-t",
            "docx",
            "--reference-doc",
            str(TOOLS / "reference.docx"),
            "--syntax-highlighting=tango",
            "-o",
            str(raw),
        ],
        front + body,
    )
    subprocess.run(
        [
            sys.executable,
            str(TOOLS / "polish_docx.py"),
            str(raw),
            str(WORK / "polished.docx"),
        ],
        check=True,
    )
    subprocess.run(
        [
            "/usr/bin/python3",
            str(TOOLS / "update_docx.py"),
            str(WORK / "polished.docx"),
            str(DOCX_OUT),
            str(WORK / "docx_check.pdf"),
        ],
        check=True,
    )
    print("DOCX written:", DOCX_OUT)


COMMANDS = {
    "toc": cmd_toc,
    "fmt": cmd_fmt,
    "widths": cmd_widths,
    "code": cmd_code,
    "check": cmd_check,
    "sync": cmd_sync,
    "links": cmd_links,
    "html": cmd_html,
    "pdf": cmd_pdf,
    "docx": cmd_docx,
}

if __name__ == "__main__":
    for name in sys.argv[1:] or ["toc", "code", "links", "check", "pdf", "docx"]:
        COMMANDS[name]()
