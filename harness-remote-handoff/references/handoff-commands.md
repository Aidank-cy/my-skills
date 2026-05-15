# Handoff Commands Reference

Exact command sequences for every handoff scenario. Copy and
present the relevant block to the user at each boundary.

---

## Feature development cycle

### After agent local commit → user pushes and opens PR

```bash
# Push the feature branch
git push origin feat/{name}

# Open PR (edit the body as needed)
gh pr create \
  --title "{type}: {subject}" \
  --body "## Summary
{one-line description}

## Changelog
{paste entries from CHANGELOG.md [Unreleased]}

## Checklist
- [x] Tests pass
- [x] Lint clean
- [x] CHANGELOG updated
- [x] Rebased on main

Closes #{issue}"
```

### After PR merged → user cleans up

```bash
git checkout main
git pull origin main
git branch -d feat/{name}

# Optional: clean all merged branches
git branch --merged main | grep -v 'main' | xargs -r git branch -d
```

### After PR merged → user tells agent to start next task

The user can say any of:
- "Next task: {description}" — agent enters `prompt-gateway`
- "What's pending?" — agent runs context recovery
- Just describe the next feature — agent treats it as a new task

No explicit "I merged" confirmation is needed. The agent detects
the merge from `git log` when it reads project state.

---

## PR review iteration cycle

### Reviewer requests changes → user tells agent

```
User: "Review says to change the toggle to a dropdown with
       three options in src/components/ThemeToggle.tsx.
       After the change, all three options switch themes correctly."
```

This is a valid Tier B prompt (what + where + done-when).
The agent stays on the current branch and appends a commit.

### After agent fixes → user pushes update

```bash
git push origin feat/{name}
# PR updates automatically, re-request review
```

---

## Release cycle

### Agent commits release locally → user pushes

```bash
# Push commit and tag together
git push origin main --follow-tags
```

### User wants a GitHub Release page too

```bash
# Option 1: Notes from tag annotation
gh release create v{x.y.z} --notes-from-tag

# Option 2: Notes from CHANGELOG section (richer)
gh release create v{x.y.z} \
  --notes "$(sed -n '/## \[{x.y.z}\]/,/## \[/p' CHANGELOG.md | sed '1d;$d')"

# Option 3: Draft release for manual editing
gh release create v{x.y.z} --draft
```

### Verify release is complete

```bash
# Confirm tag exists on remote
git ls-remote --tags origin | grep v{x.y.z}

# Confirm version file matches
cat package.json | grep '"version"'
# or: cat pyproject.toml | grep 'version'
# or: cat Cargo.toml | grep 'version'
```

---

## Hotfix cycle

### Agent commits hotfix → user pushes and fast-tracks PR

```bash
git push origin fix/{name}

gh pr create \
  --title "fix: {subject}" \
  --body "## Hotfix
{description}

Closes #{issue}" \
  --label "hotfix"
```

### After hotfix merged → immediate patch release

User tells agent:
```
"发版" / "release a patch" / "ship the hotfix"
```

Agent runs `versioning-and-changelog` Flow 2, which detects only
`Fixed` entries and produces a PATCH bump.

---

## CI failure recovery

### User reports CI failure → agent fixes

User provides:
```
"CI failed: test-e2e, error: TypeError Cannot read property
'theme' of undefined at tests/e2e/settings.spec.ts:42.
Fix so test-e2e passes."
```

Agent treats as Tier B:
- **What**: CI test-e2e failure, TypeError
- **Where**: tests/e2e/settings.spec.ts:42
- **Done-when**: test-e2e passes

After fix, agent commits and returns push command.

### User pushes CI fix

```bash
git push origin feat/{name}
# CI re-runs automatically on PR
```

---

## Context recovery commands

### Agent-side recovery (run silently on session start)

```bash
# Current branch
git branch --show-current

# Recent commits
git log --oneline -10

# Uncommitted changes
git status --short

# Recent tags
git tag --sort=-v:refname | head -3

# Remote tracking status
git rev-list --left-right --count HEAD...origin/$(git branch --show-current) 2>/dev/null

# Read harness state
cat .harness/progress.md 2>/dev/null | tail -20
head -30 CHANGELOG.md 2>/dev/null
```

### User-side recovery (when the user wants to check state manually)

```bash
# What branch am I on?
git branch --show-current

# Any uncommitted work?
git status

# What's the latest version?
git describe --tags --abbrev=0

# What's unreleased?
sed -n '/## \[Unreleased\]/,/## \[/p' CHANGELOG.md | head -20

# Am I behind remote?
git fetch origin && git status
```

---

## Multi-project context switch

When the user works on multiple harness-managed projects and
switches between them, the agent should:

1. Detect the project change from the working directory or user statement.
2. Run full context recovery for the new project.
3. Not carry over state assumptions from the previous project.

User says:
```
"Switch to project-B" / "Now working on my-api"
```

Agent runs recovery procedure against the new project's
`.harness/progress.md`, `CHANGELOG.md`, `AGENTS.md`, and git state.

---

## Sync-filter integration

When the project uses dev→public sync, remind the user after
operations that touch the sync boundary:

### After adding new harness files

```
Note: {file} is classified as PRIVATE.
Verify sync-public.yml includes: rm -rf {file}
```

### After release push

```
The sync workflow will run on push. Verify:
  - Public repo does not contain harness files
  - Public repo has the latest app source
```
