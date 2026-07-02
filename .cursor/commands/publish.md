# Publish NewsMinus to Chrome and Firefox

Build and upload the current `manifest.json` version to **Chrome Web Store** and **Firefox AMO**.

Read and follow **`.cursor/skills/publish-newsminus/SKILL.md`** completely.

## Before publish

Run these from the repo root **before** `./scripts/publish-stores.sh`:

```bash
./scripts/check-release-credentials.sh
./scripts/check-store-pending.sh
```

- **Credentials check** must pass (`scripts/release.env` or shared Nunus `release.env`).
- **Pending check** must exit **0 (READY)**. If any store is **PENDING** or **CHECK**, stop and explain — do not publish until clear (or publish only the stores that are ready, if the user asks).

## What to do

1. If the user did not say whether they want a **new version bump**, assume **publish current version** (`./scripts/publish-stores.sh` after sourcing `scripts/lib/load-release-env.sh`).
2. If they want to ship **new uncommitted changes** or asked for a **version bump**, run the **ship** command/skill first.
3. Run the **Before publish** checks above. If either fails, stop.
4. Run `./scripts/publish-stores.sh` (or `--dry-run`, `--chrome-only`, `--firefox-only` as appropriate).
5. If Firefox publish fails with AMO 404 on version create, use `./scripts/publish-firefox.sh` instead.
6. Report version, artifact paths, and which stores were submitted for review.

Do **not** bump the version unless the user asked to ship new changes first.
