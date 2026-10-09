#!/bin/sh
# Copy shared web-extension assets from the repo root into the built .appex.
#
# Xcode: "Run Script" build phase on both Safari Web Extension targets, placed
# before "Copy Bundle Resources" (User Script Sandboxing must be off).
# Optional: export NYTNA_WEBROOT="/absolute/path/to/NewsMinus" if the
# .xcodeproj is not under safari/ (defaults to PROJECT_DIR/.. = repo root).
set -eu
WEBROOT="${NYTNA_WEBROOT:-${PROJECT_DIR}/..}"
WRAPPER="${BUILT_PRODUCTS_DIR}/${WRAPPER_NAME}"
# macOS .appex is a deep bundle: resources go under Contents/Resources.
# iOS .appex is a SHALLOW bundle: resources go at the bundle ROOT. Putting them
# in a Resources/ subfolder makes codesign reject the whole bundle with
# "bundle format unrecognized, invalid, or unsuitable" (a shallow bundle must
# not contain a Resources/ directory). This matches Xcode's own iOS Copy Bundle
# Resources behaviour, which writes to the appex root.
case "${PLATFORM_NAME:-}" in
  macosx) OUT="${WRAPPER}/Contents/Resources" ;;
  *)      OUT="${WRAPPER}" ;;
esac
if [ "${PLATFORM_NAME:-}" != "macosx" ]; then
  # Clean any stale layout from earlier builds (deep Contents/ or a Resources/ subfolder).
  rm -rf "${WRAPPER}/Contents" "${WRAPPER}/Resources" 2>/dev/null || true
fi
mkdir -p "${OUT}"
for f in manifest.json background.js popup.html popup.js; do
  if [ -f "${WEBROOT}/${f}" ]; then
    cp "${WEBROOT}/${f}" "${OUT}/"
  fi
done
mkdir -p "${OUT}/sites"
if [ -d "${WEBROOT}/sites" ]; then
  rsync -a --exclude ".DS_Store" "${WEBROOT}/sites/" "${OUT}/sites/"
fi
if [ -d "${WEBROOT}/icons" ]; then
  mkdir -p "${OUT}/icons"
  rsync -a --exclude ".DS_Store" "${WEBROOT}/icons/" "${OUT}/icons/"
fi
