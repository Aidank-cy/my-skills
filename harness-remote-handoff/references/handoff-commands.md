# Handoff Commands Reference

Exact command sequences for every handoff scenario. Copy and
present the relevant block to the user at each boundary.

---

## Task completion cycle (default — auto-merge)

### After task merged to main → user verifies and syncs

```bash
# 1. Review what changed
git diff HEAD~1

# 2. Confirm build passes (adapt to project toolchain)
npm run build            # Node.js / Next.js
# cargo build            # Rust
# python -m pytest       # Python
# go build ./...         # Go

# 3. Visually inspect (adapt to what changed)
npm run dev              # start dev server → check localhost:3000
# open src/path/to/file  # open changed file directly
# curl localhost:8080/api # test API endpoint

# 4. Push all merged work to remote
git push origin main
```

The agent must replace the example commands above with the project's
actual commands. Every command must be runnable as-is.

That's it. The feature branch was already merged and deleted
locally by prompt-gateway Step 6E.

### After multiple tasks → user syncs remote

If the user completed several tasks before pushing:

```bash
# All merged commits go up in one push
git push origin main

# Verify
git log --oneline origin/main..main
# Should show 0 (local and remote are even)
```

### After task → user starts next task

The user can say any of:
- "Next task: {description}" — agent enters `prompt-gateway`
- "What's pending?" — agent runs context recovery
- Just describe the next change — agent treats it as a new task

No explicit confirmation is needed between tasks. The agent
verifies main is clean via the pre-task state gate.

---

## Task completion cycle (alternative — PR workflow)

Use this path only when the user explicitly requests code review
before remote merge.

### Agent commits on feature branch → user pushes and opens PR

```bash
# Push the feature branch
git push origin {type}/{name}

# Open PR
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
git branch -d {type}/{name}

# Optional: clean all merged branches
git branch --merged main | grep -v 'main' | xargs -r git branch -d
```

### PR review iteration → reviewer requests changes

User tells agent:

```
"Review says to change the toggle to a dropdown with
 three options in src/components/ThemeToggle.tsx.
 After the change, all three options switch themes correctly."
```

This is a valid Tier B prompt (what + where + done-when).
The agent stays on the current branch and appends a commit.

After fix:

```bash
git push origin {type}/{name}
# PR updates automatically, re-request review
```

---

## Release cycle

### Agent commits release locally → user pushes

```bash
# Push commit and tag together
git push origin main --follow-tags
```

### User wants a GitHub Release page

```bash
# Option 1: Notes from tag annotation
gh release create v{x.y.z} --notes-from-tag

# Option 2: Notes from CHANGELOG section
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

### Agent merges hotfix to main → user verifies and pushes

```bash
# 1. Review the fix
git diff HEAD~1

# 2. Confirm build passes
npm run build            # adapt to project toolchain

# 3. Confirm the fix works
npm run dev              # inspect visually, or:
# npm test               # run relevant tests

# 4. Push
git push origin main
```

### Immediate patch release after hotfix

User tells agent:

```
"release a patch" / "ship the hotfix" / "cut a release"
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

Agent creates a fix task: branch → fix → commit → merge to main.

### User pushes the fix

```bash
git push origin main
# CI re-runs on remote
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

# Local vs remote status
git fetch origin 2>/dev/null
git rev-list --left-right --count HEAD...origin/main 2>/dev/null

# Read harness state
tail -20 .harness/progress.md 2>/dev/null
head -30 CHANGELOG.md 2>/dev/null
```

### User-side recovery (manual state check)

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

## Interrupted session recovery

### Feature branch left open from previous session

```bash
# Option A: Work is complete — merge it
git checkout main
git merge {branch} --no-ff
git branch -d {branch}

# Option B: Work is incomplete — resume
git checkout {branch}
# Continue through prompt-gateway pipeline

# Option C: Work is abandoned — discard
git checkout main
git branch -D {branch}
```

---

## Multi-project context switch

When the user switches between harness-managed projects:

User says:
```
"Switch to project-B" / "Now working on my-api"
```

Agent runs recovery procedure against the new project's
`.harness/progress.md`, `CHANGELOG.md`, `AGENTS.md`, and git state.
Do not carry over state assumptions from the previous project.

---

## Sync-filter integration

### After pushing main (with dev→public sync)

```
The sync workflow will run on push. Verify:
  - Public repo does not contain harness files
  - Public repo has the latest app source
```

### After adding new harness files

```
Note: {file} is classified as PRIVATE.
Verify sync-public.yml includes: rm -rf {file}
```
