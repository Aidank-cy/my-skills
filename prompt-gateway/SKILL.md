---
name: prompt-gateway
description: >
  This skill should be used when the user asks to add, modify, remove,
  refactor, or fix project functionality, including prompts like "add
  feature", "fix bug", "modify X", "implement Y", "添加功能",
  "修改功能", "新增", or "修复". Validate that the task is
  structured as either a full spec or a lightweight spec, reject vague
  prompts with guidance, map valid prompts into a project-aware execution
  plan, and orchestrate the full pipeline: harness integrity check,
  execution, mandatory handoff to versioning-and-changelog for CHANGELOG
  updates, rule updates when needed, local commit, and handoff of remote
  operations to the user. Do not use this skill for questions,
  explanations, reviews, release-only tasks, or other read-only work.
---

# Prompt Gateway

Route every code-modification task through a structured gate.
Protect scope, harness integrity, changelog discipline, and local git hygiene.

## Core rule

Accept only one of these inputs:
- a full spec
- a lightweight spec
- a genuinely trivial change

Reject vague code-change prompts.
Treat `versioning-and-changelog` as a hard dependency.
A task that skips the CHANGELOG handoff is incomplete.

## Workflow

1. Classify the request.
2. Validate the prompt structure.
3. Check harness integrity.
4. Read project state and build an execution plan.
5. Execute and verify the change.
6. Finalize with mandatory CHANGELOG, rules review, progress update, and local commit.

## Step 1: Classify

Use this routing table:

| Request type | Action |
|--------------|--------|
| Code modification | Continue to Step 2 |
| Read-only question, explanation, or review | Skip this skill |
| Release or version request | Delegate to `versioning-and-changelog` |
| Harness setup or project bootstrap | Delegate to `harness-init` or `harness-engineering-transform` |

## Step 2: Validate the prompt

Accept either Tier A or Tier B.

### Tier A: Full spec

Require all four sections:
- `## Task`
- `## Context`
- `## Requirements`
- `## Scope`

Recognize optional sections such as `## Constraints`, `## Dependencies`, `## Test Plan`, and `## References`.

### Tier B: Lightweight spec

Require all three elements:
- **What:** a clear change description
- **Where:** at least one file path, module name, or component name
- **Done-when:** at least one testable success condition

### Validation logic

Apply this decision path:
- If the prompt includes structured headers such as `## Task`, `## Requirements`, or `## Scope`, treat it as Tier A and verify all required sections.
- If the prompt does not include those headers, test Tier B.
- If Tier B has all three elements, accept it.
- If Tier B has only two of the three elements, ask for the missing piece instead of rejecting outright.
- If the prompt has zero or one required element, reject it and provide guidance.

### Trivial exception

Allow truly trivial edits without full structure.
Use this exception only for typos, comments, or single-line config changes.
If the request touches logic, require at least Tier B.

### Rejection behavior

If neither tier passes:
- identify the missing parts explicitly
- offer a lightweight-spec path
- offer a full-spec path through Claude Code

For examples and user-facing rejection copy, read `references/prompt-validation.md`.

## Step 3: Check harness integrity

Run the harness check before reading project state.
Catch drift before execution.

### Minimum required files

| Path | Why it matters |
|------|----------------|
| `AGENTS.md` | execution boundaries and patterns |
| `CHANGELOG.md` | required for Step 6A |
| `.harness/` | harness runtime container |
| `.harness/progress.md` | cross-session state |
| `.harness/task-template.md` | Tier A reference format |

Core pipeline skills (`versioning-and-changelog`, `git-workflow`,
`prompt-gateway`) are user-level and always available. Do not check
for them inside the project. Only project-specific domain skills
live in the project's `skills/` directory.

### Decision rule

- If 1-2 required items are missing, create sensible defaults inline, record the repair in `.harness/progress.md`, and continue.
- If 3 or more required items are missing, stop and direct the user to run `harness-init` or `harness-engineering-transform`.

### Nice-to-have files

Warn, but do not block, when these are missing:
- `hooks/post-file-edit.sh`
- `hooks/pre-commit.sh`
- `.harness/impact-map.sh`
- `.harness/anti-rationalization.md`
- `CLAUDE.md`

## Step 4: Read project state and build the plan

Read:
- `AGENTS.md`
- repository structure
- `.harness/progress.md`
- unreleased changes in `CHANGELOG.md`
- latest local tag if one exists
- `.harness/impact-map.sh` output when relevant

