#!/usr/bin/env bash
# Lint an exported tailored resume for master-only leftovers, so the
# "clean, compilable .tex" rule (directives.md §1.1-1.2) can be checked
# without an LLM re-reading the file.
# Usage: scripts/lint-output.sh output/<role>.tex
# Prints any problems found. Exits 0 if clean, 1 if leftovers found, 2 on error.
set -euo pipefail

tex="${1:?usage: scripts/lint-output.sh <path/to/resume.tex>}"

if [[ ! -f "$tex" ]]; then
  echo "error: no such file: $tex" >&2
  exit 2
fi

found=0

report() { # <label> <grep-output>
  local label="$1" hits="$2"
  if [[ -n "$hits" ]]; then
    echo "✗ $label:"
    echo "$hits" | sed 's/^/    /'
    found=1
  fi
}

# 1. Master-only guidance comments (%% VARIANT, %% EXTRA, %% Repo, %% Stack, ...).
report "leftover %% guidance comments" \
  "$(grep -nE '%%' "$tex" || true)"

# 2. Commented-out bullets = alternate variants that should have been deleted.
report "commented-out \\resumeItem bullets (un-deleted variants)" \
  "$(grep -nE '^[[:space:]]*%[[:space:]]*\\resumeItem' "$tex" || true)"

# 3. Stray variant/extra markers anywhere in the file.
report "stray VARIANT/EXTRA markers" \
  "$(grep -nE 'VARIANT|EXTRA bullets' "$tex" || true)"

if [[ "$found" -eq 0 ]]; then
  echo "✓ clean: no master-only leftovers in $tex"
fi
exit "$found"
