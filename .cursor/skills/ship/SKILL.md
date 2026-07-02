---
name: ship
description: >-
  Bump the NewsMinus version, commit all pending changes to master, and push.
  Use when the user says "ship", "ship it", or "bump the version number, commit
  and push". This does NOT upload to the Chrome or Firefox stores — that is the
  separate publish flow.
---

# Ship

Bump the version, commit to `master`, and push. Solo-developer flow: commit
directly to `master`, no branches/PRs/tags unless the user asks.

Not the same as **publish** (`scripts/publish-stores.sh`), which uploads to
Chrome Web Store and Firefox AMO.

## Steps

1. **Summary**: if the user didn't give one, ask for a short release summary
   (used in the commit message `vX.Y.Z: <summary>`).

2. **Bump level**:
   - **patch** (default) — bug fixes (e.g. `1.3.1 → 1.3.2`)
   - **minor** (`--minor`) — user-facing improvements (e.g. `1.3.1 → 1.4.0`)
   - **major** (`--major`) — breaking changes or new supported sites in manifest
   - **explicit** (`--version X.Y.Z`) — only when the user asks

3. **Bump all version files** with the repo tool (keeps `manifest.json`, Safari
   `MARKETING_VERSION`, `CURRENT_PROJECT_VERSION`, and regenerated
   `project.pbxproj` in sync):

```bash
python3 scripts/bump-version.py
```

   For minor: `python3 scripts/bump-version.py --minor`

   For major: `python3 scripts/bump-version.py --major`

   For explicit: `python3 scripts/bump-version.py --version X.Y.Z`

   Read the script output for `$NEW` before committing (`next: X.Y.Z`).

4. **Validate** changed JS when `sites/` was touched:

```bash
node --check sites/nyt-betamax-main.js
```

5. **Commit everything** (code changes plus version bump) in one commit on
   `master`, then push:

```bash
git add -A
git commit -m "v$NEW: <summary>"
git push origin master
```

6. **Report** the new version and confirm the push to `origin master`.

## Notes

- Stay on `master`. If on another branch, move work to `master` rather than
  opening a PR.
- No git tag unless the user explicitly asks.
- Building zip/xpi is optional during ship; **publish** builds artifacts.
