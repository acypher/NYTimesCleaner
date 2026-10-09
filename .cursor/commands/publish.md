# Publish NewsMinus to Chrome, Firefox, and Safari

Build and upload the current `manifest.json` version to **Chrome Web Store**,
**Firefox AMO**, and the **Apple App Store** (Safari macOS + iOS, submitted for
App Review automatically).

Read and follow **`.cursor/skills/publish-newsminus/SKILL.md`** completely.

## Two modes

| User intent | Action |
|-------------|--------|
| **Publish** current version to stores | `./scripts/publish-stores.sh` |
| **New release** (bump + git tag + publish) | `./scripts/release.sh "summary"` |

Default to **publish-stores** when the user says "publish" and does not ask for a version bump.

Use **release.sh** when they want to ship **new** changes: uncommitted work should be committed first, or they provide a release summary for a version bump on a clean tree.

## Before publish

Run these from the repo root **before** `./scripts/publish-stores.sh`:

```bash
./scripts/check-release-credentials.sh
./scripts/check-store-pending.sh
```

- **Credentials check** must pass (`scripts/release.env` or shared Nunus `release.env`).
- **Pending check** must exit **0 (READY)**. If any store is **PENDING** or **CHECK**, stop and explain — do not publish until clear (or publish only the stores that are ready, if the user asks).

`publish-stores.sh` also runs credential and pending checks before uploading; running them first avoids a long build when a store is not ready.

## What to do

1. If the user did not say whether they want a **new version bump**, assume **publish current version** (`./scripts/publish-stores.sh`).
2. If they want a **tagged release + publish**, use `./scripts/release.sh "summary"` (requires clean tree).
3. If they want bump + commit + push **without** stores, use **ship** or `/version`.
4. Run the **Before publish** checks above. If either fails, stop.
5. Run `./scripts/publish-stores.sh` (or `--dry-run`, `--chrome-only`, `--firefox-only`, `--safari-only`, `--no-safari`, `--no-ios` as appropriate).
6. If Safari upload succeeds but submit fails, fix in App Store Connect and re-run `./scripts/submit-safari-appstore.sh --skip-wait` (or `submit-safari-ios.sh --skip-wait`).
7. Report version, artifact paths (zip/xpi/pkg/ipa), which stores were submitted, and confirm **daily publish-check** was armed (unless `PUBLISH_CHECK_SKIP_DAILY=1`).

Do **not** bump the version unless the user asked for a release first.

**One-time iOS prerequisite:** the iOS app record (`com.nunus.NYTimesCleanerHost.ios`)
must exist in App Store Connect before the first iOS publish.

Do **not** run `version-commit.sh` alone unless they only want GitHub/zip (that is **`/version`**, not publish).
