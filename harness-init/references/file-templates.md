# Harness Init — File Templates

This file contains all templates for generating harness engineering files in a new project. The SKILL.md references this file during Step 2 (Generate). Read this file before generating any project files.

---

## AGENTS.md template

```markdown
# AGENTS.md

## Project overview
{project-name}: {1-sentence description}. Built with {language} + {framework}. Uses {package-manager} for dependencies, {test-framework} for testing.

## Commands
- Install: `{real install command}`
- Dev: `{real dev command}`
- Test: `{real test command}`
- Lint: `{real lint command}`
- Typecheck: `{real typecheck command if applicable}`
- Build: `{real build command}`
- Post-task verify: `./hooks/post-task-verify.sh`

## Always
- Run `{lint}` and `{typecheck}` after every file edit. Fix failures before proceeding.
- Write tests for new functionality. Run the full suite before declaring done.
- Commit after each meaningful unit of work. Use conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`.
- Run `./hooks/post-task-verify.sh` after completing each task. Fix all errors before reporting done.
- New {components/modules/routes} follow the pattern in `{example path}`. [INITIAL]
- {stack-specific convention, e.g. "Use path aliases via @/ for imports"} [INITIAL]

## Ask first
- Before adding any new dependency to {package file}
- Before creating new API endpoints or database tables
- Before modifying project configuration files ({list config files})
- Before changing any file outside the current task scope

