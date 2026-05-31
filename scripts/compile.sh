#!/usr/bin/env bash
# Compile a tailored resume .tex to PDF.
# Usage: scripts/compile.sh output/<role>.tex
set -euo pipefail

src="${1:?usage: scripts/compile.sh <path/to/resume.tex>}"
outdir="$(dirname "$src")"

pdflatex -interaction=nonstopmode -halt-on-error -output-directory "$outdir" "$src"

base="$outdir/$(basename "${src%.tex}")"

# Surface overfull/underfull boxes: these are warnings (not errors), so text
# running past the margin still "compiles" and stays a 1-page PDF that looks
# broken. Capture them before the log is deleted.
boxwarns="$(grep -nE 'Overfull|Underfull' "$base.log" || true)"

# clean aux artifacts
rm -f "$base".{aux,log,out}

echo "Built: ${base}.pdf"
if [[ -n "$boxwarns" ]]; then
  echo "Layout warnings (text may run past the margin):"
  echo "$boxwarns" | sed 's/^/    /'
fi

# Report page count so the 1-page rule can be checked without reading the PDF.
pages="$("$(dirname "$0")/pdf-pages.sh" "${base}.pdf" 2>/dev/null || true)"
echo "Pages: ${pages:-unknown}"
