#!/usr/bin/env bash
# Source release credentials for NewsMinus publish scripts.
#
# Order:
#   1. scripts/release.env (repo-local overrides)
#   2. ../nunus/NunusCursor/scripts/release.env (shared OAuth / AMO keys)
#
# Maps shared Nunus Chrome OAuth vars to NewsMinus CWS_* names and sets store IDs.

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

if [[ -f "$LOCAL_ENV" ]]; then
  # shellcheck disable=SC1090
  set -a
  source "$LOCAL_ENV"
  set +a
elif [[ -f "$NUNUS_ENV" ]]; then
  # shellcheck disable=SC1090
  set -a
  source "$NUNUS_ENV"
  set +a
fi

export CWS_EXTENSION_ID="${CWS_EXTENSION_ID:-${NEWSMINUS_CHROME_EXTENSION_ID:-hkiiglaagokcdpagbblfhmdobblfelpn}}"
export CWS_CLIENT_ID="${CWS_CLIENT_ID:-${CHROME_CLIENT_ID:-}}"
export CWS_CLIENT_SECRET="${CWS_CLIENT_SECRET:-${CHROME_CLIENT_SECRET:-}}"
export CWS_REFRESH_TOKEN="${CWS_REFRESH_TOKEN:-${CHROME_REFRESH_TOKEN:-}}"

export AMO_JWT_ISSUER="${AMO_JWT_ISSUER:-}"
export AMO_JWT_SECRET="${AMO_JWT_SECRET:-}"
export AMO_ADDON_ID="${AMO_ADDON_ID:-${NEWSMINUS_AMO_ADDON_ID:-nytimescleaner@nunus.extension}}"
export AMO_CHANNEL="${AMO_CHANNEL:-listed}"
