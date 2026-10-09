---
name: ship
description: >-
  Bump the NewsMinus version (minor), commit all pending changes to master, and
  push. Use when the user says "ship", "ship it", or "bump the version number,
  commit and push". This does NOT upload to stores — that is the separate
  publish flow.
---

# Ship

Bump the version, commit to `master`, and push. Solo-developer flow: commit
directly to `master`, no branches/PRs/tags (see the git-workflow rule).

Not the same as **publish** (`scripts/publish-stores.sh`), which uploads to
Chrome, Firefox, and Safari stores.

For a **tagged release + store publish**, use `./scripts/release.sh "summary"`
instead (requires a clean git tree).

## Steps

1. **Summary**: if the user didn't give one, ask for a short release summary
   (used in the commit message `version X.Y.Z: <summary>`).

2. **Bump level**: default is **minor** (e.g. `2.0.1 → 2.1.0`). Use `--major`
   only if the user asks or `manifest.json` gains a new supported site. Use
   `--version X.Y.Z` only when the user asks for an explicit version (e.g. patch).

3. **Bump all version files** with the repo tool (keeps `manifest.json`, Safari
   `MARKETING_VERSION`, `CURRENT_PROJECT_VERSION`, and regenerated
   `project.pbxproj` in sync):

```bash
python3 scripts/bump-version.py
```

   For a major bump: `python3 scripts/bump-version.py --major`.

   For an explicit version: `python3 scripts/bump-version.py --version X.Y.Z`.

   Read the script output for `$NEW` before committing (`next: X.Y.Z`).

4. **Validate** changed JS when `sites/` was touched:

```bash
node --check sites/nyt-betamax-main.js
```

5. **Commit everything** (code changes plus version bump) in one commit on
   `master`, then push:

```bash
git add -A
git commit -m "version $NEW: <summary>"
git push origin master
```

6. **Report** the new version and confirm the push to `origin master`.

## Notes

- Stay on `master`. If on another branch, move work to `master` rather than
  opening a PR.
- No git tag (the `/version` command is the tagging + zip/xpi flow; `ship` is
  intentionally lighter).
- Agent edits bump **patch** automatically per **agent-patch-version**; use
  **ship** when the user wants a deliberate release bump (usually minor).
