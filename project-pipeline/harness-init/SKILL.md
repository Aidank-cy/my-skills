---
name: harness-init
description: >
  This skill should be used when the user asks to create a new project,
  initialize a new repository, scaffold an app, run an init command, or
  says things like "new project", "init a repo", "create a project",
  "scaffold a project", "set up a new codebase", or "harness project".
  Bootstrap the standard project first, then generate a harness
  engineering scaffold with AGENTS.md, CHANGELOG.md, .harness,
  hooks, and CI so the repository is agent-ready from day one.
  Core pipeline skills are user-level and not duplicated into the
  project. Use this skill only for new projects; use
  harness-engineering-transform for existing codebases.
---

# Harness Init

Bootstrap a brand-new project with harness engineering from the start.
Generate the standard project and the harness scaffold in one pass.

## Conversation mode check

Activate only when the user explicitly asks to initialize, scaffold,
or create a project-level harness. Skip this skill for casual
conversation, general project discussion, read-only questions, or
requests that do not target a new or empty project.

## Core rules

- Use this skill only for new or empty projects.
- Infer as much as possible from the user's request.
- Ask only for information that cannot be inferred safely.
- Generate `AGENTS.md` as the primary cross-tool rule file.
- Keep generated rules concrete, short, and runnable.

## Workflow

1. Profile the project.
2. Run the standard project init when needed.
3. Generate the harness scaffold.
4. Apply post-generation setup.
5. Brief the user on what matters most.

## Step 1: Profile the project

Infer these dimensions first:

| Dimension | Common values | Default |
|-----------|---------------|---------|
| Language | TypeScript, Python, Rust, Go | TypeScript |
| Framework | Next.js, FastAPI, Actix, Gin, none | none |
| Package manager | pnpm, npm, yarn, pip, poetry, cargo | pnpm for JS, pip for Python |
| Test framework | vitest, jest, pytest, cargo test | vitest for JS, pytest for Python |
| Lint and format | eslint+prettier, biome, ruff, clippy | eslint+prettier for JS, ruff for Python |
| Architecture | monolith, monorepo, library, CLI, fullstack | monolith |
| API | yes or no | infer from framework |
| Database | yes or no | no |
| Frontend | yes or no | infer from framework |
| Auth | yes or no | no |

Infer tool preference when possible:
- Claude Code → add `CLAUDE.md` and Claude-specific structure
- Cursor → add `.cursor/rules/`
- GitHub Copilot → add `.github/copilot-instructions.md`
- unsure or mixed → always generate `AGENTS.md` and add tool-specific files only when justified

## Step 2: Run the standard init

Run the framework or language bootstrap first when the project does not already exist.
Examples:
- `npx create-next-app@latest`
- `cargo init`
- `poetry new`
- `pnpm init`

Skip this step when the user already created the directory or initialized the project.

## Step 3: Generate the harness scaffold

Generate these core artifacts:
- `AGENTS.md`
- `CHANGELOG.md`
- `.harness/`
- `hooks/`
- CI quality gate workflow

Generate optional artifacts based on project shape:
- `CLAUDE.md`
- `.cursor/rules/`
- `.github/copilot-instructions.md`
- `agents/`
- `skills/` — only for project-specific domain skills (API, database, frontend, security)

Core pipeline skills (`prompt-gateway`, `versioning-and-changelog`,
`git-workflow`, `skill-authoring`, `sync-filter`) are user-level.
Do not duplicate them into the project's `skills/` directory.

When generating the AGENTS.md file, always include a `## Skills`
section that lists every skill in the project's `skills/`
directory with name and one-line purpose. This section is the
deterministic entry point that ensures agents discover project-
level skills regardless of which agent runtime is used. If
`skills/` contains symlinks to project-pipeline skills, list
them. If it contains project-local skills, list those too.

For AGENTS.md generation standards, verification requirements, and
design principles, read `references/shared-generation-standards.md`.

For the full scaffold layout and generation matrix, read `references/bootstrap-layout.md`.
For file content templates, read `references/file-templates.md`.

## Step 4: Post-generation setup

After writing the files:
- make harness scripts executable
- initialize git if needed
- create the initial local commit

Apply this git boundary:
- local git operations are allowed
- remote git operations stay user-owned unless the user explicitly requests them

## Step 5: Brief the user

Explain these priorities:
- review `AGENTS.md` first
- treat hooks as deterministic enforcement
- load skills on demand instead of all at once
- AGENTS.md `## Skills` section ensures all agents discover
  project-level skills — verify it lists every skill in skills/
- use `.harness/progress.md` as cross-session memory
- ratchet new rules or hooks in response to real failures

## Relationship to transform

Use `harness-init` for new projects.
Use `harness-engineering-transform` for existing codebases.
If a formerly empty project later grows from imported legacy code, rerun the transform workflow to adapt the harness to real patterns.

## Anti-rationalization

Reject these shortcuts:
- asking too many setup questions before inferring basics
- generating every optional file regardless of project size
- writing vague AGENTS rules with no runnable commands
- skipping hooks or CI because the scaffold is "only initial"
- leaving the project without a concrete example pattern
- Keeping rules that have never been triggered by a real failure
- Treating skill file count or word count as a quality signal

## References

| When needed | Read |
|-------------|------|
| Need AGENTS.md standards, verification requirements, or design principles | `references/shared-generation-standards.md` |
| Need the full scaffold layout, optional file matrix, or post-generation checklist | `references/bootstrap-layout.md` |
| Need the concrete file templates to generate | `references/file-templates.md` |
