---
name: publish-newsminus
description: >-
  Build and publish NewsMinus to Chrome Web Store, Firefox AMO, and the Apple
  App Store (Safari, macOS + iOS). Use when the user says publish NewsMinus,
  publish newsminus, publish to stores, ship to Chrome/Firefox/Safari, or run a
  store release.
---

# Publish NewsMinus

End-to-end store publish for the NewsMinus browser extension in this repo.

Stores covered: **Chrome Web Store**, **Firefox AMO**, and the **Apple App
Store** — Safari ships as a macOS app (`com.nunus.NYTimesCleanerHost`) and a
separate iOS app (`com.nunus.NYTimesCleanerHost.ios`), both fully automated
(archive → upload → submit for App Review via the App Store Connect API).

## Two modes

| User intent | Action |
|-------------|--------|
| **Publish** current version to stores | `./scripts/publish-stores.sh` |
| **New release** (bump + git tag + publish) | `./scripts/release.sh "summary"` |
| **Ship** (bump + commit + push, no tag/stores) | **ship** skill / `./scripts/bump-version.py` + git commit |

Default to **publish-stores** when the user says "publish" and does not ask for
a version bump.

Use **release.sh** when they want to ship **new** changes with a tagged release:
uncommitted work should be committed first (clean tree), or they provide a release
summary for `version-commit.sh`.

Use **ship** for a lighter bump + commit + push on `master` (no tag, no stores).

## Before publish

Do **not** run `./scripts/publish-stores.sh` until these pass:

1. Run from the **NewsMinus repo root** (`NewsMinus` workspace).
2. Confirm `manifest.json` version is what they intend to ship.
3. Credentials configured:

```bash
./scripts/check-release-credentials.sh
```

Credentials live in `scripts/release.env` (copy from `scripts/release.env.example`)
or inherit Chrome OAuth / AMO keys / Apple team + ASC API key from
`../nunus/NunusCursor/scripts/release.env` (loaded automatically; local values
override). Do not commit `release.env`.

4. **No pending submissions** on any store:

```bash
./scripts/check-store-pending.sh
```

**Stop if exit code is non-zero.** Interpret the summary:

| Result | Meaning |
|--------|---------|
| **READY** | Safe to publish. |
| **PENDING** | A store has a submission in flight — wait or publish only the ready stores. |
| **CHECK** | Could not verify automatically — confirm in store dashboards before publishing. |

Optional dry run after the checks pass:

```bash
./scripts/publish-stores.sh --dry-run
```

`publish-stores.sh` also runs the credential and pending checks automatically before uploading; running them first avoids a long build when a store is not ready.

## Publish current version (usual)

```bash
./scripts/publish-stores.sh
```

This builds `../NewsMinus-<version>.zip` and `.xpi`, archives the Safari
macOS `.pkg` and iOS `.ipa`, then uploads to:

- **Chrome** — `publish-chrome.py`
- **Firefox** — `publish-firefox.sh` (web-ext sign from staged source)
- **Safari (macOS)** — App Store Connect upload + automated submit-for-review
- **Safari (iOS)** — App Store Connect upload + automated submit-for-review