Produce an execution plan with:
- task summary
- impact level: LOW, MEDIUM, HIGH, or CRITICAL
- estimated files changed
- pre-flight checks
- file-by-file changes
- AGENTS or rules impact
- verification commands
- draft changelog entry

### Impact rules

| Level | Meaning | Extra requirement |
|------|---------|-------------------|
| LOW | single file, no API or dependency change | none |
| MEDIUM | multiple files in one area | run full verification |
| HIGH | cross-module or dependency change | run impact analysis and review AGENTS |
| CRITICAL | auth, payments, data model, infra | present the plan and wait for explicit confirmation |

## Step 5: Execute and verify

Follow the execution plan.

### Execution rules

- Re-read `AGENTS.md` boundaries before risky changes.
- Stay inside scope.
- Record out-of-scope findings in `.harness/progress.md` instead of fixing them inline.
- Run `hooks/post-file-edit.sh` after each edit when it exists.
- Keep changes atomic and independently verifiable.

Track three things during execution:
- files changed and why
- rule observations
- out-of-scope issues

### Verification

Run all required checks before finalizing:
- lint
- typecheck when applicable
- tests
- any acceptance-criteria-specific verification from the plan

If verification fails, fix it before moving on.
If the required fix would exceed scope, stop and ask for guidance.

## Step 6: Finalize

Perform all closing steps in order.

### 6A: Mandatory CHANGELOG handoff

Invoke the `versioning-and-changelog` skill's Flow 1 procedure.
Do not invent a local substitute.

Require all of the following before moving on:
- `CHANGELOG.md` changed in this task
- new entries appear under `## [Unreleased]`
- entries use the correct Keep a Changelog category
- entries begin with a clear action verb

Treat a missing CHANGELOG update as a pipeline failure.
For detailed insertion and verification rules, read `references/finalization-checklist.md`.

### 6B: Rules update

Update rules only when execution proves the rules need to change.

Update `AGENTS.md` when:
- a new reusable pattern was established
- an old rule is outdated or incomplete
- a new failure mode requires a guardrail
- a new architectural boundary was introduced

Update `CLAUDE.md` when:
- Claude-specific commands or hooks changed
- skill routing changed

When proposing a new rule:
- add a `[NEW]` tag
- never remove existing rules without user confirmation
- keep `AGENTS.md` concise

### 6C: Progress update

Append a short completion note to `.harness/progress.md` with:
- date
- task title
- status
- changes summary
- follow-ups

### 6D: Local commit

Create an atomic conventional commit following `git-workflow` conventions.
Use a commit type that matches the changelog category.
Keep the subject line under 72 characters, imperative mood.
Use `feat!:` or `fix!:` only for breaking changes.
Refer to `git-workflow` for the full Conventional Commits format
and type-to-category mapping.

### 6E: Return remote operations to the user

Do not push, create PRs, or modify remote state.
Return:
- local commit hash and message
- file count summary
- CHANGELOG status
- rules status
- suggested next commands per `git-workflow` conventions:
  `git push origin {branch}`, `gh pr create`, or release commands

## Integration points

### With `versioning-and-changelog`

Use it as a hard dependency.
This skill owns pipeline timing.
`versioning-and-changelog` owns changelog categorization and insertion format.
Do not skip either side of that contract.

### With `spec-driven-development`

Treat a Claude Code processed prompt as the spec.
Do not add another spec phase.

### With `incremental-implementation`

Split HIGH or CRITICAL work into smaller verified steps when appropriate.
Still close the task with the Step 6 sequence.

### With `harness-engineering-transform`

Suggest it when the harness integrity check shows the project scaffold is missing or degraded.

### With `git-workflow`

Defer branch naming, commit format, PR conventions, and merge strategy
to `git-workflow`. This skill owns execution pipeline timing;
`git-workflow` owns git operation norms.

## Anti-rationalization

Reject these shortcuts:
- skipping prompt structure because the request "seems clear"
- discovering scope during execution
- postponing the CHANGELOG update
- writing a custom changelog entry instead of handing off to `versioning-and-changelog`
- skipping the harness integrity check
- treating source changes as too small for the pipeline

## References

| When needed | Read |
|-------------|------|
| Need Tier A or Tier B examples, detection patterns, or rejection wording | `references/prompt-validation.md` |
| Need detailed CHANGELOG, rules-update, progress, or commit-close rules | `references/finalization-checklist.md` |
