"""Fill in the Word table of contents (with page numbers) using LibreOffice.

Usage: /usr/bin/python3 tools/update_docx.py input.docx output.docx [check.pdf]
Needs: LibreOffice and its Python-UNO bridge (the system python3 with `uno`).
The optional third argument also exports a PDF of the DOCX for visual checks.
"""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.connection import NoConnectException
from com.sun.star.lang import DisposedException


def prop(name, value):
    item = PropertyValue()
    item.Name, item.Value = name, value
    return item


source = Path(sys.argv[1]).resolve()
target = Path(sys.argv[2]).resolve()
check_pdf = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else None

profile = tempfile.mkdtemp(prefix="lo-profile-")
port = 2002 + os.getpid() % 1000
office = subprocess.Popen(
    [
        "soffice",
        "--headless",
        "--invisible",
        "--nologo",
        "--norestore",
        f"-env:UserInstallation=file://{profile}",
        f"--accept=socket,host=127.0.0.1,port={port};urp;",
    ]
)
try:
    resolver = uno.getComponentContext().ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", uno.getComponentContext()
    )
    for _ in range(60):
        try:
            ctx = resolver.resolve(
                f"uno:socket,host=127.0.0.1,port={port};urp;StarOffice.ComponentContext"
            )
            break
        except NoConnectException:  # LibreOffice is still starting
            time.sleep(0.5)
    else:
        raise RuntimeError("LibreOffice did not start")
    desktop = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.frame.Desktop", ctx
    )
    doc = desktop.loadComponentFromURL(
        source.as_uri(), "_blank", 0, (prop("Hidden", True),)
    )
    indexes = doc.getDocumentIndexes()
    count = indexes.getCount()
    for i in range(count):
        indexes.getByIndex(i).update()
    doc.refresh()
    doc.storeToURL(target.as_uri(), (prop("FilterName", "MS Word 2007 XML"),))
    if check_pdf:
        doc.storeToURL(check_pdf.as_uri(), (prop("FilterName", "writer_pdf_Export"),))
    doc.close(True)
    print(f"Updated {count} index(es); wrote {target}")
finally:
    try:
        desktop.terminate()
    except (NameError, DisposedException):  # never started, or already closed
        office.terminate()
    office.wait(timeout=60)