When ASC API credentials are configured, **Safari submit-for-review is
automated** after upload (waits for build processing, creates/reuses the App
Store version, attaches the build, sets export compliance, patches the listing
from `docs/description.md`, sets What's New, submits via `reviewSubmissions`).
Set `APP_STORE_SKIP_SUBMIT=1` to upload only.

Store-specific flags:

```bash
./scripts/publish-stores.sh --chrome-only
./scripts/publish-stores.sh --firefox-only
./scripts/publish-stores.sh --safari-only
./scripts/publish-stores.sh --no-safari    # Chrome + Firefox only
./scripts/publish-stores.sh --no-ios       # skip iOS (or PUBLISH_INCLUDE_IOS=0)
./scripts/publish-stores.sh --no-build     # use existing zip/xpi artifacts
./scripts/publish-stores.sh --build-only   # build everything, upload nothing
```

## iOS Safari (iPhone/iPad) — included by default

The iOS Safari extension ships as a **separate App Store app**
(`com.nunus.NYTimesCleanerHost.ios`, Xcode target `NewsMinusHostIOS`).

**One-time prerequisite (only manual step):** the iOS app record must exist in
App Store Connect. Apple's API cannot create app records — create it once in
ASC (New App → iOS, bundle id `com.nunus.NYTimesCleanerHost.ios`), then the
automation handles every subsequent release. (The macOS app record must also
exist for the macOS flow.)

### iOS signing is fully headless (no GUI prompts)

iOS Release configs use **Manual** signing (Debug stays Automatic for the
simulator). `build-safari-ios.sh` provisions everything itself:

- **Bundle IDs** (`…ios` + `…ios.extension`) and two **App Store provisioning
  profiles** (`NewsMinus iOS App Store`, `NewsMinus iOS Extension App Store`)
  are registered/created via the ASC API by `./scripts/ensure-ios-signing.sh`
  (idempotent; runs automatically when profiles are missing).
- **Certificate**: the *Apple Distribution* identity is **shared with Nunus**
  (same team). A local `scripts/keys/ios-signing/dist.p12` wins; otherwise
  `../nunus/NunusCursor/scripts/keys/ios-signing/dist.p12` is used. Password in
  `dist.p12.password` next to the file.
- **Keychain**: the identity is imported into a dedicated, self-passworded
  keychain at `safari/build/newsminus-ios-signing.keychain-db` so codesign
  never prompts the login keychain.

If no `.p12` can be found, the script falls back to Automatic signing +
`-allowProvisioningUpdates` (fails on accounts with no registered devices —
that's why Manual signing is the default path).

**Shallow-bundle gotcha (do not regress):** an iOS `.appex` is a *shallow*
bundle, so web-extension resources must live at the appex **root**, never in a
`Resources/` subfolder — a `Resources/` dir makes codesign reject the bundle
("bundle format unrecognized, invalid, or unsuitable").
`safari/scripts/copy-web-extension-resources.sh` writes to the root for iOS
(and `Contents/Resources` for macOS).

iOS-only scripts (mirror the macOS trio):

```bash
IPA="$(./scripts/build-safari-ios.sh | tail -1)"   # archive NewsMinusHostIOS, export .ipa
./scripts/publish-safari-ios.sh "$IPA"             # upload .ipa via altool
./scripts/submit-safari-ios.sh                     # attach build + submit for review (platform IOS)
```

## Firefox listed submissions

After the add-on exists on AMO (`newsminus` slug), prefer `publish-stores.sh`.

If AMO version-create returns **404** (add-on not listed yet) or validation
needs listing metadata, use **web-ext sign**:

```bash
./scripts/publish-firefox.sh
```

First listed submission requires `scripts/amo-metadata.json`. Requires
`web-ext` CLI (`npm install -g web-ext`).

## Chrome listing copy

- Short description comes from `manifest.json` `description` (slogan, ≤132 chars).
- Full marketing description: `scripts/store-listing.txt` — paste into the
  [Chrome Developer Dashboard](https://chrome.google.com/webstore/devconsole)
  when renaming or updating the listing.
- App Store description/subtitle come from `docs/description.md` (synced
  automatically during Safari submit; subtitle = first line, ≤30 chars).

## Full release (bump + git + publish)

When the user wants a **new version** committed and tagged, then published:

```bash
./scripts/release.sh "short summary of this release"
```

Requires a **clean** git tree. Adds `--major` or `--version X.Y.Z` when they specify.

`release.sh` runs `version-commit.sh --package` (bump, commit, tag, push, zip/xpi) then `publish-stores.sh`.

Or `./scripts/release.sh --skip-publish "summary"` for bump + artifacts without stores.

## Build only (no upload)

```bash
./scripts/newCleaner.sh                    # zip + xpi only
./scripts/publish-stores.sh --build-only   # zip + xpi + Safari pkg/ipa
```

## On failure

- Credentials check fails → list missing vars; artifacts may still build.
- Chrome **ITEM_NOT_UPDATABLE** → a version is already in review; wait.
- Safari upload succeeded but submit failed → fix in ASC (export compliance,
  listing gaps), then `./scripts/submit-safari-appstore.sh --skip-wait` (or
  `submit-safari-ios.sh --skip-wait`).
- iOS build fails → check the iOS platform is installed in Xcode and that the
  ASC app record for `com.nunus.NYTimesCleanerHost.ios` exists;
  `./scripts/ensure-ios-signing.sh` re-provisions profiles.
- One store fails → report which step failed; do not claim the others succeeded.
- Re-run publish after fixing credentials or pending state (safe to rebuild the
  same version).

## Do not confuse with

- **ship** skill — bump version, commit, push; **no** tag, **no** store upload.
- **`/version`** or `version-commit.sh` — GitHub + zip/xpi only, **no** Safari or stores.
- **Unpacked load** in `chrome://extensions` — local dev only.
- **Xcode GUI archive** — superseded by `build-safari-mac.sh` / `build-safari-ios.sh`.

## After success

Report:

- Version from `manifest.json`
- Paths to zip/xpi (and Safari .pkg/.ipa)
- Chrome and Firefox: submitted for store review — monitor dashboards
- Safari (macOS + iOS): uploaded + **submitted for App Review via API** —
  monitor [App Store Connect](https://appstoreconnect.apple.com/)

| Store | Dashboard |
|-------|-----------|
| Chrome | [Developer Dashboard](https://chrome.google.com/webstore/devconsole) |
| Firefox | [AMO Developer Hub](https://addons.mozilla.org/developers/) |
| Safari (macOS + iOS) | [App Store Connect](https://appstoreconnect.apple.com/) |

Re-run `./scripts/check-store-pending.sh` after publish; expect **PENDING**
while reviews are in progress.

See **publish-check** skill for live availability (Safari versions approved by
Apple in PENDING_DEVELOPER_RELEASE are auto-released by the check unless
`APP_STORE_AUTO_RELEASE=0`).

## Daily publish-check until live (automatic)

Every successful `./scripts/publish-stores.sh` (not `--build-only` or `--dry-run`) concludes by arming a **daily local check** via macOS `launchd`:

```bash
./scripts/setup-publish-check-daily.sh --version <published-version>
```

`publish-stores.sh` runs this automatically unless `PUBLISH_CHECK_SKIP_DAILY=1`.

Once per day (default **09:00** local; override with `PUBLISH_CHECK_DAILY_HOUR` / `PUBLISH_CHECK_DAILY_MINUTE` in `release.env`):

1. Run the same logic as **publishCheck** (`check_store_live.py`) for the **published version** stored in `scripts/.publish-check-watch.json`.
2. If Safari is **PENDING_DEVELOPER_RELEASE**, automatically release via App Store Connect API (unless `APP_STORE_AUTO_RELEASE=0`).
3. If **not** live on all stores: silent (logged to `scripts/logs/publish-check-watch.log`).
4. When **live on all stores** (Chrome, Firefox, Safari macOS + iOS): email **`code@acypher.com`** (override with `PUBLISH_CHECK_NOTIFY_EMAIL`), then stop the daily schedule.

Manual controls:

```bash
./scripts/setup-publish-check-daily.sh --status
./scripts/setup-publish-check-daily.sh --stop
./scripts/run-publish-check-watch.sh   # one check now
```
