#!/usr/bin/env bash
# Report which NewsMinus release credentials are configured.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
# shellcheck source=lib/load-release-env.sh
source "$SCRIPT_DIR/lib/load-release-env.sh"

missing=()
ok=()

need_var() {
  local name="$1"
  local value="${!name-}"
  if [[ -z "$value" ]]; then
    missing+=("$name")
  else
    ok+=("$name")
  fi
}

section() {
  echo
  echo "== $1 =="
}

section "Chrome Web Store"
need_var CWS_EXTENSION_ID
need_var CWS_CLIENT_ID
need_var CWS_CLIENT_SECRET
need_var CWS_REFRESH_TOKEN

section "Firefox AMO"
need_var AMO_JWT_ISSUER
need_var AMO_JWT_SECRET
need_var AMO_ADDON_ID
ok+=("AMO_CHANNEL (${AMO_CHANNEL:-listed})")
if ! command -v web-ext >/dev/null 2>&1; then
  echo
  echo "Warning: web-ext CLI not found (npm install -g web-ext) — needed for Firefox listed submissions"
fi

section "Summary"
if ((${#ok[@]})); then
  echo "Configured:"
  for name in "${ok[@]}"; do
    echo "  ✓ $name"
  done
fi

if ((${#missing[@]})); then
  echo
  echo "Missing (copy scripts/release.env.example → scripts/release.env, or configure Nunus release.env):"
  for name in "${missing[@]}"; do
    echo "  ✗ $name"
  done
  echo
  echo "Local env:  ${NEWSMINUS_RELEASE_ENV:-$ROOT/scripts/release.env}"
  echo "Shared env: ${NUNUS_RELEASE_ENV:-$ROOT/../nunus/NunusCursor/scripts/release.env}"
  exit 1
fi

echo
echo "All release credentials look configured."
