---
id: 9867fd3d-5a0a-4c6f-9979-86f4f988489b
---

# Tags and Versioning

## Lightweight vs Annotated Tags
<!-- bite: e963fdbd-d13b-4bc0-8274-efc7755d1776 -->

**Lightweight tag** — just a named pointer to a commit. Like a branch that doesn't move. No metadata.

**Annotated tag** — a full Git object with tagger name, email, date, message, and optionally a GPG signature. Use for releases.

```bash
# Lightweight
git tag v1.0.0                         # Tag current commit
git tag v1.0.0 a1b2c3d                 # Tag a specific commit

# Annotated (use for releases)
git tag -a v1.0.0 -m "Release 1.0.0"  # Annotated tag
git tag -a v1.0.0 a1b2c3d -m "Release 1.0.0"  # Specific commit

# Signed (requires GPG setup — see 16-hooks-and-signing)
git tag -s v1.0.0 -m "Release 1.0.0"

# Listing tags
git tag                                # List all tags
git tag -l "v1.*"                      # List matching pattern
git tag -n                             # List with tag messages

# Inspecting
git show v1.0.0                        # Show tag and tagged commit

# Pushing tags
git push origin v1.0.0                 # Push specific tag
git push origin --tags                 # Push all tags
git push origin --follow-tags          # Push only annotated tags

# Deleting tags
git tag -d v1.0.0                      # Delete local tag
git push origin --delete v1.0.0        # Delete remote tag

# Checking out a tag (detached HEAD)
git checkout v1.0.0
git checkout -b hotfix/1.0.1 v1.0.0   # Create branch from tag
```

## Semantic Versioning with Tags
<!-- bite: 846a446f-f91d-447c-9f82-4b9f63b270b2 -->

```bash
# MAJOR.MINOR.PATCH
# v1.0.0 — initial release
# v1.0.1 — patch (bug fix, backwards compatible)
# v1.1.0 — minor (new feature, backwards compatible)
# v2.0.0 — major (breaking change)

# Pre-release versions
git tag -a v2.0.0-alpha.1 -m "Alpha 1"
git tag -a v2.0.0-rc.1 -m "Release Candidate 1"
```

---

---

## The SemVer Contract
<!-- bite: 853e2bdd-69fc-4daf-bfb4-ef305e95810f -->

SemVer (`MAJOR.MINOR.PATCH`) is a communication tool — it tells users of your software what kind of change to expect:

```
v1.0.0   Initial stable release
v1.0.1   Bug fix — update safely, nothing will break
v1.1.0   New feature — update safely, you get new capabilities
v2.0.0   Breaking change — read the migration guide before updating

Pre-release identifiers (lower precedence than the release):
v2.0.0-alpha.1   → v2.0.0-alpha.2   → v2.0.0-beta.1   → v2.0.0-rc.1   → v2.0.0
```

The contract: if you depend on `^1.2.3` (npm) or `~>1.2` (bundler), you expect `1.2.4` and `1.3.0` to be safe updates. When the major version bumps, you read the changelog before upgrading.

## Tagging Releases with Git
<!-- bite: c5a4907a-6b92-4a0f-8cf9-aa176edae3ba -->

```bash
# Annotated tag for releases (recommended — stores tagger, date, message)
git tag -a v1.2.3 -m "Release 1.2.3

- Add user authentication
- Fix payment timeout issue
- Improve error messages"

# Sign a tag (if you've set up GPG)
git tag -s v1.2.3 -m "Release 1.2.3"

# Tag a specific commit (not HEAD)
git tag -a v1.2.3 a1b2c3d -m "Release 1.2.3"

# Push tags
git push origin v1.2.3      # push specific tag
git push origin --tags      # push all tags
git push --follow-tags      # push commits AND annotated tags

# List tags
git tag                     # all tags
git tag -l "v1.*"           # filter
git tag -n                  # with messages
git show v1.2.3             # show tag details and tagged commit

# Delete tags
git tag -d v1.2.3
git push origin --delete v1.2.3

# Checkout a tag (detached HEAD)
git checkout v1.2.3
git checkout -b hotfix/v1.2.4 v1.2.3   # branch from a tag
```

## Automating Versions from Conventional Commits
<!-- bite: 599e548a-2331-4fa8-93f1-23ae203ac41e -->

When all commits follow Conventional Commits format, tools can automatically determine the next version:

```
feat: add payment webhook          → 1.0.0 → 1.1.0  (MINOR bump)
fix: handle null in auth           → 1.1.0 → 1.1.1  (PATCH bump)
feat!: change auth token format    → 1.1.1 → 2.0.0  (MAJOR bump)
  BREAKING CHANGE: tokens are now JWT
docs: update readme                → no version change
chore: update deps                 → no version change
```

**Tools:**

```bash
# standard-version (standalone)
npx standard-version           # auto-bump version, generate CHANGELOG, create tag
npx standard-version --dry-run # preview what would happen
npx standard-version --release-as minor   # force a specific bump type

# semantic-release (automated, runs in CI)
# Configured in .releaserc or package.json
# Runs on CI, analyses commits, creates tags and GitHub releases automatically
```

**`package.json` with standard-version:**

```json
{
  "scripts": {
    "release": "standard-version",
    "release:minor": "standard-version --release-as minor",
    "release:major": "standard-version --release-as major",
    "release:patch": "standard-version --release-as patch"
  }
}
```

## CHANGELOG Generation
<!-- bite: a6c2a777-7557-46f3-ab3a-5842e5f2afbb -->

```bash
# standard-version automatically generates CHANGELOG.md on each release
# Organised by version, with sections for features, fixes, and breaking changes

# Example generated CHANGELOG.md:
# ## [1.2.0] - 2026-01-15
# ### Features
# - **auth:** add JWT refresh token rotation (#142)
# - **payments:** add Paystack webhook support (#138)
# ### Bug Fixes
# - **auth:** handle null user in middleware (#145)
# ### BREAKING CHANGES
# - **api:** response format for /users changed
```

## Version Badges and Release Notes
<!-- bite: 2975ca33-d939-4683-afa9-a61c80ff7551 -->

When you push an annotated tag, create a GitHub Release to add notes and attach binary assets:

```bash
# Via GitHub CLI
gh release create v1.2.3 \
  --title "Release 1.2.3" \
  --notes "## What's Changed
  - Add user authentication
  - Fix payment timeout
  
  **Full Changelog**: https://github.com/org/repo/compare/v1.2.2...v1.2.3"

# Attach build artifacts
gh release create v1.2.3 \
  --notes "Release notes" \
  ./dist/app-linux-x64 \
  ./dist/app-macos-arm64

# Auto-generate notes from PR titles and commit messages
gh release create v1.2.3 --generate-notes
```

---

## Related
<!-- bite: ad5a9d1d-44e3-47fb-ae90-63679bcf7bfd -->
- [[git/12-conventions-and-hygiene|Conventions and Hygiene]] — the commit types that drive an automated version bump
- [[git/14-github-and-ci|Git in CI]] — tagging and releasing from a pipeline
- [[git/15-the-github-cli|The GitHub CLI]] — `gh release create --generate-notes` in context
- [[git/17-hooks-and-signing|Hooks and Signing]] — signed tags
- [[git/index|Git course map]]

## About this lesson
<!-- bite: 0ff54d49-9196-4f68-a3c2-a73f1ed4451b -->

**Level:** Intermediate. **Covers:** Lightweight vs annotated tags, and the semantic versioning contract they encode — including automating versions and changelogs from conventional commits.
