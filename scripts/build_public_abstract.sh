#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"

if [[ ! -x "$CHROME" ]]; then
  printf 'Chrome not found: %s\n' "$CHROME" >&2
  exit 1
fi

build_one() {
  local source="$1"
  local pdf="$2"
  local preview="$3"
  local profile
  profile="$(mktemp -d "${TMPDIR:-/tmp}/closure-abstract-chrome.XXXXXX")"
  trap 'rm -rf "$profile"' RETURN

  rm -f "$pdf"
  python3 - "$CHROME" "$profile" "$source" "$pdf" <<'PY'
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

chrome, profile, source, output = sys.argv[1:]
command = [
    chrome,
    "--headless=new",
    "--disable-gpu",
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-extensions",
    "--no-first-run",
    "--allow-file-access-from-files",
    "--run-all-compositor-stages-before-draw",
    "--no-pdf-header-footer",
    f"--user-data-dir={profile}",
    f"--print-to-pdf={output}",
    Path(source).resolve().as_uri(),
]
process = subprocess.Popen(
    command,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    start_new_session=True,
)
deadline = time.monotonic() + 30
last_size = -1
stable_since = None
try:
    while time.monotonic() < deadline:
        if process.poll() is not None:
            break
        path = Path(output)
        size = path.stat().st_size if path.exists() else 0
        if size > 10_000 and size == last_size:
            stable_since = stable_since or time.monotonic()
            if time.monotonic() - stable_since >= 1.5:
                break
        else:
            stable_since = None
            last_size = size
        time.sleep(0.25)
finally:
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()

if not Path(output).exists() or Path(output).stat().st_size <= 10_000:
    raise SystemExit(f"Chrome did not produce {output}")
PY

  local pages
  pages="$(pdfinfo "$pdf" | awk '/^Pages:/ { print $2 }')"
  [[ "$pages" == "2" ]] || {
    printf '%s produced %s pages, expected 2\n' "$source" "$pages" >&2
    exit 1
  }
  pdfinfo "$pdf" | grep -Eq '^Page size:[[:space:]]+59[45]\..* x 84[12]\..* pts \(A4\)$' || {
    printf '%s is not A4\n' "$pdf" >&2
    exit 1
  }

  pdftoppm -f 1 -l 1 -singlefile -png -r 150 "$pdf" "${preview%.png}" >/dev/null 2>&1
  rm -rf "$profile"
  trap - RETURN
}

xmllint --noout "$ROOT/distinction-reentry.svg"
xmllint --noout "$ROOT/ru/distinction-reentry.svg"

build_one "$ROOT/index.html" "$ROOT/ABSTRACT.pdf" "$ROOT/preview-page-1.png"
build_one "$ROOT/ru/index.html" "$ROOT/ru/ABSTRACT.pdf" "$ROOT/ru/preview-page-1.png"

printf 'PASS public abstracts: English=2 pages A4 Russian=2 pages A4\n'
