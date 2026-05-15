# Semantic Versioning — Full Rules & Edge Cases

Reference for version number decisions. Read this when you're unsure how to bump.

---

## The rules (semver.org summary)

1. Version format: `MAJOR.MINOR.PATCH` (e.g. `2.5.3`)
2. Once released, the contents of that version MUST NOT be modified. Any fix = new version.
3. MAJOR version zero (0.y.z) is for initial development. Anything may change at any time.
4. Version 1.0.0 defines the public API. After that, version bumps follow the rules below.
5. PATCH — backward-compatible bug fixes only.
6. MINOR — new backward-compatible functionality. PATCH resets to 0.
7. MAJOR — any backward-incompatible change. MINOR and PATCH reset to 0.
8. Pre-release versions: append hyphen + identifiers (e.g. `1.0.0-alpha.1`, `1.0.0-beta.2`, `1.0.0-rc.1`).
9. Build metadata: append plus + identifiers (e.g. `1.0.0+build.123`). Ignored for precedence.

## Git tag format

Always use the `v` prefix: `v1.2.3`, not `1.2.3`. This is the dominant convention in the ecosystem (GitHub, npm, cargo, Go modules all use or expect `v` prefix).

```bash
# Correct
git tag -a v1.2.3 -m "Release v1.2.3"

# Wrong
git tag -a 1.2.3 -m "Release 1.2.3"
```

## When to release v1.0.0

Release v1.0.0 when ANY of these are true:
- The project is used in production
- Other projects depend on it
- You've documented a public API
- The user explicitly says "this is stable"

Stay on v0.x.x when:
- The project is a prototype or experiment
- The API is still changing frequently
- No one depends on it yet

## Pre-release versions

Use for testing before a stable release:

```
v1.3.0-alpha.1   → first alpha (internal testing)
v1.3.0-alpha.2   → second alpha
v1.3.0-beta.1    → beta (wider testing)
v1.3.0-rc.1      → release candidate (feature-complete, final testing)
v1.3.0            → stable release
```

Precedence: `alpha < beta < rc < stable`

Only use pre-releases when the user explicitly asks. For most projects, just release stable versions.

---

## Edge cases and common questions

### "I added a feature AND fixed a bug"
Highest bump wins → MINOR (feature > bugfix).

### "I refactored internals but the public behavior didn't change"
PATCH. Internal changes are not features.

### "I changed the default value of a config option"
If existing users' behavior changes without them doing anything → MAJOR (breaking).
If it's a new option with a backward-compatible default → MINOR.

### "I deprecated a function but didn't remove it"
MINOR. Deprecation is a notice, not a break. Removal is MAJOR.

### "I updated a dependency"
- If the update doesn't change your project's behavior → PATCH.
- If the update adds new capabilities you expose → MINOR.
- If the update breaks your public API → MAJOR.

### "I only changed documentation"
PATCH. But if it's the only change since the last release, consider whether a release is even needed.

### "I changed the build tooling but not the output"
PATCH or no release. Build tooling isn't part of the public API.

### "I accidentally released a broken version"
Release a new PATCH immediately with the fix. Never delete or modify an existing tag.
If it's critical, yank the release (npm unpublish, crates.io yank) but still keep the version number used.

### "I'm not sure if this is a breaking change"
Ask the user. When in doubt, it's MAJOR. Being conservative with MAJOR is better than breaking someone's code with a MINOR bump.

---

## Version in different ecosystems

### Node.js (package.json)
```json
{
  "version": "1.3.0"
}
```
Update with: `npm version minor --no-git-tag-version` (or `major` / `patch`)

### Python (pyproject.toml)
```toml
[project]
version = "1.3.0"
```
Or use dynamic versioning with `setuptools-scm` (reads from git tags).

### Rust (Cargo.toml)
```toml
[package]
version = "1.3.0"
```
Update with: `cargo set-version 1.3.0` (requires `cargo-edit`)

### Go
Go modules use the git tag directly. No version file to update.
For v2+, the module path changes: `github.com/user/repo/v2`

---

## CHANGELOG.md format reference

### Full template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

## [1.3.0] - 2026-05-13

### Added
- User profile page with avatar upload (#12)
- Dark mode toggle in settings (#14)

### Changed
- Improved error messages for auth failures (#13)

### Fixed
- Login redirect loop on expired sessions (#15)

## [1.2.1] - 2026-05-01

### Fixed
- Memory leak in WebSocket handler (#11)

### Security
- Updated jwt library to patch CVE-2026-XXXX

## [1.2.0] - 2026-04-15

### Added
- JWT authentication for API endpoints (#8)
- Rate limiting middleware (#9)

### Changed
- Migrated session storage from cookies to Redis (#10)

### Deprecated
- Cookie-based session auth (will be removed in v2.0.0)

## [1.1.0] - 2026-03-20
...
```

### Entry writing rules

- One line per change, starting with a verb (Added, Fixed, Changed...)
- Include issue/PR number if available: `(#12)` or `(GH-12)`
- Write for humans, not for git log readers
- Be specific: "Fixed login redirect loop" not "Fixed bug"
- Group related changes under the same category

### Link references (optional, at bottom of file)

```markdown
[Unreleased]: https://github.com/user/repo/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/user/repo/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/user/repo/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/user/repo/releases/tag/v1.2.0
```

---

## Automation helpers

### Extract version from git tags
```bash
# Latest tag
git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0"

# Strip the 'v' prefix for package files
VERSION=$(git describe --tags --abbrev=0 | sed 's/^v//')
```

### Compute next version from conventional commits
```bash
CURRENT=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
COMMITS=$(git log ${CURRENT}..HEAD --oneline --no-merges)

if echo "$COMMITS" | grep -qE '^[a-f0-9]+ (feat|fix|refactor|docs|test|chore)!:|BREAKING CHANGE'; then
  BUMP="major"
elif echo "$COMMITS" | grep -qE '^[a-f0-9]+ feat'; then
  BUMP="minor"
else
  BUMP="patch"
fi

echo "Current: $CURRENT | Bump: $BUMP"
```

### Extract changelog section for a release
```bash
# Get the changelog text for a specific version
VERSION="1.3.0"
sed -n "/## \[${VERSION}\]/,/## \[/p" CHANGELOG.md | sed '1d;$d'
```
