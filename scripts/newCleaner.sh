#!/usr/bin/env bash
# Versioned Chrome Web Store zip + Firefox .xpi (manifest version in filenames).
#
# Chrome zip details (work around vague Web Store "try again" / unzip failures):
# - Omits browser_specific_settings (Firefox-only keys).
# - Writes the archive with Python zipfile + ZIP_DEFLATED (some macOS `zip` builds
#   or xattrs confuse the store backend while chrome://extensions unpacked is fine).
# - Copies with COPYFILE_DISABLE=1 to avoid AppleDouble files.
#
#   newCleaner() { /path/to/NewsMinus/scripts/newCleaner.sh "$@"; }
#
# Optional: NYTNA_EXTENSION_ROOT=/other/clone ./scripts/newCleaner.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
ROOT="${NYTNA_EXTENSION_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
PARENT="$(cd "$ROOT/.." && pwd)"

ver="$(python3 -c "import json; print(json.load(open('$ROOT/manifest.json'))['version'])")"
ZIP="$PARENT/NewsMinus-${ver}.zip"

rm -f "$ZIP"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/nytna-chromezip.XXXXXX")"
cleanup() {
  rm -rf "$TMP"
}
trap cleanup EXIT

export COPYFILE_DISABLE=1
export NYTNA_ROOT="$ROOT"
export NYTNA_TMP="$TMP"
export NYTNA_ZIP_OUT="$ZIP"

python3 - <<'PY'
import json
import os
import shutil
import zipfile
from pathlib import Path

root = Path(os.environ["NYTNA_ROOT"])
tmp = Path(os.environ["NYTNA_TMP"])
zip_path = Path(os.environ["NYTNA_ZIP_OUT"])

m = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
m.pop("browser_specific_settings", None)
m.setdefault("minimum_chrome_version", "111")
(tmp / "manifest.json").write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")

for name in ("background.js", "popup.html", "popup.js", "sites", "icons"):
    src = root / name
    dst = tmp / name
    if src.is_file():
        shutil.copy2(src, dst, follow_symlinks=True)
    elif src.is_dir():
        shutil.copytree(
            src,
            dst,
            symlinks=False,
            ignore_dangling_symlinks=True,
            dirs_exist_ok=False,
        )

files = []
for p in tmp.rglob("*"):
    if not p.is_file():
        continue
    arc = p.relative_to(tmp).as_posix()
    if arc.startswith(".") or "/." in arc:
        continue
    files.append((p, arc))
files.sort(key=lambda t: (0 if t[1] == "manifest.json" else 1, t[1]))

with zipfile.ZipFile(
    zip_path,
    "w",
    compression=zipfile.ZIP_DEFLATED,
    compresslevel=6,
) as zf:
    for path, arcname in files:
        zf.write(path, arcname, compress_type=zipfile.ZIP_DEFLATED)

assert zip_path.is_file(), zip_path
PY

echo "Wrote $ZIP (Python zipfile; Chrome Web Store manifest)"

echo "Building Firefox .xpi: $PARENT/NewsMinus-${ver}.xpi"
env NYTNA_EXTENSION_ROOT="$ROOT" NYTNA_XPI="$PARENT/NewsMinus-${ver}.xpi" \
  "$SCRIPT_DIR/build-newsminus-firefox-xpi.sh"

echo "Wrote $PARENT/NewsMinus-${ver}.xpi"
