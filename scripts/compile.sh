#!/usr/bin/env bash
# Compile a tailored resume .tex to PDF.
# Usage: scripts/compile.sh output/<role>.tex
set -euo pipefail

src="${1:?usage: scripts/compile.sh <path/to/resume.tex>}"
outdir="$(dirname "$src")"

base="$outdir/$(basename "${src%.tex}")"

# pdflatex's console output is ~100 lines of noise per run; keep it out of the
# transcript and print only the error context when the build fails.
if ! pdflatex -interaction=nonstopmode -halt-on-error -output-directory "$outdir" "$src" >/dev/null 2>&1; then
  echo "BUILD FAILED: $src"
  grep -A4 -E '^!|Error' "$base.log" 2>/dev/null | head -30 || true
  rm -f "$base".{aux,out}
  exit 1
fi

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
