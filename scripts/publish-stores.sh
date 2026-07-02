#!/usr/bin/env bash
# Publish the current NYTimesCleaner release artifacts to Chrome Web Store and AMO.
#
# Required Chrome Web Store env:
#   CWS_EXTENSION_ID
#   CWS_CLIENT_ID
#   CWS_CLIENT_SECRET
#   CWS_REFRESH_TOKEN
#
# Required Firefox AMO env:
#   AMO_JWT_ISSUER
#   AMO_JWT_SECRET
#   AMO_ADDON_ID       # AMO numeric id, slug, or manifest guid
#
# Optional env:
#   AMO_CHANNEL=listed
#   AMO_BASE_URL=https://addons.mozilla.org/api/v5
#   NYTNA_EXTENSION_ROOT=/path/to/repo

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
ROOT="${NYTNA_EXTENSION_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
PARENT="$(cd "$ROOT/.." && pwd)"

# shellcheck source=lib/load-release-env.sh
source "$SCRIPT_DIR/lib/load-release-env.sh"

BUILD=1
DRY_RUN=0
PUBLISH_CHROME=1
PUBLISH_FIREFOX=1
AMO_CHANNEL="${AMO_CHANNEL:-listed}"
AMO_BASE_URL="${AMO_BASE_URL:-https://addons.mozilla.org/api/v5}"

usage() {
  cat <<'EOF'
Usage: scripts/publish-stores.sh [options]

Options:
  --dry-run             Validate artifacts and required environment only.
  --no-build            Use existing ../NYTimesCleaner-<version>.zip/.xpi files.
  --chrome-only         Publish only to Chrome Web Store.
  --firefox-only        Publish only to Firefox AMO.
  --amo-channel VALUE   AMO channel: listed or unlisted. Default: listed.
  -h, --help            Show this help.

The script builds versioned artifacts with scripts/newCleaner.sh by default.
Chrome publishing submits the zip for review using the existing store listing.
Firefox publishing uploads the xpi, waits for validation, then creates a new
version for the existing AMO add-on.
EOF
}

log() {
  printf '%s\n' "$*"
}

die() {
  printf 'publish-stores: %s\n' "$*" >&2
  exit 1
}

need_command() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

require_env() {
  local missing=()
  local name
  for name in "$@"; do
    if [[ -z "${!name:-}" ]]; then
      missing+=("$name")
    fi
  done

  if ((${#missing[@]})); then
    die "missing required environment variables: ${missing[*]}"
  fi
}

url_path_encode() {
  python3 - "$1" <<'PY'
import sys
from urllib.parse import quote

print(quote(sys.argv[1], safe=""))
PY
}

amo_jwt() {
  require_env AMO_JWT_ISSUER AMO_JWT_SECRET
  python3 - <<'PY'
import base64
import hashlib
import hmac
import json
import os
import time
import uuid

def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

issued_at = int(time.time())
header = {"alg": "HS256", "typ": "JWT"}
payload = {
    "iss": os.environ["AMO_JWT_ISSUER"],
    "jti": str(uuid.uuid4()),
    "iat": issued_at,
    "exp": issued_at + 60,
}
unsigned = ".".join(
    b64url(json.dumps(part, separators=(",", ":")).encode("utf-8"))
    for part in (header, payload)
)
signature = hmac.new(
    os.environ["AMO_JWT_SECRET"].encode("utf-8"),
    unsigned.encode("ascii"),
    hashlib.sha256,
).digest()
print(f"{unsigned}.{b64url(signature)}")
PY
}

version_from_manifest() {
  python3 - "$ROOT/manifest.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as manifest:
    print(json.load(manifest)["version"])
PY
}

validate_artifacts() {
  [[ -f "$ZIP" ]] || die "missing Chrome zip: $ZIP"
  [[ -f "$XPI" ]] || die "missing Firefox xpi: $XPI"
  python3 - "$ZIP" "$XPI" <<'PY'
import sys
import zipfile

for path in sys.argv[1:]:
    with zipfile.ZipFile(path) as archive:
        if "manifest.json" not in archive.namelist():
            raise SystemExit(f"manifest.json is not at archive root: {path}")
PY
}

publish_chrome() {
  require_env CWS_EXTENSION_ID CWS_CLIENT_ID CWS_CLIENT_SECRET CWS_REFRESH_TOKEN

  log "Chrome: refreshing access token"
  local token_json
  token_json="$(
    curl -fsS "https://oauth2.googleapis.com/token" \
      -d "client_secret=$CWS_CLIENT_SECRET" \
      -d "grant_type=refresh_token" \
      -d "refresh_token=$CWS_REFRESH_TOKEN" \
      -d "client_id=$CWS_CLIENT_ID"
  )"
  local token
  token="$(jq -er '.access_token' <<<"$token_json")"

  local upload_url="https://www.googleapis.com/upload/chromewebstore/v1.1/items/$CWS_EXTENSION_ID"
  local publish_url="https://www.googleapis.com/chromewebstore/v1.1/items/$CWS_EXTENSION_ID/publish"

  log "Chrome: uploading $ZIP"
  local upload_json
  upload_json="$(
    curl -fsS -X PUT \
      -H "Authorization: Bearer $token" \
      -H "x-goog-api-version: 2" \
      -T "$ZIP" \
      "$upload_url"
  )"
  jq -c '{uploadState, itemError}' <<<"$upload_json"

  log "Chrome: submitting for review"
  local publish_json
  publish_json="$(
    curl -fsS -X POST \
      -H "Authorization: Bearer $token" \
      -H "x-goog-api-version: 2" \
      "$publish_url"
  )"
  jq -c . <<<"$publish_json"
}

