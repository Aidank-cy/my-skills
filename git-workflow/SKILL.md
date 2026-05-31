---
name: git-workflow
description: >
  This skill should be used when the user asks to "commit code",
  "create a branch", "merge a feature", "push changes", "release",
  "git operations", "commit code", "create branch", "switch branch", "merge branch",
  "next feature", or needs guidance on branch naming, commit
  conventions, merge strategy, or the task-based branch lifecycle.
  Also trigger when the agent is about to start a new task and needs
  to verify branch state, or when a task is complete and ready for
  merge. Governs the git operation norms that connect prompt-gateway
  (task pipeline) and versioning-and-changelog (release pipeline)
  into a unified development flow. Do not use for non-git questions
  or general coding tasks.
---

# Git Workflow

Standardize every git operation in a harness-managed project.
One task = one branch. Every branch merges back to main when done.

## Core rules

- One task per branch. One logical change per commit.
- Never commit directly to `main`.
- Always pass through `prompt-gateway` before committing code changes.
- Always update `CHANGELOG.md` before committing.
- Merge to main at the end of every task. Do not leave branches open.

## Task-based branch lifecycle

Every task follows this cycle:

```
main ──→ checkout -b {type}/{name} ──→ subtasks ──→ commit ──→ merge ──→ main
```

### 1. Open branch

Run the pre-task state gate, then create the branch:

```bash
# 1. Ensure on main and up to date
git checkout main
git pull origin main

# 2. Verify clean state
git status --short           # expect clean
git branch                   # no stale feature branches

# 3. Create task branch
git checkout -b {type}/{short-description}
```

### 2. Work on branch

Execute subtasks through `prompt-gateway` Steps 3–5.
Each subtask is verified before moving to the next.

### 3. Commit

After all subtasks pass verification:

```bash
git add -A
git commit -m "{type}({scope}): {description}"
```

If the task has multiple independent logical changes, create one
commit per change. Each commit independently passes lint, typecheck,
and tests.

### 4. Merge to main and clean up

```bash
git checkout main
git merge {feature-branch} --no-ff
git branch -d {feature-branch}

# Verify
git status --short           # expect clean
git log --oneline -3         # confirm merge commit
```

After merge, the project is on main and ready for the next task.

## Pre-task state gate

Run this check **before** starting each task. No exceptions.

```
□ Am I on main?
  → NO: a previous task branch is still active.
    Complete or abort it first (see Stale branch recovery).
  → YES: continue.
□ Is main up to date?
  → Run: git log --oneline -1
  → Confirm latest commit is expected.
  → If not: git pull origin main
□ Working tree clean?
  → Run: git status --short
  → If dirty: stash or discard before branching.
```

Only after all three checks pass, create the new branch.

## Branch naming

```
{type}/{short-description}
```

| Type | When |
|---|---|
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
- Always branch from `main`.

## Commit conventions

Follow Conventional Commits.

### Format

```
{type}[!][(scope)]: {subject}

[body]

[footer]
```

### Subject line rules

- Imperative mood: "Add feature", not "Added feature".
- Max 72 characters.
- No trailing period.
- Lowercase after colon: `feat: add dark mode toggle`.

### Type-to-category mapping

| Commit type | Changelog category | Version bump |
|---|---|---|
| `feat` | Added | MINOR |
| `fix` | Fixed | PATCH |
| `refactor` | Changed | PATCH |
| `docs` | Changed | PATCH |
| `test` | Changed | PATCH |
| `chore` | Changed | PATCH |
| `feat!:` / `fix!:` | depends | MAJOR |

### What to commit together

Bundle into one commit:
- Code change + its test update + CHANGELOG entry
- AGENTS.md rule update triggered by the same change

Separate into distinct commits:
- Different logical changes within the same task

## Merge strategy

| Scenario | Method |
|---|---|
| Task branch, single commit | Squash merge or `--no-ff` merge |
| Task branch, multiple meaningful commits | `--no-ff` merge (preserve history) |
| Release branch | Regular merge commit |
| Hotfix | Squash merge |

Default for the task lifecycle: `git merge --no-ff` to preserve
the branch history as a single merge commit on main.

## Sequential task workflow

When processing multiple tasks in one session:

```
Task 1: main → branch → subtasks → commit → merge → main
Task 2: main → branch → subtasks → commit → merge → main
Task 3: main → branch → subtasks → commit → merge → main
```

Each task is fully isolated. Never carry uncommitted work from
one task into the next. Run the pre-task state gate between
every task.

### Decision table

| Current state | Action |
|---|---|
| On main, clean | Create new branch → start task |
| On main, dirty working tree | Stash or discard → then create branch |
| On task branch, work uncommitted | Commit or stash → merge to main → new branch |
| On task branch, work committed | Merge to main → delete branch → new branch |
| On wrong branch (drift) | Abort. Return to main. Resolve stale branch. |

## Stale branch recovery

If a previous task branch was left open:

```bash
# Option A: Previous work is complete
git checkout main
git merge {stale-branch} --no-ff
git branch -d {stale-branch}

# Option B: Previous work is incomplete and should be discarded
git checkout main
git branch -D {stale-branch}

# Option C: Previous work is incomplete but should be preserved
git stash                    # if uncommitted changes exist
git checkout main
# Decide: finish later or discard
```

## Release workflow

Delegate version decisions to `versioning-and-changelog`.

### Simple release

```bash
# 1. On main, run versioning-and-changelog Flow 2
# 2. Commit
git add -A
git commit -m "chore(release): bump to v{X.Y.Z}"
# 3. Tag
git tag -a v{X.Y.Z} -m "Release v{X.Y.Z}"
# 4. Push
git push origin main --follow-tags
```

### Complex release

Use a release branch only when stabilization is needed:

```bash
git checkout -b release/v{X.Y.Z}
# Finalize → versioning-and-changelog Flow 2
git checkout main
git merge release/v{X.Y.Z}
git tag -a v{X.Y.Z} -m "Release v{X.Y.Z}"
git push origin main --follow-tags
git branch -d release/v{X.Y.Z}
```

## Integration points

| Skill | Relationship |
|---|---|
| `prompt-gateway` | Owns task pipeline. Triggers branch creation (Step 0) and merge (Step 6E). This skill defines the mechanics. |
| `versioning-and-changelog` | Owns version decisions and CHANGELOG format. This skill owns git mechanics around releases. |
| `sync-filter` | Harness files are PRIVATE per sync-filter rules. |
| `harness-remote-handoff` | Manages handoff after release commands. |

## Anti-rationalization

Reject these shortcuts:
- Committing directly to main "because it's a small fix"
- Leaving task branches open after completion
- Skipping the pre-task state gate
- Skipping rebase "because there are no conflicts"
- Pushing without verifying lint and tests pass
- Creating a PR without a CHANGELOG entry
- Adding task B commits to task A's branch
- Deferring merge-to-main "to batch tasks together"
- Keeping rules that have never been triggered by a real failure
- Treating skill file count or word count as a quality signal

## References

| When needed | Read |
|---|---|
| Branch naming examples, PR template, merge policy, rebase workflow | `references/branching-and-pr.md` |
