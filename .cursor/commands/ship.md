# Ship NewsMinus

Bump the version, commit all pending changes to `master`, and push.

Read and follow **`.cursor/skills/ship/SKILL.md`** completely.

## What to do

1. If the user did not give a release summary, ask for a short one.
2. Default bump is **minor** unless they asked for major/explicit version.
3. Run `python3 scripts/bump-version.py` (add `--major` or `--version X.Y.Z` when appropriate).
4. Commit on `master` with message `version X.Y.Z: <summary>` and push to `origin master`.
5. Report the new version.

Do **not** run `./scripts/publish-stores.sh` unless the user also asked to publish.

For a **tagged release + store publish** (clean tree required), use **`/release`**
or `./scripts/release.sh "summary"` instead.
