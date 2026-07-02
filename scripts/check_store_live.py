#!/usr/bin/env python3
"""Check whether manifest.json version is live on Chrome and Firefox."""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, parse, request

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
MANIFEST = ROOT / "manifest.json"

sys.path.insert(0, str(SCRIPT_DIR / "lib"))
from load_release_env import load_release_env  # noqa: E402


@dataclass
class LiveStatus:
    store: str
    state: str  # LIVE | PENDING | BEHIND | CHECK
    live_version: str
    target_version: str
    summary: str
    detail: str = ""


def version_key(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for piece in version.split("."):
        if piece.isdigit():
            parts.append(int(piece))
    return tuple(parts) if parts else (0,)


def versions_match(left: str, right: str) -> bool:
    if left == "unknown" or right == "unknown":
        return False
    return version_key(left) == version_key(right)


def repo_version() -> str:
    return str(json.loads(MANIFEST.read_text(encoding="utf-8"))["version"])


def env(name: str) -> str:
    return os.environ.get(name, "").strip()


def http_json(url: str, *, headers: dict[str, str] | None = None, data: bytes | None = None, method: str | None = None) -> Any:
    req = request.Request(url, data=data, method=method, headers=headers or {})
    with request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def chrome_access_token() -> str:
    body = parse.urlencode(
        {
            "client_id": env("CWS_CLIENT_ID"),
            "client_secret": env("CWS_CLIENT_SECRET"),
            "refresh_token": env("CWS_REFRESH_TOKEN"),
            "grant_type": "refresh_token",
        }
    ).encode("utf-8")
    payload = http_json(
        "https://oauth2.googleapis.com/token",
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = payload.get("access_token")
    if not token:
        raise RuntimeError(f"Chrome OAuth failed: {payload}")
    return token


def amo_jwt() -> str:
    def b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    issued_at = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": env("AMO_JWT_ISSUER"),
        "jti": str(uuid.uuid4()),
        "iat": issued_at,
        "exp": issued_at + 60,
    }
    unsigned = ".".join(
        b64url(json.dumps(part, separators=(",", ":")).encode("utf-8"))
        for part in (header, payload)
    )
    signature = hmac.new(
        env("AMO_JWT_SECRET").encode("utf-8"),
        unsigned.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{unsigned}.{b64url(signature)}"


def chrome_status(target: str) -> LiveStatus:
    store = "Chrome Web Store"
    required = ["CWS_EXTENSION_ID", "CWS_CLIENT_ID", "CWS_CLIENT_SECRET", "CWS_REFRESH_TOKEN"]
    if any(not env(name) for name in required):
        return LiveStatus(store, "CHECK", "unknown", target, "credentials missing")

    extension_id = env("CWS_EXTENSION_ID")
    token = chrome_access_token()
    url = f"https://www.googleapis.com/chromewebstore/v1.1/items/{extension_id}?projection=DRAFT"
    try:
        item = http_json(url, headers={"Authorization": f"Bearer {token}", "x-goog-api-version": "2"})
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return LiveStatus(store, "CHECK", "unknown", target, "could not read item", f"HTTP {exc.code}: {body}")

    live = str(item.get("crxVersion") or "unknown")
    if versions_match(live, target):
        return LiveStatus(store, "LIVE", live, target, f"{target} is live")

    return LiveStatus(
        store,
        "PENDING" if live != "unknown" else "BEHIND",
        live,
        target,
        f"live {live}; target {target}",
        "Monitor Chrome Developer Dashboard if a submission is in review.",
    )


def firefox_status(target: str) -> LiveStatus:
    store = "Firefox AMO"
    required = ["AMO_JWT_ISSUER", "AMO_JWT_SECRET", "AMO_ADDON_ID"]
    if any(not env(name) for name in required):
        return LiveStatus(store, "CHECK", "unknown", target, "credentials missing")

    addon_id = parse.quote(env("AMO_ADDON_ID"), safe="")
    url = f"https://addons.mozilla.org/api/v5/addons/addon/{addon_id}/"
    try:
        data = http_json(url, headers={"Authorization": f"JWT {amo_jwt()}"})
    except error.HTTPError as exc:
        if exc.code == 404:
            return LiveStatus(store, "BEHIND", "none", target, "add-on not listed yet")
        body = exc.read().decode("utf-8", errors="replace")
        return LiveStatus(store, "CHECK", "unknown", target, "could not read add-on", f"HTTP {exc.code}: {body}")

    current = data.get("current_version") or {}
    live = str(current.get("version") or "unknown")
    if versions_match(live, target):
        return LiveStatus(store, "LIVE", live, target, f"{target} is live")

    for row in data.get("versions") or []:
        version = str((row.get("version") or {}).get("version") or "")
        if version != target:
            continue
        file_status = str((row.get("file") or {}).get("status") or "")
        if file_status and file_status != "public":
            return LiveStatus(
                store,
                "PENDING",
                live,
                target,
                f"live {live}; {target} is {file_status}",
            )

    return LiveStatus(store, "BEHIND", live, target, f"live {live}; target {target} not live")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether NewsMinus is live on Chrome and Firefox.")
    parser.add_argument("--version", metavar="X.Y.Z", help="Check a specific version (default: manifest.json).")
    parser.add_argument("--quiet", action="store_true", help="Only print summary when not fully live.")
    args = parser.parse_args()

    load_release_env()
    target = args.version or repo_version()
    rows = [chrome_status(target), firefox_status(target)]
    all_live = all(row.state == "LIVE" for row in rows)

    if not args.quiet or not all_live:
        print(f"NewsMinus live check (target {target})")
        print()
        for row in rows:
            print(f"{row.store}: {row.state} — live {row.live_version}; target {row.target_version}")
            print(f"  {row.summary}")
            if row.detail:
                print(f"  {row.detail}")
        print()

    if all_live:
        print(f"Summary: LIVE on Chrome and Firefox for {target}.")
        return 0

    pending = [row.store for row in rows if row.state == "PENDING"]
    behind = [row.store for row in rows if row.state == "BEHIND"]
    check = [row.store for row in rows if row.state == "CHECK"]
    parts = []
    if pending:
        parts.append(f"pending: {', '.join(pending)}")
    if behind:
        parts.append(f"behind: {', '.join(behind)}")
    if check:
        parts.append(f"check: {', '.join(check)}")
    print(f"Summary: NOT LIVE — {'; '.join(parts)}.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
