---
name: prompt-gateway
description: >
  This skill should be used when the user asks to add, modify, remove,
  refactor, or fix project functionality, including prompts like "add
  feature", "fix bug", "modify X", "implement Y", "add functionality",
  "modify functionality", "new feature", "fix issue", "next change", "next feature", or any
  code-change request. Route every code-modification prompt through
  a task-based gate: decompose the prompt into a task with subtasks,
  create a feature branch, execute all subtasks, verify, commit, and
  merge back to main. Reject vague prompts with guidance. Treat
  git-workflow and versioning-and-changelog as hard dependencies.
  Do not use for questions, explanations, reviews, release-only tasks,
  or other read-only work.
---

# Prompt Gateway

Route every code-modification prompt through a structured task gate.
One prompt = one task. One task = one branch lifecycle.

## Core concept

```
User prompt
  → Task (with subtasks)
    → Branch from main
      → Execute subtasks one by one
        → Verify all subtasks
          → Commit
            → Merge to main
              → Ready for next task
```

A task that skips any stage is incomplete.

## Workflow

0. Branch state gate
1. Classify the request
2. Validate and decompose into task + subtasks
3. Check harness integrity
4. Build execution plan
5. Execute subtasks and verify
6. Finalize: CHANGELOG → commit → merge to main

## Step 0: Branch state gate

Before entering the pipeline, verify git branch state.

```
□ Am I on main?
  → YES: proceed to Step 1.
  → NO (on a feature branch):
    ├── Is the current branch's work complete and committed?
    │   → YES: merge to main, delete branch, then proceed to Step 1.
    │   → NO: finish the current task first (Steps 5→6),
    │          then merge to main, then proceed to Step 1.
    └── Does the branch name match this new task?
        → If not, this is feature drift. Stop and resolve.
```

After the gate passes, create the feature branch per `git-workflow`
conventions:

```bash
git checkout main
git pull origin main
git checkout -b {type}/{short-description}
```

## Step 1: Classify

| Request type | Action |
|---|---|
| Code modification | Continue to Step 2 |
| Read-only question, explanation, review | Skip this skill |
| Release or version request | Delegate to `versioning-and-changelog` |
| Harness setup or bootstrap | Delegate to `harness-init` or `harness-engineering-transform` |

## Step 2: Validate and decompose

### Validation

Accept either format:

**Tier A — Full spec** (all four sections required):
`## Task`, `## Context`, `## Requirements`, `## Scope`

**Tier B — Lightweight spec** (all three elements required):
- **What:** clear change description
- **Where:** file path, module, or component name
- **Done-when:** testable success condition

If 2 of 3 Tier B elements are present, ask for the missing piece.
If fewer than 2, reject with guidance.

Allow trivial edits (typos, comments, single-line config) without
full structure. If the request touches logic, require at least Tier B.

### Task decomposition

After validation passes, decompose the prompt into one task with
explicit subtasks:

```
Task: {task title derived from the prompt}
Branch: {type}/{short-description}

Subtasks:
  □ 1. {first atomic change — what + where + done-when}
  □ 2. {second atomic change}
  □ 3. ...
```

Decomposition rules:
- Each subtask is one atomic, independently verifiable change.
- A subtask modifies one logical unit (a function, a component,
  a config block).
- Order subtasks by dependency: foundations first, dependents later.
- If the prompt contains only one change, the task has one subtask.

Present the decomposition to the user for confirmation before
proceeding. Adjust if the user disagrees.

For validation examples and rejection copy, read
`references/prompt-validation.md`.

## Step 3: Check harness integrity

### Required files

| Path | Purpose |
|---|---|
| `AGENTS.md` | Execution boundaries and patterns |
| `CHANGELOG.md` | Required for Step 6A |
| `.harness/` | Harness runtime container |
| `.harness/progress.md` | Cross-session state |

### Decision rule

- 1–2 items missing: create sensible defaults, log in
  `.harness/progress.md`, continue.
