#!/usr/bin/env python3
"""Check Chrome Web Store and Firefox AMO for pending submissions."""

from __future__ import annotations

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
class StoreStatus:
    store: str
    state: str  # READY | PENDING | CHECK
    summary: str
    detail: str = ""


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


def chrome_status(target: str) -> StoreStatus:
    store = "Chrome Web Store"
    required = ["CWS_EXTENSION_ID", "CWS_CLIENT_ID", "CWS_CLIENT_SECRET", "CWS_REFRESH_TOKEN"]
    if any(not env(name) for name in required):
        return StoreStatus(store, "CHECK", "credentials missing", "Set CWS_* vars or Nunus release.env")

    extension_id = env("CWS_EXTENSION_ID")
    token = chrome_access_token()
    url = f"https://www.googleapis.com/chromewebstore/v1.1/items/{extension_id}?projection=DRAFT"
    try:
        item = http_json(url, headers={"Authorization": f"Bearer {token}", "x-goog-api-version": "2"})
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return StoreStatus(store, "CHECK", "could not read item", f"HTTP {exc.code}: {body}")

    live_version = str(item.get("crxVersion") or "unknown")
    statuses = item.get("status") or []
    status_text = ", ".join(str(s) for s in statuses) if statuses else "unknown"

    if live_version == target and "pendingReview" not in status_text.lower():
        return StoreStatus(store, "READY", f"live {live_version}; no draft pending")

    if live_version == target:
        return StoreStatus(
            store,
            "PENDING",
            f"live {live_version}; item status {status_text}",
            "Chrome may reject uploads while a submission is in review.",
        )

    if live_version != target:
        return StoreStatus(
            store,
            "PENDING",
            f"live {live_version}; draft/target {target}",
            "A newer version may be in review or staged.",
        )

    return StoreStatus(store, "CHECK", f"status {status_text}", "Confirm in Chrome Developer Dashboard.")


def firefox_status(target: str) -> StoreStatus:
    store = "Firefox AMO"
    required = ["AMO_JWT_ISSUER", "AMO_JWT_SECRET", "AMO_ADDON_ID"]
    if any(not env(name) for name in required):
        return StoreStatus(store, "CHECK", "credentials missing", "Set AMO_* vars in release.env")

    addon_id = parse.quote(env("AMO_ADDON_ID"), safe="")
    url = f"https://addons.mozilla.org/api/v5/addons/addon/{addon_id}/"
    try:
        data = http_json(url, headers={"Authorization": f"JWT {amo_jwt()}"})
    except error.HTTPError as exc:
        if exc.code == 404:
            return StoreStatus(store, "READY", "add-on not listed yet", "First listed submission uses web-ext sign.")
        body = exc.read().decode("utf-8", errors="replace")
        return StoreStatus(store, "CHECK", "could not read add-on", f"HTTP {exc.code}: {body}")

    current = data.get("current_version") or {}
    live_version = str(current.get("version") or "unknown")
    if live_version == target:
        return StoreStatus(store, "READY", f"live {target}")

    versions = data.get("versions") or []
    for row in versions:
        version = str((row.get("version") or {}).get("version") or "")
        if version != target:
            continue
        file_status = str((row.get("file") or {}).get("status") or "")
        if file_status and file_status != "public":
            return StoreStatus(
                store,
                "PENDING",
                f"live {live_version}; {target} is {file_status}",
                "Monitor AMO Developer Hub until review completes.",
            )

    return StoreStatus(
        store,
        "READY",
        f"live {live_version}; target {target} not submitted",
        "Safe to publish if you intend to ship a new version.",
    )


def main() -> int:
    load_release_env()
    target = repo_version()
    rows = [chrome_status(target), firefox_status(target)]

    print(f"NewsMinus publish pending check (manifest {target})")
    print()
    pending = False
    check = False
    for row in rows:
        print(f"{row.store}: {row.state} — {row.summary}")
        if row.detail:
            print(f"  {row.detail}")
        if row.state == "PENDING":
            pending = True
        if row.state == "CHECK":
            check = True

    print()
    if pending:
        print("Summary: PENDING — wait for in-flight reviews before publishing the same store.")
        return 1
    if check:
        print("Summary: CHECK — verify manually before publishing Chrome/Firefox.")
        return 1
    print("Summary: READY — no pending submissions detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
