#!/usr/bin/env bash
# Sign and submit NewsMinus to Firefox AMO via web-ext.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=lib/load-release-env.sh
source "$SCRIPT_DIR/lib/load-release-env.sh"

for var in AMO_JWT_ISSUER AMO_JWT_SECRET; do
  if [[ -z "${!var:-}" ]]; then
    echo "error: $var is required (set in scripts/release.env or Nunus release.env)" >&2
    exit 1
  fi
done

if ! command -v web-ext >/dev/null 2>&1; then
  echo "error: web-ext CLI not found (npm install -g web-ext)" >&2
  exit 1
fi

channel="${AMO_CHANNEL:-listed}"
artifacts_dir="${NEWSMINUS_FIREFOX_ARTIFACTS:-$ROOT/../firefox-artifacts-newsminus}"
metadata="${NEWSMINUS_AMO_METADATA:-$ROOT/scripts/amo-metadata.json}"
mkdir -p "$artifacts_dir"

args=(
  sign
  --source-dir "$ROOT"
  --api-key "$AMO_JWT_ISSUER"
  --api-secret "$AMO_JWT_SECRET"
  --channel "$channel"
  --artifacts-dir "$artifacts_dir"
  --approval-timeout 0
)

if [[ -f "$metadata" ]]; then
  args+=(--amo-metadata "$metadata")
fi

web-ext "${args[@]}"

signed="$(find "$artifacts_dir" -name '*.xpi' | head -1)"
if [[ -z "$signed" ]]; then
  echo "Submitted to AMO ($channel); signed XPI appears after review." >&2
else
  echo "Signed/submitted: $signed"
fi
