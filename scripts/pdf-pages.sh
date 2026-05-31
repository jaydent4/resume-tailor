#!/usr/bin/env bash
# Report the page count of a PDF so the resume can be checked for the
# "exactly 1 page" rule without an LLM reading the file.
# Usage: scripts/pdf-pages.sh output/<role>.pdf
# Prints the page count to stdout. Exits 0 if the PDF has exactly 1 page,
# 1 if it has a different number of pages, 2 on error.
set -euo pipefail

pdf="${1:?usage: scripts/pdf-pages.sh <path/to/resume.pdf>}"

if [[ ! -f "$pdf" ]]; then
  echo "error: no such file: $pdf" >&2
  exit 2
fi

# Count pages with ghostscript (no rendering, just the page tree).
pages="$(gs -q -dNODISPLAY -dNOSAFER \
  -c "($pdf) (r) file runpdfbegin pdfpagecount = quit" 2>/dev/null || true)"

if ! [[ "$pages" =~ ^[0-9]+$ ]]; then
  echo "error: could not read page count from $pdf" >&2
  exit 2
fi

echo "$pages"
[[ "$pages" -eq 1 ]]
