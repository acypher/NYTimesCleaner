#!/usr/bin/env bash
# Build ../NewsMinus.xpi from this repo (Firefox / AMO).
# Sanity-check: manifest.json at zip root.
#
# Optional env:
#   NYTNA_EXTENSION_ROOT  — repo root (default: parent of this script’s directory)
#   NYTNA_XPI            — output .xpi path (default: $ROOT/../NewsMinus.xpi)
#
# Versioned zip + .xpi together: scripts/newCleaner.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
ROOT="${NYTNA_EXTENSION_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
OUT="${NYTNA_XPI:-$ROOT/../NewsMinus.xpi}"

cd "$ROOT" || {
  echo "buildNytimesCleanerFirefox: cannot cd to $ROOT" >&2
  exit 1
}

rm -f "$OUT"

zip -r "$OUT" . \
  -x "*.git*" \
  -x ".DS_Store" \
  -x "*/.DS_Store" \
  -x "safari/*" \
  -x "images/*" \
  -x "samples/*" \
  -x ".idea/*" \
  -x ".cursor/*" \
  -x "scripts/*" \
  -x "*.iml"

manifest_at_root() {
  local z="$1"
  if command -v zipinfo >/dev/null 2>&1; then
    grep -Fqx 'manifest.json' < <(zipinfo -1 "$z")
  else
    grep -qE '[[:space:]]manifest\.json$' < <(unzip -l "$z")
  fi
}

if ! manifest_at_root "$OUT"; then
  echo "buildNytimesCleanerFirefox: sanity check failed (manifest.json not at zip root): $OUT" >&2
  exit 1
fi

echo 'zipped and checked'
