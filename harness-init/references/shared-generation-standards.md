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

## Design principles

- Apply the ratchet principle: add constraints in response to real
  failures or plausible high-risk failure modes.
- Distinguish probabilistic guidance from deterministic enforcement.
- Prefer progressive disclosure over loading every rule at once.
- Keep context small and structured.
- Separate generation from evaluation when reviewer personas are
  available.
- Keep outputs model-agnostic unless a tool-specific file is required.
