#!/usr/bin/env bash
# Report which NewsMinus release credentials are configured.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
# shellcheck source=lib/load-release-env.sh
source "$SCRIPT_DIR/lib/load-release-env.sh"

missing=()
warn=()
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

need_file() {
  local name="$1"
  local value="${!name-}"
  if [[ -z "$value" ]]; then
    missing+=("$name")
  elif [[ ! -f "$value" ]]; then
    warn+=("$name (set but file not found: $value)")
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

section "Apple App Store (Safari, macOS + iOS)"
need_var APPLE_TEAM_ID
if [[ -n "${APP_STORE_CONNECT_API_KEY_ID:-}" || -n "${APP_STORE_CONNECT_ISSUER_ID:-}" || -n "${APP_STORE_CONNECT_API_KEY_PATH:-}" ]]; then
  need_var APP_STORE_CONNECT_API_KEY_ID
  need_var APP_STORE_CONNECT_ISSUER_ID
  need_file APP_STORE_CONNECT_API_KEY_PATH
else
  need_var APPLE_ID
  need_var APPLE_APP_SPECIFIC_PASSWORD
fi
ok+=("MACOS_BUNDLE_ID (${MACOS_BUNDLE_ID:-com.nunus.NYTimesCleanerHost})")
ok+=("IOS_BUNDLE_ID (${IOS_BUNDLE_ID:-com.nunus.NYTimesCleanerHost.ios})")
if [[ "${PUBLISH_INCLUDE_IOS:-1}" == "0" ]]; then
  ok+=("iOS skipped (PUBLISH_INCLUDE_IOS=0)")
else
  ok+=("iOS included by default (skip with --no-ios)")
fi
if ! command -v xcodebuild >/dev/null 2>&1; then
  warn+=("xcodebuild (install Xcode)")
fi

section "Summary"
if ((${#ok[@]})); then
  echo "Configured:"
  for name in "${ok[@]}"; do
    echo "  ✓ $name"
  done
fi

if ((${#warn[@]})); then
  echo
  echo "Warnings:"
  for item in "${warn[@]}"; do
    echo "  ! $item"
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
