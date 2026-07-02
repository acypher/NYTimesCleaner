---
name: publish-check
description: >-
  Check Chrome Web Store and Firefox AMO to see whether manifest.json version
  is live. Use when the user says publishCheck, publish check, check store
  status, is the release live, or asks whether a version is available on stores.
---

# Publish check

Verify that the version in `manifest.json` is **live** (available to users) on
Chrome and Firefox.

Safari is not checked automatically — confirm manually in Xcode / App Store
Connect if applicable.

## Run

From the **NewsMinus repo root**:

```bash
./scripts/check-store-live.sh
```

Requires credentials via `scripts/release.env` or shared Nunus `release.env`.
Exit **0** only when Chrome and Firefox both report **LIVE** for the repo version.

Check a specific published version (while `manifest.json` has moved on):

```bash
./scripts/check-store-live.sh --version 1.3.1
```

Quiet mode (useful for scripts):

```bash
./scripts/check-store-live.sh --version 1.3.1 --quiet
```

## Interpret results

| State | Meaning |
|-------|---------|
| **LIVE** | Store is serving the target version to users. |
| **PENDING** | Target version submitted or in review; older version still live. |
| **BEHIND** | Target version not live and no in-flight submission detected — may need publish or failed review. |
| **CHECK** | Could not determine (missing credentials or API gap). |

### Chrome

Uses Web Store API v1.1 with `CWS_EXTENSION_ID`. Without OAuth credentials, Chrome
shows **CHECK** — open the
[Chrome Developer Dashboard](https://chrome.google.com/webstore/devconsole)
manually.

### Firefox

Uses AMO API with `AMO_ADDON_ID` (`nytimescleaner@nunus.extension` / slug
`newsminus`). Unreviewed listed builds show **PENDING**.

## Report to the user

After running the script, summarize in a short table:

| Store | State | Live | Target |
|-------|-------|------|--------|

Include the script **Summary** line. If **NOT LIVE**, say which stores are still
**PENDING** vs **BEHIND** vs **CHECK** and what to do next (wait, re-publish,
fix credentials, check dashboard).

## Related commands

| Goal | Script |
|------|--------|
| Can we publish again? (nothing in review) | `./scripts/check-store-pending.sh` |
| Ship a new build to stores | `./scripts/publish-stores.sh` (see **publish-newsminus** skill) |
| Is the release live? | `./scripts/check-store-live.sh` |

Run **pending** before publish; run **live** after publish or when the user asks
if a version shipped.

## Do not confuse with

- **`check-store-pending.sh`** — blocks publish when submissions are in flight;
  does **not** confirm live availability.
- **Store dashboards** — use when API returns **CHECK** or the user wants manual
  confirmation.
