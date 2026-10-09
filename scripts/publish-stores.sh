#!/usr/bin/env bash
# Build and publish the current manifest.json version to Chrome, Firefox, and Safari.
# No version bump or git operations — use release.sh for a full release.
#
# Before publish (run manually or rely on checks below):
#   ./scripts/check-release-credentials.sh
#   ./scripts/check-store-pending.sh   # must exit 0 (READY)
#
# Usage:
#   ./scripts/publish-stores.sh                # Chrome + Firefox + Safari macOS + Safari iOS
#   ./scripts/publish-stores.sh --build-only
#   ./scripts/publish-stores.sh --dry-run
#   ./scripts/publish-stores.sh --chrome-only
#   ./scripts/publish-stores.sh --firefox-only
#   ./scripts/publish-stores.sh --safari-only
#   ./scripts/publish-stores.sh --no-safari
#   ./scripts/publish-stores.sh --no-ios
#   ./scripts/publish-stores.sh --no-build     # use existing ../NewsMinus-<version>.zip/.xpi
#
# iOS Safari (separate App Store app com.nunus.NYTimesCleanerHost.ios) is included by default.
# Skip it with --no-ios or PUBLISH_INCLUDE_IOS=0.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
ROOT="${NYTNA_EXTENSION_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
# shellcheck source=lib/load-release-env.sh
source "$SCRIPT_DIR/lib/load-release-env.sh"

BUILD=1
BUILD_ONLY=0
DRY_RUN=0
PUBLISH_CHROME=1
PUBLISH_FIREFOX=1
PUBLISH_SAFARI=1
INCLUDE_IOS="${PUBLISH_INCLUDE_IOS:-1}"

usage() {
  sed -n '2,16p' "$0" >&2
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --build-only) BUILD_ONLY=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --no-build) BUILD=0; shift ;;
    --chrome-only) PUBLISH_FIREFOX=0; PUBLISH_SAFARI=0; shift ;;
    --firefox-only) PUBLISH_CHROME=0; PUBLISH_SAFARI=0; shift ;;
    --safari-only) PUBLISH_CHROME=0; PUBLISH_FIREFOX=0; shift ;;
    --no-safari) PUBLISH_SAFARI=0; shift ;;
    --ios) INCLUDE_IOS=1; shift ;;
    --no-ios) INCLUDE_IOS=0; shift ;;
    -h|--help) usage ;;
    *) echo "error: unknown argument: $1" >&2; usage ;;
  esac
done

VERSION="$(python3 -c "import json; print(json.load(open('$ROOT/manifest.json'))['version'])")"
PARENT="$(cd "$ROOT/.." && pwd)"
ZIP="$PARENT/NewsMinus-${VERSION}.zip"
XPI="$PARENT/NewsMinus-${VERSION}.xpi"

echo "== Publish NewsMinus ${VERSION} =="

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry run — would:"
  if [[ "$BUILD" -eq 1 ]]; then
    echo "  1. Build $ZIP and $XPI (newCleaner.sh)"
  else
    echo "  1. Use existing $ZIP and $XPI"
  fi
  if [[ "$PUBLISH_SAFARI" -eq 1 ]]; then
    echo "  2. Build Safari macOS archive (build-safari-mac.sh)"
    if [[ "$INCLUDE_IOS" -eq 1 ]]; then
      echo "  2b. Build Safari iOS archive (build-safari-ios.sh)"
    fi
  fi
  if [[ "$BUILD_ONLY" -eq 0 ]]; then
    echo "  3. Upload to selected stores"
    "$SCRIPT_DIR/check-release-credentials.sh" || true
    "$SCRIPT_DIR/check-store-pending.sh" || true
  fi
  exit 0
fi

if [[ "$BUILD" -eq 1 ]]; then
  echo
  echo "== Build Chrome zip + Firefox xpi =="
  "$SCRIPT_DIR/newCleaner.sh"
else
  [[ -f "$ZIP" ]] || { echo "error: missing Chrome zip: $ZIP" >&2; exit 1; }
  [[ -f "$XPI" ]] || { echo "error: missing Firefox xpi: $XPI" >&2; exit 1; }
fi