## Never
- Delete or comment out existing tests. Fix them or ask for guidance.
- Hardcode secrets, API keys, or credentials. Use environment variables.
- Add lint suppression comments ({eslint-disable / # noqa / @ts-ignore / etc.}). Fix the underlying issue.
- Use {banned patterns for this stack, e.g. "any" type in TypeScript, "eval()" in Python}.
- Touch files outside the task scope. No drive-by refactoring.
- Commit without running `{test command}` first.

## Architecture
{3-5 lines describing the directory structure and boundaries:}
{e.g. "src/routes/ — API route handlers, one file per resource"}
{e.g. "src/services/ — business logic, no direct HTTP or DB imports"}
{e.g. "src/db/ — database models and migrations"}
{e.g. "tests/ mirrors src/ structure"}

## Patterns to follow
{Once the first few files exist, reference them:}
- New routes: follow `src/routes/health.ts` [INITIAL]
- New tests: follow `tests/health.test.ts` [INITIAL]

---
_This is a living document. Remove [INITIAL] tags once validated. Add new rules only when a real failure occurs — every line should trace to a specific mistake._
```

---

## CLAUDE.md template

Only generate if the user uses Claude Code.

```markdown
# CLAUDE.md

Read AGENTS.md first — it contains the core project rules.

## Claude Code specific

### Hooks
- Post-file-edit: `hooks/post-file-edit.sh` — auto lint+typecheck
- Pre-commit: `hooks/pre-commit.sh` — block test suppression and secret leaks

### Skills
Check `skills/using-skills/SKILL.md` to determine which skill applies to the current task.

### Planning gate
Before any multi-file change, output a plan using `.harness/plan-template.md` format. Wait for approval.

### Progress
Read `.harness/progress.md` at session start. Update it before ending the session.
```

---

## .harness/task-template.md

```markdown
## Task: {title}

### Scope
Files to modify:
  - {path} → {1-sentence description}

Files to read (do not modify):
  - {path} → {why: pattern to follow}

### Pattern to follow
{Reference existing file: "Follow the pattern in src/routes/health.ts"}

### Acceptance criteria
1. `{test command}` passes
2. `{lint command}` passes
3. {domain-specific check}

### Out of scope
{What NOT to touch}
```

---

## .harness/plan-template.md

```markdown
## Plan: {task title}

Before modifying any file, output a plan in this format and wait for approval.

1. **Files to modify**: [list with 1-sentence each]
2. **Files to create**: [list]
3. **New dependencies**: [each with justification, or "none"]
4. **Verification**: [commands to run after implementation]
5. **Assumptions**: [mark each with [ASSUMPTION]]
```

---

## .harness/impact-map.sh

### TypeScript / JavaScript version
```bash
#!/bin/bash
MODULE_PATH="${1:?Usage: impact-map.sh <module-path>}"
echo "=== IMPACT MAP: $MODULE_PATH ==="
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""
echo "CORE FILES (in module):"
find "$MODULE_PATH" -name '*.ts' -o -name '*.tsx' | sort
echo ""
echo "DEPENDENTS (files importing from this module):"
grep -r "from ['\"].*$(basename $MODULE_PATH)" ./src --include='*.ts' --include='*.tsx' -l 2>/dev/null | sort
echo ""
echo "TESTS:"
find . -path "*/test*" -name "*$(basename $MODULE_PATH)*" -o -path "*__tests__*" -name "*$(basename $MODULE_PATH)*" 2>/dev/null | sort
echo ""
echo "EXPORTS:"
grep -rn "^export" "$MODULE_PATH"/*.ts "$MODULE_PATH"/index.ts 2>/dev/null
```

### Python version
```bash
#!/bin/bash
MODULE_PATH="${1:?Usage: impact-map.sh <module-path>}"
MODULE_NAME=$(basename "$MODULE_PATH")
echo "=== IMPACT MAP: $MODULE_PATH ==="
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""
echo "CORE FILES:"
find "$MODULE_PATH" -name '*.py' | sort
echo ""
echo "DEPENDENTS:"
grep -r "from $MODULE_NAME\|import $MODULE_NAME" . --include='*.py' -l 2>/dev/null | grep -v "$MODULE_PATH" | sort
echo ""
echo "TESTS:"
find . -path "*/test*$MODULE_NAME*" -name '*.py' 2>/dev/null | sort
echo ""
echo "PUBLIC API:"
grep -rn "^def \|^class \|^async def " "$MODULE_PATH"/*.py 2>/dev/null | grep -v "^.*:def _"
```

### Rust version
```bash
#!/bin/bash
MODULE_PATH="${1:?Usage: impact-map.sh <module-path>}"
echo "=== IMPACT MAP: $MODULE_PATH ==="
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""
echo "CORE FILES:"
find "$MODULE_PATH" -name '*.rs' | sort
echo ""
echo "DEPENDENTS:"
grep -r "use.*$(basename $MODULE_PATH)" ./src --include='*.rs' -l 2>/dev/null | sort
echo ""
echo "TESTS:"
grep -rn "#\[cfg(test)\]\|#\[test\]" "$MODULE_PATH" 2>/dev/null
echo ""
echo "PUBLIC API:"
grep -rn "^pub " "$MODULE_PATH"/*.rs 2>/dev/null
```

---

## .harness/progress.md (starts empty)

```markdown
## Current state
- Latest release: (none)
- Completed: (none)
- In progress: (none)
- Next session should: (pending first task)

## Recent (last 3 sub-features only)
(none yet)

## Archive
Full history: `.harness/archive/completed-phases.md`
```

**progress.md rules:**
- This file must never exceed 50 lines.
- When a phase or milestone is completed, move its detailed entries
  to `.harness/archive/completed-phases.md` and leave only a one-line
  summary in the "Completed" list above.
- The "Recent" section holds at most 3 entries. When a 4th is added,
  archive the oldest.
- Create `.harness/archive/` directory and an empty
  `completed-phases.md` file during scaffold generation.

---

## .harness/session-log.md

```markdown
# Session log

Entries use timestamp + tool name as unique identifier.
Do not use sequential session numbers — they collide when
multiple agents work on the same project.

Format per entry:

## {YYYY-MM-DD}T{HH:MM}Z — {tool}
**Phase:** {current phase or task}
**Resuming from:** {what progress.md said to do next}
**Completed:** {what was done}
**Uncommitted work:** YES/NO
**Rework:** YES/NO — {what was redone from a prior session, if any}
**First-attempt success:** {N}/{M} subtasks passed on first try
```

---

## .harness/anti-rationalization.md

```markdown
# Anti-rationalization table

Pre-written rebuttals to common agent excuses for skipping quality steps.

| Agent will say | Why it's wrong | Correct action |
|---------------|----------------|----------------|
| "I'll add tests later" | Later never comes. Ship tested. | Write tests now. |
| "This is too small to need tests" | Small changes break things. | At least one test. |
| "I need to refactor this other module first" | Scope creep. Stay on task. | Note it as a separate task. |
| "The existing test is wrong" | Tests document intent. Don't erase that. | Fix code or ask the user. |
| "This lint rule doesn't apply here" | It was added for a reason. | Fix the code, not the rule. |
| "I'll clean this up in a follow-up" | Follow-ups don't happen. | Clean it now. |
| "I need to install {library} for this" | Check if an equivalent already exists. | Search the codebase first, then ask. |
```

---

## skills/using-skills/SKILL.md (meta-router)

```markdown
---
name: using-skills
description: "Router that selects which project skill to activate for the current task. Loaded at session start."
---

# Skill Router

Before starting any task, check which skill applies:

- **spec-driven-development** — Use when starting any new feature or significant change. Write a spec before writing code.
- **incremental-implementation** — Use for any task that touches >3 files. Build in small, tested increments.
- **versioning-and-changelog** — Use when the user says "release", "bump version", "cut a release", or after finishing a feature to record changes. Also updates CHANGELOG.md during incremental implementation.
{add lines for additional skills generated based on project profile}

## Non-negotiable
- Touch only what you're asked to touch.
- Don't remove code you don't fully understand.
- Don't refactor adjacent files because you noticed a TODO.
- Load only the relevant skill. Don't read all skills at once.
```

---

## skills/spec-driven-development/SKILL.md

```markdown
---
name: spec-driven-development
description: "Write a structured specification before writing any code. Trigger when starting a new feature, API endpoint, component, or significant change. Also trigger when the user gives a vague requirement that needs decomposition."
---

# Spec-driven development

## Overview
Write a spec before code. The spec is a contract between you and the user. It eliminates the most expensive failure mode: building the wrong thing correctly.

## Process

1. **Receive the requirement** — could be vague ("add user profiles") or precise.

2. **Write the spec** using `.harness/task-template.md` format:
   - List exact files to create or modify
   - Define acceptance criteria as runnable commands
   - State what's out of scope
   - Mark any assumptions with [ASSUMPTION]

3. **Present to user for approval.** Do not write any code until approved.

4. **After approval**, proceed to implementation using the incremental-implementation skill.

## Anti-rationalization

| Agent excuse | Rebuttal |
|-------------|----------|
| "This is simple enough to just build" | If it's simple, the spec takes 30 seconds. Write it. |
| "The user already described what they want" | User descriptions are requirements, not specs. Translate. |
| "I'll figure out the details as I go" | That's how scope creep starts. Decide now. |

## Verification
- Spec exists and was presented to the user before any code was written.
- All acceptance criteria in the spec are testable commands.
- Out-of-scope section is explicitly defined.
```

---

## skills/incremental-implementation/SKILL.md

```markdown
---
name: incremental-implementation
description: "Build features in small, tested, committed increments rather than large batches. Trigger when the task touches more than 3 files or involves multiple logical steps."
---

# Incremental implementation

## Overview
Large batches of changes are hard to review, hard to debug, and hard to revert. Build in the smallest increment that is independently testable and committable.

## Process

1. **Decompose** the spec into ordered steps. Each step should:
   - Touch 1-3 files
   - Be independently testable
   - Leave the codebase in a working state

2. **For each step:**
   a. Write the code change
   b. Write or update the test
   c. Run `{test command}` — must pass
   d. Run `{lint command}` — must pass
   e. Commit with a descriptive conventional commit message
   f. Update CHANGELOG.md under `## [Unreleased]` with a one-liner for this change
   g. Update `.harness/progress.md`

3. **After all steps:** Run the full test suite one final time.

## Anti-rationalization

| Agent excuse | Rebuttal |
|-------------|----------|
| "It's faster to do it all at once" | Faster to write, slower to debug. Increments win. |
| "These changes are too interconnected to separate" | Find the lowest-dependency piece and start there. |
| "I'll commit at the end" | If the last step fails, you lose everything. Commit as you go. |
| "I'll update the changelog later" | You'll forget entries. One line per commit, right after committing. |

## Red flags
- Uncommitted changes spanning >5 files
- Tests not run for >2 consecutive file edits
- Progress file not updated after completing a step
- CHANGELOG.md not updated after a commit
```

---

## hooks/post-file-edit.sh

### TypeScript version
```bash
#!/bin/bash
FILE="$1"
case "$FILE" in
  *.ts|*.tsx)
    npx tsc --noEmit 2>&1 || exit 1
    npx eslint "$FILE" --max-warnings 0 2>&1 || exit 1
    ;;
  *.css|*.scss)
    npx prettier --check "$FILE" 2>&1 || exit 1
    ;;
esac
```

### Python version
```bash
#!/bin/bash
FILE="$1"
case "$FILE" in
  *.py)
    ruff check "$FILE" 2>&1 || exit 1
    ruff format --check "$FILE" 2>&1 || exit 1
    ;;
esac
```

### Rust version
```bash
#!/bin/bash
FILE="$1"
case "$FILE" in
  *.rs)
    cargo check 2>&1 || exit 1
    cargo clippy -- -D warnings 2>&1 || exit 1
    ;;
esac
```

---

## hooks/pre-commit.sh (universal)

```bash
#!/bin/bash
# Block test suppression
if git diff --cached | grep -E '\.skip\(|xit\(|xdescribe\(|@pytest\.mark\.skip' ; then
  echo "ERROR: Skipped tests detected. Fix the test or remove the skip."
  exit 1
fi

# Block lint suppression
if git diff --cached | grep -E 'eslint-disable|@ts-ignore|# type: ignore|# noqa' ; then
  echo "ERROR: Lint suppression detected. Fix the underlying issue."
  exit 1
fi

# Block hardcoded secrets
if git diff --cached | grep -iE '(api_key|secret|password|token)\s*=\s*["\x27][^"\x27]{8,}' ; then
  echo "ERROR: Possible hardcoded secret. Use environment variables."
  exit 1
fi
```

---

## hooks/post-task-verify.sh

This hook is run by the agent (or user) at the end of each task
to verify that all finalization obligations were met. Unlike
post-file-edit.sh (which runs after each edit), this runs once
per completed task.

```bash
#!/bin/bash
set -euo pipefail

# Gate 1: CHANGELOG was updated
UNRELEASED=$(grep -c "## \[Unreleased\]" CHANGELOG.md 2>/dev/null || echo "0")
if [ "$UNRELEASED" = "0" ]; then
  echo "ERROR: CHANGELOG.md missing or has no [Unreleased] section."
  echo "FIX: Update CHANGELOG.md under [Unreleased] with a summary of this task's changes."
  exit 1
fi

LAST_CHANGELOG_COMMIT=$(git log -1 --format="%H" -- CHANGELOG.md 2>/dev/null || echo "none")
LAST_ANY_COMMIT=$(git log -1 --format="%H" 2>/dev/null || echo "none")
if [ "$LAST_CHANGELOG_COMMIT" != "$LAST_ANY_COMMIT" ]; then
  echo "WARNING: CHANGELOG.md was not updated in the latest commit."
  echo "FIX: Amend the commit or create a new commit with CHANGELOG updates."
fi

# Gate 2: progress.md was updated
if [ -f .harness/progress.md ]; then
  PROGRESS_LINES=$(wc -l < .harness/progress.md)
  if [ "$PROGRESS_LINES" -gt 50 ]; then
    echo "ERROR: .harness/progress.md exceeds 50 lines ($PROGRESS_LINES lines)."
    echo "FIX: Archive completed phases to .harness/archive/completed-phases.md."
    exit 1
  fi
fi

# Gate 3: No uncommitted changes
DIRTY=$(git status --short 2>/dev/null)
if [ -n "$DIRTY" ]; then
  echo "ERROR: Uncommitted changes detected:"
  echo "$DIRTY"
  echo "FIX: Stage and commit all changes, or stash unrelated work."
  exit 1
fi

# Gate 4: Must be on main (task branch should be merged and deleted)
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
if [ "$BRANCH" != "main" ]; then
  echo "ERROR: Still on branch '$BRANCH'. Task branch was not merged."
  echo "FIX: Merge to main and delete the task branch:"
  echo "  git checkout main && git merge $BRANCH --no-ff && git branch -d $BRANCH"
  exit 1
fi

# Gate 5: Audit trigger check
if [ -f .harness/progress.md ]; then
  COMPLETED_COUNT=$(grep -c "^- " .harness/progress.md 2>/dev/null || echo "0")
  LAST_AUDIT=$(grep "Last audit:" .harness/progress.md 2>/dev/null | tail -1 || echo "")
  if [ "$COMPLETED_COUNT" -gt 3 ] && [ -z "$LAST_AUDIT" ]; then
    echo "NOTICE: 3+ phases completed since last audit."
    echo "Consider running a periodic audit (see shared-generation-standards.md)."
  fi
fi

echo "✅ Post-task verification passed."
```

---

## .github/workflows/ai-quality-gate.yml

```yaml
name: AI Quality Gate
on: [pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: No test suppression
        run: |
          if git diff origin/main...HEAD | grep -E '\.skip\(|xit\(|@pytest\.mark\.skip'; then
            echo "::error::Test suppression detected"; exit 1
          fi
      - name: No lint suppression
        run: |
          if git diff origin/main...HEAD | grep -E 'eslint-disable|@ts-ignore|# noqa'; then
            echo "::error::Lint suppression detected"; exit 1
          fi
      - name: No hardcoded secrets
        run: |
          if git diff origin/main...HEAD | grep -iE '(api_key|secret|password)\s*=\s*["'"'"'][^"'"'"']{8,}'; then
            echo "::error::Possible hardcoded secret"; exit 1
          fi
```

---

## agents/code-reviewer.md (for medium+ projects)

```markdown
# Code Reviewer

You are a senior staff engineer reviewing code for correctness, clarity, and adherence to project conventions.

## Scope
- Logic errors and edge cases
- Convention violations (check AGENTS.md)
- Test coverage gaps
- Unnecessary complexity
- Scope creep (changes outside the stated task)

## Ignore
- Cosmetic preferences already handled by the formatter
- Performance micro-optimizations unless there's a measurable problem

## Output format
- **Verdict**: PASS / NEEDS_CHANGES / BLOCK
- **Findings**: specific issues with file paths
- **Suggestions**: improvements (clearly separated from blockers)

## Composition
- Invoked by: user or /review command
- Does not invoke other personas
```

---

## CHANGELOG.md (initial template for new projects)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

## [0.1.0] - {today's date YYYY-MM-DD}

### Added
- Initial project scaffold with harness engineering structure
```

---

## skills/versioning-and-changelog/SKILL.md

```markdown
---
name: versioning-and-changelog
description: "Track project changes and manage version releases. Trigger when the user says 'release', 'bump version', 'tag', 'cut a release', 'version iteration', or after finishing a feature to record changes in CHANGELOG.md."
---

# Versioning & Changelog

## Overview
This skill manages two things: recording what changed (CHANGELOG.md) and releasing versions (SemVer + git tags).

## Recording changes (during development)

After each commit, add a one-liner under `## [Unreleased]` in CHANGELOG.md:

| Commit prefix | Changelog category |
|---------------|-------------------|
| feat: | ### Added |
| fix: | ### Fixed |
| refactor: / chore: | ### Changed |
| docs: | (skip unless user-facing) |

## Cutting a release (when user says "release")

1. Review entries under `## [Unreleased]`
2. Determine bump type:
   - Any `Added` → MINOR (v1.2.3 → v1.3.0)
   - Only `Fixed`/`Changed` → PATCH (v1.2.3 → v1.2.4)
   - Any `Removed` or breaking change → MAJOR (v1.2.3 → v2.0.0)
3. Present proposed version to user for confirmation
4. Move `[Unreleased]` entries to new version section with today's date
5. Update version in project config (package.json / pyproject.toml / Cargo.toml)
6. Commit: `git commit -m "chore: release v{version}"`
7. Tag: `git tag -a v{version} -m "Release v{version}"`
8. Push: `git push origin main --follow-tags`
9. GitHub release (if gh CLI available): `gh release create v{version} --notes "..."`

## Anti-rationalization

| Agent excuse | Rebuttal |
|-------------|----------|
| "I'll update the changelog at the end" | You'll forget entries. Update per commit. |
| "This is too small for the changelog" | If it's worth committing, it's worth recording. |
| "I'll just bump patch" | Added features are MINOR by definition. Follow SemVer. |
```
