# Full release (version + stores)

Bump version, commit, tag, push, build all artifacts, and publish to Chrome, Firefox, and Safari.

Requires a **clean** git tree. Read **`.cursor/skills/publish-newsminus/SKILL.md`**.

## What to do

1. If the user did not give a release summary, ask for a short one.
2. Confirm the working tree is clean (or ask them to commit/stash first).
3. Run from the repo root:

```bash
./scripts/release.sh "summary here"
```

Add `--major` or `--version X.Y.Z` when appropriate. Use `--skip-publish` for bump + artifacts only.

4. Report version, git tag, artifact paths, and which stores were submitted.

For **publish current version only** (no bump), use **`/publish`** instead.