publish_firefox() {
  require_env AMO_JWT_ISSUER AMO_JWT_SECRET AMO_ADDON_ID

  local base="${AMO_BASE_URL%/}"
  local addon_id
  addon_id="$(url_path_encode "$AMO_ADDON_ID")"

  log "Firefox: uploading $XPI to AMO ($AMO_CHANNEL)"
  local upload_json
  upload_json="$(
    curl -fsS -X POST "$base/addons/upload/" \
      -H "Authorization: JWT $(amo_jwt)" \
      -F "upload=@$XPI" \
      -F "channel=$AMO_CHANNEL"
  )"
  local upload_uuid
  upload_uuid="$(jq -er '.uuid' <<<"$upload_json")"

  log "Firefox: waiting for AMO validation ($upload_uuid)"
  local detail_json processed valid
  for _ in {1..60}; do
    detail_json="$(
      curl -fsS "$base/addons/upload/$upload_uuid/" \
        -H "Authorization: JWT $(amo_jwt)"
    )"
    processed="$(jq -r '.processed' <<<"$detail_json")"
    valid="$(jq -r '.valid' <<<"$detail_json")"

    if [[ "$processed" == "true" ]]; then
      if [[ "$valid" == "true" ]]; then
        break
      fi
      jq -c '.validation' <<<"$detail_json" >&2
      die "AMO validation failed for upload $upload_uuid"
    fi

    sleep 10
  done

  [[ "${valid:-}" == "true" ]] || die "timed out waiting for AMO validation"

  log "Firefox: creating new AMO version"
  local version_json
  version_json="$(
    jq -nc --arg upload "$upload_uuid" '{upload: $upload}' |
      curl -fsS -X POST "$base/addons/addon/$addon_id/versions/" \
        -H "Authorization: JWT $(amo_jwt)" \
        -H "Content-Type: application/json" \
        --data-binary @-
  )"
  jq -c . <<<"$version_json"
}

while (($#)); do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      ;;
    --no-build)
      BUILD=0
      ;;
    --chrome-only)
      PUBLISH_FIREFOX=0
      ;;
    --firefox-only)
      PUBLISH_CHROME=0
      ;;
    --amo-channel)
      shift
      [[ $# -gt 0 ]] || die "--amo-channel requires a value"
      AMO_CHANNEL="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
  shift
done

[[ "$AMO_CHANNEL" == "listed" || "$AMO_CHANNEL" == "unlisted" ]] || die "AMO channel must be listed or unlisted"

need_command curl
need_command jq
need_command python3

if ((BUILD)); then
  "$SCRIPT_DIR/newCleaner.sh"
fi

VERSION="$(version_from_manifest)"
ZIP="$PARENT/NYTimesCleaner-$VERSION.zip"
XPI="$PARENT/NYTimesCleaner-$VERSION.xpi"

validate_artifacts
log "Artifacts ready:"
log "  Chrome:  $ZIP"
log "  Firefox: $XPI"

if ((DRY_RUN)); then
  ((PUBLISH_CHROME)) && require_env CWS_EXTENSION_ID CWS_CLIENT_ID CWS_CLIENT_SECRET CWS_REFRESH_TOKEN
  ((PUBLISH_FIREFOX)) && require_env AMO_JWT_ISSUER AMO_JWT_SECRET AMO_ADDON_ID
  log "Dry run passed."
  exit 0
fi

((PUBLISH_CHROME)) && publish_chrome
((PUBLISH_FIREFOX)) && publish_firefox

log "Publish requests completed."