- 3+ items missing: stop and direct to `harness-init` or
  `harness-engineering-transform`.

### Nice-to-have (warn, do not block)

`hooks/post-file-edit.sh`, `hooks/pre-commit.sh`,
`.harness/task-template.md`, `.harness/impact-map.sh`, `CLAUDE.md`

## Step 4: Build execution plan

Read: `AGENTS.md`, repo structure, `.harness/progress.md`,
unreleased CHANGELOG entries, latest local tag.

Produce:

```
Task: {title}
Branch: {type}/{short-description}
Impact: LOW | MEDIUM | HIGH | CRITICAL
Subtasks:
  1. {subtask} → files: {list} → verify: {how}
  2. ...
CHANGELOG draft: {category}: {entry}
```

| Impact | Meaning | Extra |
|---|---|---|
| LOW | Single file, no API/dependency change | None |
| MEDIUM | Multiple files, one area | Full verification |
| HIGH | Cross-module or dependency change | Impact analysis + AGENTS review |
| CRITICAL | Auth, payments, data model, infra | Present plan, wait for confirmation |

## Step 5: Execute subtasks and verify

Process subtasks sequentially:

```
For each subtask:
  1. Execute the change
  2. Run hooks/post-file-edit.sh if it exists
  3. Verify: lint, typecheck, tests, subtask-specific criteria
  4. Mark subtask complete: □ → ✅
  5. If verification fails, fix before moving to next subtask
```

Execution rules:
- Re-read `AGENTS.md` boundaries before risky changes.
- Stay inside scope.
- Record out-of-scope findings in `.harness/progress.md`.
- Keep each subtask atomic and independently verifiable.

After all subtasks pass, run a final full verification:
lint + typecheck + tests + acceptance criteria.

### Plan alignment check

After all subtasks pass technical verification, confirm architectural alignment:

```
□ Did the implementation reuse existing patterns and abstractions
  found in the codebase, rather than creating new ones?
□ Does the implementation stay within the file and module scope
  defined in Step 4's plan?
□ If new files were created, do they follow the project's
  established directory and naming conventions?
□ Were any lint-disable or noqa comments added? If so, remove them
  and fix the underlying violation.
```

If any check fails, fix before proceeding to Step 6.

## Step 6: Finalize

Non-negotiable. Do not return to the user before completing all
sub-steps in order.

### 6A: CHANGELOG handoff

Invoke `versioning-and-changelog` Flow 1. Verify:
- `CHANGELOG.md` changed in this task
- New entries under `## [Unreleased]`
- Correct Keep a Changelog category
- Entries begin with action verbs

### 6B: Rules update (conditional)

Update `AGENTS.md` when a new pattern, failure mode, or boundary
was established. Tag new rules with `[NEW]`.
Update `CLAUDE.md` when Claude-specific commands or routing changed.
Skip when nothing changed.

### 6C: Progress update

Append to `.harness/progress.md`:
- Date, task title, status
- Subtask completion summary
- Follow-ups and out-of-scope findings

### 6D: Commit

Pre-commit checklist:

```
□ All subtasks verified?
□ CHANGELOG updated (6A)?
□ Rules updated if needed (6B)?
□ Progress updated (6C)?
□ Lint, typecheck, tests pass?
□ No unrelated changes staged?
```

Create a single conventional commit covering the entire task.
Follow `git-workflow` commit format.

If the task has genuinely independent logical changes that warrant
separate commits, create one commit per logical change, each
independently passing all checks.

### 6D-alt: Sandbox mode (Codex or restricted environments)

When running in a sandboxed environment without direct git commit/push
access:

1. Stage all changes: `git add -A`
2. Write the proposed commit message to `.harness/pending-commit.md`
   using `git-workflow` commit conventions.
3. Present the full diff summary and proposed commit message.
4. Skip Steps 6D and 6E — the user owns commit and merge.

Detection: if `git commit` fails with a permissions or sandbox error,
or if the user has indicated Codex/sandbox mode, use this path
automatically.

### 6E: Merge to main

