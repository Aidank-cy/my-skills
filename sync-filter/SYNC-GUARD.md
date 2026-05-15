# Public Sync Guard — Codex Instructions

> This file governs the dev → public repository sync boundary.
> Read this BEFORE creating, moving, or deleting any file.

## Context

This private repo syncs to a public repo via `.github/workflows/sync-public.yml`.
The workflow strips private files then force-pushes the clean result. **You must
keep the workflow in sync with reality.**

## Classification — Decide in This Order

1. **AI agent configs** → PRIVATE
   `AGENTS.md`, `CLAUDE.md`, `.cursor/`, `.github/copilot-instructions.md`, `skills/`, `hooks/`

2. **Internal process docs** → PRIVATE
   `.project-rules/`, `.harness/`, `CHANGELOG.md`, `DEVLOG.md`, `TODO.md`

3. **The sync workflow + quality gates** → PRIVATE
   `.github/workflows/sync-public.yml`, `.github/workflows/ai-quality-gate.yml`

4. **App source, configs, public docs** → PUBLIC
   `app/`, `components/`, `lib/`, `config/`, `package.json`, `README.md`, `LICENSE`, build configs

5. **Everything else** → Ask me. Default to PRIVATE if I am unreachable.

## Rules

- **New private file or directory?** Add the corresponding `rm` line to
  `sync-public.yml` in the SAME commit. Never leave a private file
  unprotected for even one push.

- **Reclassifying a file?** Tell me first. Never silently move something
  from private to public or vice versa.

- **Gray zone files** (e.g., `EDITING.md`, `.env.example`, `Makefile`):
  If it references internal tools, AI prompts, or private infrastructure
  → PRIVATE. If it is purely for public contributors → PUBLIC.

- **When in doubt, keep it private.** Easy to publish later, impossible
  to un-publish.

## Audit (run every ~20 commits or when asked)

```bash
# Files marked for removal
grep -oP '(?<=rm -rf |rm -f ).+' .github/workflows/sync-public.yml \
  | tr ' ' '\n' | sort > /tmp/private.txt

# All repo files
find . -not -path './.git/*' -not -path './node_modules/*' \
  -type f | sed 's|^\./||' | sort > /tmp/all.txt

# Unclassified files (verify each is intentionally public)
comm -23 /tmp/all.txt /tmp/private.txt
```

Report any unclassified files to me.

## Danger — Stop and Ask If You See

- Hardcoded API keys, tokens, or passwords in any file
- A workflow referencing `secrets.*` the public repo would not have
- Private registry URLs or internal service endpoints in config files
- The public repo already contains files that should have been stripped
