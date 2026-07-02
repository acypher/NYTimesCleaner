#!/usr/bin/env bash
# Check Chrome and Firefox for pending submissions before publish.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
exec python3 "$SCRIPT_DIR/check_store_pending.py"
