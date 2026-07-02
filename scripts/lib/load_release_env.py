#!/usr/bin/env python3
"""Load release env for Python scripts (mirrors scripts/lib/load-release-env.sh)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOADER = ROOT / "scripts" / "lib" / "load-release-env.sh"


def load_release_env() -> None:
    if not LOADER.is_file():
        return
    env = os.environ.copy()
    result = subprocess.run(
        ["bash", "-c", f'source "{LOADER}" && env -0'],
        check=True,
        capture_output=True,
        text=False,
    )
    for chunk in result.stdout.split(b"\0"):
        if not chunk or b"=" not in chunk:
            continue
        key, value = chunk.split(b"=", 1)
        os.environ[key.decode("utf-8")] = value.decode("utf-8")
