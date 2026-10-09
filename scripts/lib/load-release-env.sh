#!/usr/bin/env bash
# Source release credentials for NewsMinus publish scripts.
#
# Order:
#   1. ../nunus/NunusCursor/scripts/release.env (shared OAuth / AMO / Apple keys)
#   2. scripts/release.env (repo-local overrides win)
#
# Maps shared Nunus Chrome OAuth vars to NewsMinus CWS_* names, sets NewsMinus
# store IDs, and pins the NewsMinus Apple bundle IDs / profile names (the shared
# Nunus env may define its own — app-specific values must never leak across).

set -euo pipefail

RELEASE_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
ROOT="$(cd "$RELEASE_LIB_DIR/../.." && pwd)"
export ROOT

LOCAL_ENV="${NEWSMINUS_RELEASE_ENV:-$ROOT/scripts/release.env}"
NUNUS_ENV="${NUNUS_RELEASE_ENV:-}"

if [[ -z "$NUNUS_ENV" ]]; then
  candidate="$ROOT/../nunus/NunusCursor/scripts/release.env"
  if [[ -f "$candidate" ]]; then
    NUNUS_ENV="$candidate"
  fi
fi

if [[ -f "$NUNUS_ENV" ]]; then
  # shellcheck disable=SC1090
  set -a
  source "$NUNUS_ENV"
  set +a
fi
if [[ -f "$LOCAL_ENV" ]]; then
  # shellcheck disable=SC1090
  set -a
  source "$LOCAL_ENV"
  set +a
fi

# —— Chrome Web Store ——
export CWS_EXTENSION_ID="${CWS_EXTENSION_ID:-${NEWSMINUS_CHROME_EXTENSION_ID:-hkiiglaagokcdpagbblfhmdobblfelpn}}"
export CWS_CLIENT_ID="${CWS_CLIENT_ID:-${CHROME_CLIENT_ID:-}}"
export CWS_CLIENT_SECRET="${CWS_CLIENT_SECRET:-${CHROME_CLIENT_SECRET:-}}"
export CWS_REFRESH_TOKEN="${CWS_REFRESH_TOKEN:-${CHROME_REFRESH_TOKEN:-}}"

# —— Firefox AMO ——
export AMO_JWT_ISSUER="${AMO_JWT_ISSUER:-}"
export AMO_JWT_SECRET="${AMO_JWT_SECRET:-}"
export AMO_ADDON_ID="${AMO_ADDON_ID:-${NEWSMINUS_AMO_ADDON_ID:-nytimescleaner@nunus.extension}}"
export AMO_CHANNEL="${AMO_CHANNEL:-listed}"

# —— Apple (Safari, macOS + iOS) ——
# Team + App Store Connect API key are shared with Nunus (same Apple account).
export APPLE_TEAM_ID="${APPLE_TEAM_ID:-}"
export APP_STORE_CONNECT_API_KEY_ID="${APP_STORE_CONNECT_API_KEY_ID:-}"
export APP_STORE_CONNECT_ISSUER_ID="${APP_STORE_CONNECT_ISSUER_ID:-}"
export APP_STORE_CONNECT_API_KEY_PATH="${APP_STORE_CONNECT_API_KEY_PATH:-}"

# Bundle IDs and profile names are NewsMinus-specific. Values inherited from
# the shared Nunus release.env are intentionally overridden here; use
# NEWSMINUS_* vars for local customization.
export MACOS_BUNDLE_ID="${NEWSMINUS_MACOS_BUNDLE_ID:-com.nunus.NYTimesCleanerHost}"
export IOS_BUNDLE_ID="${NEWSMINUS_IOS_BUNDLE_ID:-com.nunus.NYTimesCleanerHost.ios}"
export IOS_EXT_BUNDLE_ID="${NEWSMINUS_IOS_EXT_BUNDLE_ID:-${IOS_BUNDLE_ID}.extension}"
export IOS_HOST_PROFILE="${NEWSMINUS_IOS_HOST_PROFILE:-NewsMinus iOS App Store}"
export IOS_EXT_PROFILE="${NEWSMINUS_IOS_EXT_PROFILE:-NewsMinus iOS Extension App Store}"

export RELEASE_GIT_REMOTE="${RELEASE_GIT_REMOTE:-origin}"
export RELEASE_GIT_BRANCH="${RELEASE_GIT_BRANCH:-master}"
