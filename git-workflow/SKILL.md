---
name: git-workflow
description: >
  This skill should be used when the user asks to "commit code",
  "create a branch", "open a PR", "merge a feature", "push changes",
  "release", "git操作", "提交代码", "创建分支", "切换分支",
  "下一个功能", or needs guidance on branch naming, commit conventions,
  merge strategy, multi-feature branch isolation, or the full git
  lifecycle for a harness-managed project. Also trigger when the agent
  is about to start a second feature in the same session and needs to
  verify branch state before proceeding. Governs the git operation
  norms that connect prompt-gateway (execution pipeline) and
  versioning-and-changelog (release pipeline) into a unified
  development flow. Do not use for non-git questions or general
  coding tasks.
---

# Git Workflow

Standardize every git operation in a harness-managed project.
Bridge the gap between `prompt-gateway` (code modification) and
`versioning-and-changelog` (release) with consistent branch, commit,
PR, and merge conventions.

## Core rules

- One feature per branch. One logical change per commit.
- Never commit directly to `main`.
- Always pass through `prompt-gateway` before committing code changes.
- Always update `CHANGELOG.md` before committing (enforced by `prompt-gateway` Step 6A).
- Keep remote operations user-owned unless explicitly requested.

## Branch model

Use a trunk-based model with short-lived feature branches.

```
main (protected, always releasable)
 ├── feat/add-dark-mode
 ├── fix/auth-redirect-loop
 ├── chore/update-deps
 └── release/v1.3.0       (only for multi-step releases)
```

### Branch naming

```
{type}/{short-description}
```

| Type | When |
|------|------|
| `feat` | New functionality |
| `fix` | Bug fix |
| `refactor` | Internal restructure, no behavior change |
| `docs` | Documentation only |
| `chore` | Tooling, config, dependency updates |
| `test` | Test-only changes |
| `release` | Multi-step release preparation |

Rules:
- Lowercase, hyphens only (no underscores, no camelCase).
- Max 50 characters total.
- Include issue number when available: `fix/42-auth-redirect`.
- Branch from `main` unless working on a stacked change.

### Branch lifecycle

```
1. Create branch from main
2. Develop (prompt-gateway pipeline per change)
3. Local commit (prompt-gateway Step 6D)
4. Push branch
5. Open PR
6. Review and merge to main
7. Delete branch after merge
```

## Sequential multi-feature workflow

When a session involves modifying multiple features or skills in
sequence, enforce strict branch isolation. Each feature gets its own
branch; never stack unrelated changes onto an existing feature branch.

### Pre-feature state gate

Run this check **before** starting each feature in a multi-feature
session. No exceptions, even if the next change feels trivial.

```
□ Am I on main?
  → NO: a previous feature branch is still active.
    Stop. Complete or abort it first (see Close-and-switch below).
  → YES: continue.
□ Is main up to date with the previous feature's merge?
  → Run: git log --oneline -1
  → Confirm the latest commit is the merge of the previous feature
    branch (or the initial state if this is the first feature).
  → If not, run: git pull origin main
□ Working tree clean?
  → Run: git status --short
  → If dirty, stash or discard before branching.
```

Only after all three boxes are checked, create the new feature branch:

```bash
git checkout -b {type}/{short-description}
```

### Close-and-switch protocol

After completing a feature (all commits done, checks passed), close
the branch before starting the next feature:

```bash
# 1. Final commit on the feature branch (prompt-gateway Step 6D)
git add -A
git commit -m "{type}({scope}): {description}"

# 2. Switch to main and merge
git checkout main
git merge {feature-branch} --no-ff   # or squash, per merge strategy
# For local-only workflow without PR:
#   git merge --squash {feature-branch} && git commit

# 3. Delete the completed branch
git branch -d {type}/{short-description}

# 4. Verify clean state
git status --short   # expect clean
git log --oneline -3 # confirm merge commit

# 5. Now safe to create the next feature branch
```

### Decision table

