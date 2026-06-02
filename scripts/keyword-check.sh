#!/usr/bin/env bash
# Check that the JD's keywords actually made it into the tailored resume,
# without re-reading the whole .tex. Pass the required/preferred skills and
# technologies from the job description; each is matched case-insensitively as
# a literal substring against the resume.
#
# Usage:
#   scripts/keyword-check.sh output/<role>.tex "Go" "Kubernetes" "GitHub Actions"
#   scripts/keyword-check.sh output/<role>.tex "Go,Kubernetes,PostgreSQL,GCP"
#
# Prints a present/missing report. Exits 0 if every keyword is present,
# 1 if any are missing, 2 on error.
set -euo pipefail

tex="${1:?usage: scripts/keyword-check.sh <path/to/resume.tex> <keyword> [keyword ...]}"
shift || true

if [[ ! -f "$tex" ]]; then
  echo "error: no such file: $tex" >&2
  exit 2
fi
if [[ "$#" -eq 0 ]]; then
  echo "error: no keywords given" >&2
  exit 2
fi

# Flatten args, splitting any comma-separated values into individual keywords.
keywords=()
for arg in "$@"; do
  IFS=',' read -ra parts <<< "$arg"
  for p in "${parts[@]}"; do
    p="${p#"${p%%[![:space:]]*}"}"   # ltrim
    p="${p%"${p##*[![:space:]]}"}"   # rtrim
    [[ -n "$p" ]] && keywords+=("$p")
  done
done

echo "Keyword coverage for $tex:"
missing=()
for kw in "${keywords[@]}"; do
  if grep -iqF -- "$kw" "$tex"; then
    echo "  ✓ $kw"
  else
    echo "  ✗ $kw"
    missing+=("$kw")
  fi
done

if [[ "${#missing[@]}" -eq 0 ]]; then
  echo "All ${#keywords[@]} keyword(s) present."
  exit 0
fi

# Join missing with ", "
joined="$(printf '%s, ' "${missing[@]}")"; joined="${joined%, }"
echo "${#missing[@]} of ${#keywords[@]} missing: ${joined}"
echo "(Add any that exist in master.tex; if a missing keyword is not in the master, do not invent it.)"
exit 1
