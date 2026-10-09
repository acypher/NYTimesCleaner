#!/usr/bin/env bash
# Build ../NewsMinus.xpi from this repo (Firefox / AMO).
# Sanity-check: manifest.json at zip root.
#
# Optional env:
#   NYTNA_EXTENSION_ROOT  — repo root (default: parent of this script's directory)
#   NYTNA_XPI            — output .xpi path (default: $ROOT/../NewsMinus.xpi)
#
# Versioned zip + .xpi together: scripts/newCleaner.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
ROOT="${NYTNA_EXTENSION_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
OUT="${NYTNA_XPI:-$ROOT/../NewsMinus.xpi}"
STAGE="$(mktemp -d "${TMPDIR:-/tmp}/newsminus-firefox-stage.XXXXXX")"

cleanup() {
  rm -rf "$STAGE"
}
trap cleanup EXIT

cd "$ROOT" || {
  echo "buildNewsMinusFirefox: cannot cd to $ROOT" >&2
  exit 1
}

"$SCRIPT_DIR/stage-firefox-source.sh" "$STAGE" "$ROOT"

rm -f "$OUT"

(
  cd "$STAGE" || exit 1
  zip -r "$OUT" .
)

manifest_at_root() {
  local z="$1"
  if command -v zipinfo >/dev/null 2>&1; then
    grep -Fqx 'manifest.json' < <(zipinfo -1 "$z")
  else
    grep -qE '[[:space:]]manifest\.json$' < <(unzip -l "$z")
  fi
}

if ! manifest_at_root "$OUT"; then
  echo "buildNewsMinusFirefox: sanity check failed (manifest.json not at zip root): $OUT" >&2
  exit 1
fi

echo 'zipped and checked'
