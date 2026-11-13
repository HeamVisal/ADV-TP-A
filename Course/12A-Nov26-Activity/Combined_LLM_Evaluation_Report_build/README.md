# Build files for the combined LLM evaluation report

This folder holds everything needed to reproduce
`../Combined_LLM_Evaluation_Report.pdf` and `../Combined_LLM_Evaluation_Report.docx`
from the editable source `../Combined_LLM_Evaluation_Report.md`.

| Path | Purpose |
|---|---|
| `code/ch01_*.py` … `code/ch10_*.py` | Chapter code, extracted from the report’s ```` ```python ```` blocks |
| `outputs/*.txt` | Real outputs of those scripts; `outputs/environment.txt` records versions |
| `tools/build_report.py` | Main build script (TOC, code extraction, output checks, HTML/PDF/DOCX) |
| `tools/run_examples.py` | Runs every chapter script and saves its output |
| `tools/template.html`, `tools/report.css` | HTML template and print stylesheet for the PDF |
| `tools/print_pdf.cjs` | Prints the HTML to PDF with Chrome (bookmarks, page numbers, tagged text) |
| `tools/make_reference_docx.py`, `tools/reference.docx` | Word style template |
| `tools/toc_field.xml` | Word TOC field inserted in place of the Markdown TOC |
| `tools/polish_docx.py` | Table borders, repeated header rows, header/footer page numbers |
| `tools/update_docx.py` | Fills in the Word TOC page numbers with LibreOffice |
| `requirements.txt` | Python packages used for the build and the examples |
| `build/` | Generated intermediates (HTML, first-pass PDF, DOCX check PDF); safe to delete |

## Requirements

- Python 3.11+ with the packages in `requirements.txt`, ideally in a separate virtual
  environment so the course environments are not changed:
  `python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt`
  (for a CPU-only PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cpu` first).
- NLTK WordNet data: `python -m nltk.downloader wordnet`.
- Google Chrome (path in `CHROME_PATH`, default `/usr/bin/google-chrome`) and Node.js
  with `puppeteer-core@24` (`npm install puppeteer-core@24` in any folder, then set
  `NODE_PATH` to its `node_modules`).
- LibreOffice with its Python-UNO bridge (the system `/usr/bin/python3` must be able to
  `import uno`), used only to fill the Word table of contents.
- Fonts used by the PDF: Noto Serif, Noto Sans, Noto Sans Mono, Noto Sans Khmer, Latin Modern Math.

## Rebuild

Run from this folder after editing the Markdown:

```bash
python tools/build_report.py toc fmt widths code links   # update TOC, format code, size tables
python tools/run_examples.py                             # execute all chapter code
python tools/build_report.py check                       # report output blocks must match
python tools/build_report.py pdf docx                    # two-pass PDF, then DOCX
```

If `check` reports a difference after a library upgrade, review it, then run
`python tools/build_report.py sync` to copy the new outputs into the report.

The PDF is printed twice: the first pass finds the page of every heading (from the
PDF’s named destinations) and the second pass writes those numbers into the table
of contents. The build stops if page numbers change between passes.

## Notes

- The Word table of contents is a real TOC field. Its page numbers come from
  LibreOffice’s layout; if Word paginates differently, right-click the table of
  contents and choose **Update Field → Update entire table**.
- `bert-score` downloads `bert-base-uncased` (about 440 MB) and the Khmer tokenizer
  check downloads two more tokenizers on first run.
