#!/usr/bin/env bash
# Diagnose a one-page overflow WITHOUT rendering the PDF to an image.
# When a resume compiles to more than one page, this prints the text that
# spilled onto page 2+ (as plain text via ghostscript) so the cause can be
# seen and trimmed cheaply, instead of reading an expensive rendered image.
# Usage: scripts/overflow.sh output/<role>.pdf
# Exits 0 if the PDF is exactly 1 page, 1 if it overflows, 2 on error.
set -euo pipefail

pdf="${1:?usage: scripts/overflow.sh <path/to/resume.pdf>}"

if [[ ! -f "$pdf" ]]; then
  echo "error: no such file: $pdf" >&2
  exit 2
fi

pages="$(gs -q -dNODISPLAY -dNOSAFER \
  -c "($pdf) (r) file runpdfbegin pdfpagecount = quit" 2>/dev/null || true)"

if ! [[ "$pages" =~ ^[0-9]+$ ]]; then
  echo "error: could not read page count from $pdf" >&2
  exit 2
fi

if [[ "$pages" -eq 1 ]]; then
  echo "1 page — fits."
  exit 0
fi

echo "OVERFLOW: $pages pages. Content that spilled past page 1 (trim this):"
echo "------------------------------------------------------------"
gs -q -dNOPAUSE -dBATCH -dFirstPage=2 -dLastPage="$pages" \
   -sDEVICE=txtwrite -o - "$pdf" 2>/dev/null \
  | sed 's/[[:space:]]\+$//' | grep -v '^[[:space:]]*$'
echo "------------------------------------------------------------"
exit 1