PKG=""
IPA=""
if [[ "$PUBLISH_SAFARI" -eq 1 ]]; then
  echo
  echo "== Build Safari macOS archive =="
  PKG="$("$SCRIPT_DIR/build-safari-mac.sh" | tail -1)"

  if [[ "$INCLUDE_IOS" -eq 1 ]]; then
    echo
    echo "== Build Safari iOS archive =="
    if IPA="$("$SCRIPT_DIR/build-safari-ios.sh" | tail -1)"; then
      :
    else
      echo "WARNING: iOS Safari build failed; skipping iOS for this run." >&2
      echo "  Ensure the iOS platform is installed (Xcode > Settings > Components) and that" >&2
      echo "  an App Store Connect app exists for ${IOS_BUNDLE_ID:-com.nunus.NYTimesCleanerHost.ios}." >&2
      INCLUDE_IOS=0
      IPA=""
    fi
  fi
fi

if [[ "$BUILD_ONLY" -eq 1 ]]; then
  echo
  echo "Build complete (--build-only; no store upload)."
  echo "  Chrome: $ZIP"
  echo "  Firefox: $XPI"
  if [[ "$PUBLISH_SAFARI" -eq 1 ]]; then
    echo "  Safari (macOS): $PKG"
    if [[ "$INCLUDE_IOS" -eq 1 ]]; then
      echo "  Safari (iOS): $IPA"
    fi
  fi
  exit 0
fi

print_artifacts() {
  echo "  Chrome: $ZIP"
  echo "  Firefox: $XPI"
  if [[ "$PUBLISH_SAFARI" -eq 1 ]]; then
    echo "  Safari (macOS): $PKG"
    if [[ "$INCLUDE_IOS" -eq 1 ]]; then echo "  Safari (iOS): $IPA"; fi
  fi
}

echo
echo "== Check store credentials =="
if ! "$SCRIPT_DIR/check-release-credentials.sh"; then
  echo
  echo "Stopped before publishing. Artifacts are ready:"
  print_artifacts
  echo
  echo "Fill in scripts/release.env, then run:"
  echo "  ./scripts/publish-stores.sh"
  exit 1
fi

echo
echo "== Check for pending store submissions =="
if ! "$SCRIPT_DIR/check-store-pending.sh"; then
  echo
  echo "Stopped before publishing. Artifacts are ready:"
  print_artifacts
  exit 1
fi

if [[ "$PUBLISH_CHROME" -eq 1 ]]; then
  echo
  echo "== Publish Chrome =="
  python3 "$SCRIPT_DIR/publish-chrome.py" "$ZIP"
fi

if [[ "$PUBLISH_FIREFOX" -eq 1 ]]; then
  echo
  echo "== Publish Firefox =="
  "$SCRIPT_DIR/publish-firefox.sh"
fi

if [[ "$PUBLISH_SAFARI" -eq 1 ]]; then
  echo
  echo "== Publish Safari (Mac App Store) =="
  "$SCRIPT_DIR/publish-safari-mac.sh" "$PKG"

  if [[ "${APP_STORE_SKIP_SUBMIT:-}" == "1" ]]; then
    echo "Skipped App Store submit (APP_STORE_SKIP_SUBMIT=1)."
  else
    echo
    echo "== Submit Safari for App Review (macOS) =="
    "$SCRIPT_DIR/submit-safari-appstore.sh"
  fi

  if [[ "$INCLUDE_IOS" -eq 1 ]]; then
    echo
    echo "== Publish Safari (iOS App Store) =="
    "$SCRIPT_DIR/publish-safari-ios.sh" "$IPA"

    if [[ "${APP_STORE_SKIP_SUBMIT:-}" == "1" ]]; then
      echo "Skipped iOS App Store submit (APP_STORE_SKIP_SUBMIT=1)."
    else
      echo
      echo "== Submit Safari for App Review (iOS) =="
      "$SCRIPT_DIR/submit-safari-ios.sh"
    fi
  fi
fi

echo
echo "Publish ${VERSION} complete."
if [[ "$PUBLISH_CHROME" -eq 1 ]]; then echo "  Chrome: ${ZIP}"; fi
if [[ "$PUBLISH_FIREFOX" -eq 1 ]]; then echo "  Firefox: signed via web-ext"; fi
if [[ "$PUBLISH_SAFARI" -eq 1 ]]; then
  echo "  Safari (macOS): ${PKG} uploaded; App Review submission attempted via API"
  if [[ "$INCLUDE_IOS" -eq 1 ]]; then
    echo "  Safari (iOS): ${IPA} uploaded; App Review submission attempted via API"
  fi
fi
echo "Monitor review status in the store dashboards / App Store Connect."

if [[ "${PUBLISH_CHECK_SKIP_DAILY:-}" != "1" ]]; then
  echo
  echo "== Arm daily publish-check until live =="
  "$SCRIPT_DIR/setup-publish-check-daily.sh" --version "$VERSION"
fi
