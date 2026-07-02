#!/usr/bin/env bash
# Check whether manifest.json version is live on Chrome and Firefox.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
exec python3 "$SCRIPT_DIR/check_store_live.py" "$@"
