# Version commit to GitHub

Bump the NewsMinus version, commit, tag, push to GitHub, and build Chrome zip + Firefox xpi. Does **not** build Safari or publish to stores.

Read and follow the **version-bumping** rule. Default bump is **minor**.

## What to do

1. If the user did not give a release summary, ask for a short one (used in `version X.Y.Z: <summary>`).
2. If the working tree is dirty, stop and tell them to commit or stash unrelated changes first.
3. Determine bump level from the user's message:
   - **major** (`--major`) — new supported site in `manifest.json`, or they explicitly asked for a major release
   - **minor** (default) — improvements within existing sites
4. Run from the repo root:

```bash
./scripts/version-commit.sh --package "summary here"
```

Add `--major` or `--version X.Y.Z` when appropriate. Use `--dry-run` only if the user asks to preview.

5. Report the new version, tag, branch pushed, and paths to `../NewsMinus-X.Y.Z.zip` and `../NewsMinus-X.Y.Z.xpi`.

Do not run `./scripts/release.sh` unless the user explicitly asks for Safari build or store publish.
