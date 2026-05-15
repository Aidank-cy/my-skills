---
name: versioning-and-changelog
description: >
  This skill should be used when the user asks to update a changelog,
  bump a version, cut a release, tag a release, ship code, or says
  things like "release", "bump version", "tag", "发版",
  "更新版本", or "ship it". Trigger automatically after a code
  modification task completes so CHANGELOG.md is updated under
  [Unreleased] before commit. Manage SemVer decisions, release
  sections, version-file updates, tagging, and release handoff.
---

# Versioning And Changelog

Manage the ship phase.
Record meaningful changes, decide the correct version, and close the release path cleanly.

## Core rules

- Update `CHANGELOG.md` after every code-modification task.
- Keep unreleased work under `## [Unreleased]` until a release is cut.
- Use Semantic Versioning.
- Use `v`-prefixed git tags.
- Never modify an existing released version; ship a new version instead.

Read `references/semver-rules.md` before making the first version decision in a session.

## Categories

Use only these Keep a Changelog categories:
- `Added`
- `Changed`
- `Deprecated`
- `Removed`
- `Fixed`
- `Security`

## Version rules

Apply this bump table:

| Change type | Bump |
|-------------|------|
| Breaking change | MAJOR |
| Backward-compatible feature | MINOR |
| Backward-compatible fix or maintenance | PATCH |

Apply the pre-1.0 rule:
- before `1.0.0`, use `0.MINOR.PATCH`
- a new feature still bumps MINOR
- a fix-only release still bumps PATCH

Use commit intent as the default signal:

| Commit prefix | Default meaning | Default changelog category |
|---------------|-----------------|----------------------------|
| `feat:` | new functionality | `Added` |
| `fix:` | bug fix | `Fixed` |
| `refactor:` | internal restructure | `Changed` |
| `docs:` | documentation change | `Changed` |
| `test:` | test-only change | `Changed` |
| `chore:` | maintenance or tooling | `Changed` |
| `feat!:` / `fix!:` / `BREAKING CHANGE:` | breaking change | depends on actual change |

## Flow 1: Update unreleased changes

Run this flow automatically after every code-modification task.

### Required steps

1. Review the files changed in the task.
2. Group meaningful user-visible changes by changelog category.
3. Write one human-readable line per logical change.
4. Insert the entries under `## [Unreleased]` in `CHANGELOG.md`.
5. Commit the code changes and the changelog update together.

### Exceptions

Skip the automatic changelog update only when the task changes:
- `CHANGELOG.md` only
- AI tooling or rules files only, with no product or code change

### Entry rules

Write entries that:
- start with a verb
- describe the outcome, not the file edit
- use one line per logical change
- include issue or PR numbers when available

## Flow 2: Cut a release

Run this flow when the user explicitly asks to release or bump a version.

### Step 1: Review unreleased changes

Inspect `## [Unreleased]`.
If it is empty, reconstruct pending release context from local git history.

### Step 2: Determine the bump

Apply these rules:
- any breaking change or `Removed` entry forces MAJOR
- any `Added` entry forces at least MINOR
- only `Fixed`, `Changed`, docs, refactor, or maintenance changes produce PATCH

Present the proposed version before finalizing the release.
Include:
- current version
- unreleased change summary
- proposed bump type
- proposed next version

### Step 3: Move unreleased entries into a release section

Create a versioned section in this form:
- `## [x.y.z] - YYYY-MM-DD`

Leave an empty `## [Unreleased]` section at the top.

### Step 4: Update version files

Update the version in the project's real package or build files.
Examples include:
- `package.json`
- `pyproject.toml`
- `Cargo.toml`

If multiple ecosystem version files exist, keep them aligned.

### Step 5: Commit, tag, and optionally release

For the local release path:
- stage the version and changelog changes
- create a release commit: `chore(release): bump to v{x.y.z}`
- create an annotated `v` tag: `git tag -a v{x.y.z} -m "Release v{x.y.z}"`

For remote operations:
- push, PR creation, and hosted release publication remain user-owned unless the user explicitly asks for them
- defer push and merge mechanics to `git-workflow`

## Release checklist

Confirm all of the following before calling a release complete:
- `CHANGELOG.md` reflects the final release content
- the version file matches the release version
- the git tag matches the release version with a `v` prefix
- `## [Unreleased]` remains present for the next cycle

## Integration points

### With code-modification skills

Expect code-modification workflows such as `prompt-gateway` to hand off here at the end of implementation.
Own the changelog format and insertion rules.

### With harness-init

Create an initial `CHANGELOG.md` during project bootstrap.
Seed it with:
- `## [Unreleased]`
- the first version section
- an initial `Added` entry for the scaffold

### With release workflows

Take over when the user says `release`, `bump version`, `tag`, `发版`, or equivalent.
Compute the bump from real unreleased work, not from guesswork.

### With `git-workflow`

Own version and CHANGELOG decisions. Defer git mechanics (branch
management, tagging format, push strategy, merge policy) to
`git-workflow`. The two skills share the commit-type-to-category
mapping table — keep them aligned.

## Anti-rationalization

Reject these shortcuts:
- deferring the changelog update until later
- skipping a changelog entry because the change is "small"
- defaulting to PATCH when `Added` exists
- cutting a release without a tag
- bumping a version without reviewing unreleased changes
- leaving version files and tags out of sync

## References

| When needed | Read |
|-------------|------|
| Need full SemVer rules, edge cases, tag format, or release examples | `references/semver-rules.md` |
