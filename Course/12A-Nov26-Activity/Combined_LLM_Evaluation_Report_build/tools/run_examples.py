"""Run every chapter example and save its output to ../outputs/.

Usage (from the build folder):  python tools/run_examples.py
The environment summary is written to outputs/environment.txt.
"""

import platform
import subprocess
import sys
from importlib import metadata
from pathlib import Path

BUILD = Path(__file__).resolve().parent.parent
CODE, OUT = BUILD / "code", BUILD / "outputs"
OUT.mkdir(exist_ok=True)

packages = [
    "scikit-learn",
    "sacrebleu",
    "nltk",
    "rouge-score",
    "jiwer",
    "bert-score",
    "torch",
    "transformers",
    "regex",
]
lines = [f"Python {platform.python_version()} on {platform.platform()}"]
for name in packages:
    try:
        lines.append(f"{name}=={metadata.version(name)}")
    except metadata.PackageNotFoundError:
        lines.append(f"{name}: not installed")
(OUT / "environment.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))

failed = []
for script in sorted(CODE.glob("ch*.py")):
    result = subprocess.run(
        [sys.executable, script.name],
        cwd=CODE,
        capture_output=True,
        text=True,
        check=False,
    )
    (OUT / f"{script.stem}.txt").write_text(result.stdout, encoding="utf-8")
    status = "OK" if result.returncode == 0 else f"FAILED ({result.returncode})"
    print(f"{script.name}: {status}")
    if result.returncode != 0:
        failed.append(script.name)
        print(result.stderr[-2000:])
sys.exit(1 if failed else 0)
