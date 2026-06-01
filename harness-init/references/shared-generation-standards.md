# Shared Generation Standards

Use these standards when generating or transforming harness artifacts.

## AGENTS.md generation standards

- Keep `AGENTS.md` at or below 60 lines.
- Use real project commands for install, lint, typecheck, test, build,
  and dev when those commands exist.
- Do not describe commands in prose when a runnable command can be
  listed instead.
- Use a three-tier boundary model: `Always`, `Ask first`, `Never`.
- Keep rules concrete, traceable, and tied to the actual project.
- Prefer model-agnostic guidance in `AGENTS.md`; put tool-specific
  guidance in `CLAUDE.md`, `.cursor/rules/`, or equivalent files.
- Mark new-project assumptions with `[INITIAL]`.
- Mark existing-codebase inferences with `[INFERRED]`.
- Include architecture and pattern guidance only when supported by
  project structure or a plausible failure mode.
- Keep generated rules short enough that agents will actually read
  and follow them.
- The Never tier must always include a ban on inline lint-disable
  comments (eslint-disable, noqa, @ts-ignore, etc.).

## Default code quality gates

When generating hooks and lint configuration for a new project,
include these gates from day one. Thresholds can be adjusted per
project but must not be omitted.

### Python projects (ruff)
- Add `"C901"` to the ruff `select` list
- Set `[tool.ruff.lint.mccabe] max-complexity = 18`

### JavaScript/TypeScript projects (eslint)
- `"complexity": ["error", { "max": 18 }]`
- `"max-depth": ["error", 5]`
- `"max-lines-per-function": ["error", { "max": 100, "skipBlankLines": true, "skipComments": true }]`
- `"max-lines": ["error", { "max": 360, "skipBlankLines": true, "skipComments": true }]`
- `"max-params": ["error", 5]`

### File size gate (all projects)
- `hooks/post-file-edit.sh` must include a file-size check that
  fails on any source file exceeding 360 lines.
- The error message must list the offending files and include a
  FIX instruction.

### Post-task verification gate (all projects)
- `hooks/post-task-verify.sh` must be generated for every project.
- It checks: CHANGELOG updated, progress.md under 50 lines, no
  uncommitted changes, on main branch (task branch merged), and
  audit trigger (3+ phases since last audit).
- Error messages must include the specific problem and a FIX
  instruction with runnable commands.
- This hook converts prompt-gateway Step 6's probabilistic
  obligations into deterministic checks.

### Rationale
Retrofitting these limits after hundreds of commits requires
splitting many files while preserving behavior and import paths.
Setting them from day one costs nearly nothing — the agent
naturally writes smaller files.

## Common verification checklist

Before finishing, confirm:
- `AGENTS.md` is short and contains real commands.
- Inferred or initial rules are labeled.
- `CHANGELOG.md` exists and matches the repo's version history state.
- Templates and hooks reference real project commands.
- Generated skills match the project's real domains.
- Generated files do not point to nonexistent tools, paths, or scripts.
- Executable scripts received executable permissions.
- Optional files are justified by the project shape.
- Rules that should be deterministic have matching hooks, CI, or tests
  where practical.
- Lint config includes complexity and file-size rules (not just
  syntax and formatting checks).
- `hooks/post-task-verify.sh` exists and checks CHANGELOG,
  progress.md, uncommitted changes, branch state, and audit trigger.

## Design principles

- Apply the ratchet principle: add constraints in response to real
  failures or plausible high-risk failure modes.
- Distinguish probabilistic guidance from deterministic enforcement.
- Prefer progressive disclosure over loading every rule at once.
- Keep context small and structured.
- Separate generation from evaluation when reviewer personas are
  available.
- Keep outputs model-agnostic unless a tool-specific file is required.

## Periodic audit procedure

Every 3+ completed phases (or every 2 weeks of active development,
whichever comes first), run this audit:

### Anti-rationalization audit
- Review every rule in AGENTS.md, anti-rationalization.md, and
  skill anti-rationalization sections.
- Remove or demote rules that have not been triggered by a real
  failure since the last audit.

### AGENTS.md audit
- Demote unused Always rules to Ask First.
- Remove Ask First rules that have never been triggered.
- Verify all commands are still runnable.

### progress.md audit
- Archive completed phases to .harness/archive/completed-phases.md.
- Confirm progress.md is under 50 lines.

### Skill audit
- Check each project-level skill for word count (max 3000 / 500 lines).
- Check for duplicated content across skills.
- Check that all reference pointers resolve to real files.

### Session-log audit
- Review Rework and First-attempt success trends.
- If a specific task type shows repeated rework, add a hook or
  skill to prevent recurrence.