| Current state | Action |
|---------------|--------|
| On main, clean, previous merge confirmed | Create new branch → start work |
| On main, dirty working tree | Stash or discard → then create branch |
| On feature branch, work uncommitted | Commit or stash → merge to main → new branch |
| On feature branch, work committed but not merged | Merge to main → delete branch → new branch |
| On wrong feature branch (drift detected) | Abort. Stash changes. Return to main. Merge or discard the stale branch. Restart. |

### Anti-drift signals

Watch for these signs that branch isolation has broken:

- `git log --oneline` shows commits for feature B on a branch named
  for feature A.
- `git diff main --stat` shows files unrelated to the current branch
  name.
- The branch has been alive for more than one feature request.

If any signal fires, stop immediately. Do not add more commits.
Return to main via the close-and-switch protocol.

## Commit conventions

Follow Conventional Commits. Match the commit type to the changelog
category assigned by `versioning-and-changelog`.

### Format

```
{type}[!][(scope)]: {subject}

[body]

[footer]
```

### Subject line rules

- Imperative mood: "Add feature", not "Added feature" or "Adds feature".
- Max 72 characters.
- No trailing period.
- Start with lowercase after the colon: `feat: add dark mode toggle`.

### Type-to-category mapping

| Commit type | Changelog category | Version bump |
|-------------|-------------------|--------------|
| `feat` | Added | MINOR |
| `fix` | Fixed | PATCH |
| `refactor` | Changed | PATCH |
| `docs` | Changed | PATCH |
| `test` | Changed | PATCH |
| `chore` | Changed | PATCH |
| `feat!:` / `fix!:` | depends | MAJOR |

### Body and footer

Include a body when the subject alone does not explain the change.
Use the footer for:
- `Closes #42` or `Fixes #42` to link issues.
- `BREAKING CHANGE: description` for breaking changes.

### What to commit together

Bundle related changes into one atomic commit:
- Code change + its test update + CHANGELOG entry = one commit.
- AGENTS.md rule update triggered by the change = same commit.

Separate into distinct commits:
- Different logical changes within the same user request.
  One branch, one commit per logic point — not one branch per logic point.
- Unrelated work that belongs to different user requests = separate branches.

## Development lifecycle

### Starting a feature

Before writing any code, run the pre-feature state gate
(see "Sequential multi-feature workflow" above).

```
□ Am I on main? → git checkout main && git pull origin main
□ Is main clean and up to date? → git status --short (expect empty)
□ If this is part of a multi-feature session, was the previous
  feature branch merged and deleted? → git branch (no stale branches)
□ Did I create a feature branch? → git checkout -b {type}/{name}
□ Never skip branch creation. Committing to main is a workflow violation.
```

```bash
# 1. Ensure main is current
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feat/add-dark-mode

# 3. Begin work through prompt-gateway pipeline
```

### During development

Follow `prompt-gateway` for each modification:
1. Validate the prompt (Tier A or Tier B).
2. Check harness integrity.
3. Execute and verify.
4. Finalize: CHANGELOG → rules → progress → local commit.

After each commit, check:

```
□ git log --oneline on this branch — does each commit
  represent exactly one logical change?
□ Does each commit pass lint, typecheck, and tests independently?
□ Are there more logic points in the original request?
  → YES: start the next cycle from Step 5.
  → NO: proceed to preparing for PR.
```

Multiple commits on one branch are fine for complex features.
Each commit must independently pass lint, typecheck, and tests.

### Preparing for PR

Before pushing:

```bash
# Rebase on latest main to avoid merge conflicts
git fetch origin
git rebase origin/main

# Verify all checks pass
# (lint, typecheck, tests — per AGENTS.md commands)

# Push
git push origin feat/add-dark-mode
```

Use rebase, not merge, to keep history linear.
If the branch has messy intermediate commits, squash before pushing:

```bash
git rebase -i origin/main
# Mark intermediate commits as 'squash' or 'fixup'
```

### Opening a PR

