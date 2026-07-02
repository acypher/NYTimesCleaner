---
name: publish-newsminus
description: >-
  Build and publish NewsMinus to Chrome Web Store and Firefox AMO. Use when the
  user says publish NewsMinus, publish newsminus, publish to stores, ship to
  Chrome/Firefox, or run a store release.
---

# Publish NewsMinus

End-to-end store publish for the NewsMinus browser extension in this repo.

Stores covered: **Chrome Web Store** and **Firefox AMO**. Safari ships via Xcode
(`safari/NYTimesCleanerSafari.xcodeproj`) — manual, not automated here.

## Two modes

| User intent | Action |
|-------------|--------|
| **Publish** current version to stores | `./scripts/publish-stores.sh` |
| **Ship + publish** (bump, commit, push, then publish) | Run **ship** skill first, then publish |

Default to **publish-stores** when the user says "publish" and does not ask for
a version bump.

## Before publish

Do **not** run `./scripts/publish-stores.sh` until these pass:

1. Run from the **NewsMinus repo root** (`NYTimesCleaner` workspace).
2. Confirm `manifest.json` version is what they intend to ship.
3. Credentials configured:

```bash
./scripts/check-release-credentials.sh
```

Credentials live in `scripts/release.env` (copy from `scripts/release.env.example`)
or inherit OAuth/AMO keys from `../nunus/NunusCursor/scripts/release.env`.
Do not commit `release.env`.

4. **No pending submissions** on Chrome or Firefox:

```bash
./scripts/check-store-pending.sh
```

**Stop if exit code is non-zero.** Interpret the summary:

| Result | Meaning |
|--------|---------|
| **READY** | Safe to publish. |
| **PENDING** | A store has a submission in flight — wait or publish only the ready store. |
| **CHECK** | Could not verify automatically — confirm in store dashboards before publishing. |

Optional dry run:

```bash
./scripts/publish-stores.sh --dry-run
```

## Publish current version (usual)

Source credentials (maps Nunus OAuth → NewsMinus store IDs):

```bash
source scripts/lib/load-release-env.sh
./scripts/publish-stores.sh
```

This builds `../NYTimesCleaner-<version>.zip` and `.xpi`, then uploads to:

- **Chrome** — Web Store API v1.1 (`CWS_EXTENSION_ID`, default `hkiiglaagokcdpagbblfhmdobblfelpn`)
- **Firefox** — AMO upload API via `publish-stores.sh`

Store-specific flags:

```bash
./scripts/publish-stores.sh --chrome-only
./scripts/publish-stores.sh --firefox-only
./scripts/publish-stores.sh --no-build    # use existing artifacts
```

## Firefox listed submissions

After the add-on exists on AMO (`newsminus` slug), prefer `publish-stores.sh`.

If AMO version-create returns **404** (add-on not listed yet) or validation
needs listing metadata, use **web-ext sign**:

```bash
./scripts/publish-firefox.sh
```

First listed submission requires `scripts/amo-metadata.json` (summary,
description, license, categories). Updates reuse the listing; metadata is optional
after the first version.

Requires `web-ext` CLI (`npm install -g web-ext`).

## Chrome listing copy

- Short description comes from `manifest.json` `description` (slogan, ≤132 chars).
- Full marketing description: `scripts/store-listing.txt` — paste into the
  [Chrome Developer Dashboard](https://chrome.google.com/webstore/devconsole)
  when renaming or updating the listing.

## Build only (no upload)

```bash
./scripts/newCleaner.sh
```

Artifacts: `../NYTimesCleaner-<version>.zip` and `.xpi`.

## On failure

- Credentials check fails → list missing vars; artifacts may still build.
- Chrome **ITEM_NOT_UPDATABLE** → a version is already in review; wait for
  review to finish before uploading again.
- One store fails → report which step failed; do not claim both succeeded.
- Re-run publish after fixing credentials or pending state.

## Do not confuse with

- **ship** skill — bump version, commit, push; **no** store upload.
- **Unpacked load** in `chrome://extensions` — local dev only.

## After success

Report:

- Version from `manifest.json`
- Paths to zip/xpi
- Chrome and Firefox: submitted for store review — monitor dashboards

| Store | Dashboard |
|-------|-----------|
| Chrome | [Developer Dashboard](https://chrome.google.com/webstore/devconsole) |
| Firefox | [AMO Developer Hub](https://addons.mozilla.org/developers/) |

Re-run `./scripts/check-store-pending.sh` after publish; expect **PENDING** while
reviews are in progress.

See **publish-check** skill for live availability.