After all commits are done, execute the merge protocol from
`git-workflow`:

```bash
git checkout main
git merge {feature-branch} --no-ff
git branch -d {feature-branch}
git status --short          # expect clean
git log --oneline -3        # confirm merge
```

Return to the user in this order:

**1. Task summary:**
- Commit hash(es) and message(s)
- File count summary
- CHANGELOG status
- Merge confirmation

**2. User verification commands:**

Present concrete commands the user can run to inspect and verify the
changes before pushing. Tailor these to the project's actual toolchain
and the files changed in the task. Always include at minimum:
- A diff command to review what changed
- The project's build or typecheck command
- A way to visually inspect or run the result (dev server, open file,
  run CLI, etc.)

Example:

```
Verify the changes:
  git diff HEAD~1                    # review what changed
  cd {project} && npm run build      # confirm build passes
  npm run dev                        # inspect at localhost:3000
```

Adapt the commands to the real project. Use `pytest`, `cargo test`,
`go build`, or whatever the project actually runs. If the change is
visual, suggest opening the relevant page or component. If it is a
CLI tool, suggest running it with a test input. Do not include generic
placeholder commands — every command must be runnable as-is.

**3. Remote sync (handoff to `harness-remote-handoff`):**

Present the git push command(s) per `harness-remote-handoff`.

The project is now on main, ready for the next task.

### 6F: Project-level Always obligations

Regardless of task-scoped restrictions, always complete these
before finishing:

1. Update `CHANGELOG.md` under `[Unreleased]` with a summary
   of what this task changed.
2. Update `.harness/progress.md` "Recent" section with the
   completed work.

These obligations cannot be overridden by task-level "out of scope"
declarations.

## Task lifecycle summary

```
┌─────────────────────────────────────────────────┐
│  User prompt                                     │
│    ↓                                             │
│  Step 0: Branch gate → checkout -b new branch    │
│  Step 1: Classify                                │
│  Step 2: Validate → decompose into subtasks      │
│  Step 3: Harness check                           │
│  Step 4: Build plan                              │
│  Step 5: Execute subtasks one by one             │
│  Step 6A: CHANGELOG                              │
│  Step 6B: Rules (if needed)                      │
│  Step 6C: Progress                               │
│  Step 6D: Commit or 6D-alt sandbox handoff       │
│  Step 6E: Merge to main → delete branch          │
│  Step 6F: Project-level Always obligations       │
│    ↓                                             │
│  ✅ Done. Ready for next task.                    │
└─────────────────────────────────────────────────┘
```

## Integration points

| Skill | Relationship |
|---|---|
| `git-workflow` | Owns branch naming, commit format, merge mechanics. This skill triggers the operations; `git-workflow` defines the norms. |
| `versioning-and-changelog` | Hard dependency. Owns CHANGELOG categorization and insertion. Step 6A is non-negotiable. |
| `harness-engineering-transform` | Suggested when harness integrity check fails badly. |
| `harness-remote-handoff` | Governs context recovery between sessions. |

## Anti-rationalization

Reject these shortcuts:
- Skipping prompt validation because the request "seems clear"
- Skipping task decomposition for multi-change prompts
- Discovering scope during execution
- Postponing CHANGELOG update
- Skipping harness integrity check
- Treating changes as "too small" for the pipeline
- Skipping Step 0 because "I'm already on a branch"
- Adding task B's changes to task A's branch
- Skipping the merge-to-main step
- Committing directly on main
- Skipping sandbox mode detection when git operations fail
- Letting a task-scoped "out of scope" declaration override
  project-level Always rules. CHANGELOG.md and progress.md updates
  are Always obligations — a task prompt cannot exempt them.
- Keeping rules that have never been triggered by a real failure
- Treating skill file count or word count as a quality signal

## References

| When needed | Read |
|---|---|
| Tier A/B examples, detection patterns, rejection wording | `references/prompt-validation.md` |
| CHANGELOG, rules, progress, commit-close details | `references/finalization-checklist.md` |