Include in the PR description:
- Summary of what changed and why.
- Link to the issue or spec.
- Changelog entries added (copy from CHANGELOG.md).
- Checklist: tests pass, lint clean, CHANGELOG updated.

```bash
gh pr create \
  --title "feat: add dark mode toggle" \
  --body "## Summary
Add dark mode toggle to settings page.

## Changelog
### Added
- Add dark mode toggle with system preference fallback

## Checklist
- [x] Tests pass
- [x] Lint clean
- [x] CHANGELOG updated
- [x] Rebased on main

Closes #14"
```

### Merging

Before merging, check the branch commit count:

```
□ Run: git log --oneline origin/main..HEAD
□ Count meaningful commits (exclude WIP/fixup).
□ 1 commit → squash merge.
□ 2+ meaningful commits → rebase and merge.
□ Release branch → regular merge.
```

Choose the merge method based on the branch content:

- **Single logical change on a feature branch** → squash merge (one clean commit on main).
- **Multiple meaningful commits on a feature branch** → rebase and merge (preserve individual commit history on main).
- **Release branch** → regular merge commit (preserve release history).
- **Hotfix** → squash merge.

Delete the branch after merge.

```bash
# After PR is approved and merged via GitHub
git checkout main
git pull origin main
git branch -d feat/add-dark-mode
```

## Release workflow

Delegate version decisions to `versioning-and-changelog`.
This skill owns the git mechanics around a release.

### Simple release (most cases)

```bash
# 1. On main, run versioning-and-changelog Flow 2
#    (determines bump, updates CHANGELOG, updates version files)

# 2. Commit the release
git add -A
git commit -m "chore(release): bump to v1.3.0"

# 3. Tag
git tag -a v1.3.0 -m "Release v1.3.0"

# 4. Push
git push origin main --follow-tags
```

### Complex release (multi-step preparation)

Use a release branch only when stabilization is needed:

```bash
git checkout -b release/v2.0.0
# Cherry-pick or finalize changes
# Run versioning-and-changelog Flow 2
git checkout main
git merge release/v2.0.0
git tag -a v2.0.0 -m "Release v2.0.0"
git push origin main --follow-tags
git branch -d release/v2.0.0
```

## Hotfix workflow

```bash
# 1. Branch from main
git checkout -b fix/critical-auth-bypass

# 2. Fix through prompt-gateway pipeline
# 3. PR, review, merge to main
# 4. Immediately run versioning-and-changelog Flow 2 for a PATCH release
```

## Integration points

### With prompt-gateway

`prompt-gateway` owns the execution pipeline and produces local commits
(Step 6D). This skill standardizes the branch and commit conventions
that `prompt-gateway` follows. The two skills share the same
Conventional Commits format.

### With versioning-and-changelog

`versioning-and-changelog` owns version decisions and CHANGELOG format.
This skill owns the git mechanics (tagging, pushing, branch management)
around releases. Defer all bump-level decisions to
`versioning-and-changelog`.

### With sync-filter

When the project uses a dev→public sync pipeline, classify all
harness files as PRIVATE per `sync-filter` rules. Git workflow
artifacts (branch conventions, PR templates) are internal process
and should not sync to the public repo.

### With `harness-remote-handoff`

After the release git commands are returned to the user,
`harness-remote-handoff` manages the handoff protocol and
context recovery for the next session.

## Anti-rationalization

Reject these shortcuts:
- Committing directly to main "because it's a small fix".
- Skipping rebase "because there are no conflicts yet".
- Leaving dead feature branches after merge.
- Pushing without verifying lint and tests pass locally.
- Creating a PR without a CHANGELOG entry.
- Using merge commits on feature branches instead of rebase.
- Tagging a release without running `versioning-and-changelog` Flow 2.
- Adding feature B commits to feature A's branch "because it's faster".
- Skipping the pre-feature state gate "because I know main is clean".
- Deferring the merge-to-main step "to batch multiple features together".

## References

| When needed | Read |
|-------------|------|
| Need detailed branching strategy, PR template, or merge policy | `references/branching-and-pr.md` |
