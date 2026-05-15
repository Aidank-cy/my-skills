---
name: sync-filter
description: >
  This skill should be used when the user asks to "add a file to the
  sync workflow", "classify a file as private or public", "audit the
  sync pipeline", "set up dev-to-public sync", or works on a project
  with a private dev repo that syncs to a public repo via GitHub Actions.
  Also trigger when encountering files like AGENTS.md, CLAUDE.md,
  .project-rules/, sync-public.yml, or any dev→public pipeline.
---

# Sync filter

Manage the boundary between a private dev repo and its public mirror.
The sync workflow strips private files then force-pushes the clean
result. Keep the workflow in sync with reality at all times.

## Classification decision tree

Work top-down. Stop at the first match.

| # | Condition | Action |
|---|-----------|--------|
| 1 | AI agent config (`AGENTS.md`, `CLAUDE.md`, `.cursor/`, `copilot-instructions.md`, `skills/`, `hooks/`) | **PRIVATE** |
| 2 | Internal process docs (`.project-rules/`, `.harness/`, `CHANGELOG.md`, `TODO.md`) | **PRIVATE** |
| 3 | Sync workflow or private-only CI (`sync-public.yml`, `ai-quality-gate.yml`) | **PRIVATE** |
| 4 | Contains secrets, tokens, private registry URLs, or internal endpoints | **PRIVATE** |
| 5 | App source, build configs, public docs (`app/`, `lib/`, `package.json`, `README.md`, `LICENSE`) | **PUBLIC** |
| 6 | None of the above | **Default PRIVATE** — ask the user |

### Gray zone

Files like `EDITING.md`, `.env.example`, `Makefile`, `docker-compose.yml`:
- References internal tools, AI prompts, or private infra → **PRIVATE**
- Purely for public contributors or standard build → **PUBLIC**
- Uncertain → **PRIVATE**, flag to the user

## Operating rules

### Creating files

New private file or directory → add the corresponding `rm` line to
`sync-public.yml` in the **same commit**. Never leave a private file
unprotected for even one push.

New public file → no action needed.

### Reclassifying files

Never silently move a file between private and public. Flag the change
to the user first.

### Danger signals — stop and ask

- Hardcoded API keys, tokens, or passwords in any file
- Workflow referencing `secrets.*` the public repo would not have
- Private registry URLs or internal service endpoints in configs
- Public repo already contains files that should have been stripped

## Quick reference

```
NEW FILE?
├─ AI config / agent instructions?  → PRIVATE
├─ Internal docs / dev process?     → PRIVATE
├─ The sync workflow itself?        → PRIVATE
├─ App source / public docs?        → PUBLIC
├─ Build config / manifests?        → PUBLIC
└─ Not sure?                        → PRIVATE, ask user

If PRIVATE → update sync-public.yml in same commit
If PUBLIC  → no action needed
```

## References

Read on demand — do not load all by default.

| When | Read |
|------|------|
| Writing or modifying the sync workflow | `references/workflow-template.md` |
| Setting up sync for a new project | `references/setup-guide.md` |
| Running a periodic sync audit | `references/audit.md` |
| Need private/public patterns for a specific stack | `references/project-patterns.md` |
| Need a standalone sync-guard for non-skill-aware tools | `SYNC-GUARD.md` |