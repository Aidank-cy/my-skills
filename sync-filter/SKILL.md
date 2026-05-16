---
name: sync-filter
description: >
  This skill should be used when the user asks to "set up dev-to-public
  sync", "add a file to the sync workflow", "classify a file as private
  or public", "create a sync PAT", "configure branch protection for sync",
  "debug a sync push failure", "audit the sync pipeline", or works on a
  project with a private dev repo (named with a -dev suffix) that syncs
  to a public repo via GitHub Actions. Also trigger when encountering
  files like AGENTS.md, CLAUDE.md, .project-rules/, sync-public.yml,
  auto-close-pr.yml, or any dev→public pipeline.
---

# Sync filter

Manage the boundary between a private dev repo and its public mirror.
The sync workflow strips private files then force-pushes the clean
result. Keep the workflow in sync with reality at all times.

## Naming convention

Private repo = public repo name + `-dev` suffix.

```
Aidank-portfolio      ← public
Aidank-portfolio-dev  ← private (source of truth)
```

## Classification decision tree

Work top-down. Stop at the first match.

| # | Condition | Action |
|---|-----------|--------|
| 1 | AI agent config (`AGENTS.md`, `CLAUDE.md`, `.cursor/`, `copilot-instructions.md`, `skills/`, `hooks/`) | **PRIVATE** |
| 2 | Internal process docs (`.project-rules/`, `.harness/`, `CHANGELOG.md`, `TODO.md`, `EDITING.md`) | **PRIVATE** |
| 3 | Sync workflow or private-only CI (`sync-public.yml`, `ai-quality-gate.yml`) | **PRIVATE** |
| 4 | Contains secrets, tokens, private registry URLs, or internal endpoints | **PRIVATE** |
| 5 | Public-facing protection workflows (`auto-close-pr.yml`) | **PUBLIC** — must reach the public repo to function |
| 6 | App source, build configs, public docs (`app/`, `lib/`, `package.json`, `README.md`, `LICENSE`) | **PUBLIC** |
| 7 | None of the above | **Default PRIVATE** — ask the user |

### Gray zone

Files like `.env.example`, `Makefile`, `docker-compose.yml`:
- References internal tools, AI prompts, or private infra → **PRIVATE**
- Purely for public contributors or standard build → **PUBLIC**
- Uncertain → **PRIVATE**, flag to the user

## Token authentication

### Secret naming convention

Format: `{TARGET_REPO_SHORT}_PAT` — uppercase, underscores, descriptive.

```
PORTFOLIO_PAT       ← pushes to Aidank-portfolio
PROJECT_B_PAT       ← pushes to project-B
```

Store in: private repo → Settings → Secrets and variables → Actions →
**Repository secrets** (not Variables — Variables are plaintext).

### Token types

**Classic token (recommended for simplicity):**
- Scopes required: `repo` + `workflow`
- `workflow` scope is mandatory when syncing any `.github/workflows/*.yml`
  file — GitHub isolates workflow file permissions from content permissions

**Fine-grained token:**
- Repository access: select only the target public repo
- Permissions: Contents (Read & write), Metadata (Read-only),
  Workflows (Read & write)

### Credential handling in the workflow

Never embed the token directly in the git remote URL. Use the credential
helper pattern:

```yaml
env:
  TOKEN: ${{ secrets.PORTFOLIO_PAT }}
run: |
  git config credential.helper store
  echo "https://username:${TOKEN}@github.com" > ~/.git-credentials
  git remote add public https://github.com/owner/public-repo.git
  git push public HEAD:main --force
```

### Verify before storing

Always test a new token locally before saving it as a secret:

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer ghp_xxxxx" \
  https://api.github.com/repos/OWNER/PUBLIC-REPO
# Must return 200
```

Copy the token using the copy button on GitHub, not manual text selection.
Whitespace or missing characters cause silent 401 failures.

## Branch protection (public repo)

Use **Rulesets** (Settings → Rules → Rulesets) on the public repo:

1. Create a new branch ruleset targeting `main`
2. Bypass list: add **Repository admin**
3. Enable rules: **Restrict updates**, **Restrict deletions**,
   **Block force pushes**
4. Enforcement: **Active**

This blocks all direct pushes except from the admin (your PAT).

### Auto-close external PRs

Add `auto-close-pr.yml` to the private repo (classify as **PUBLIC** so
it syncs). Uses `pull_request_target` to trigger on fork PRs safely.
See `references/workflow-template.md` for the template.

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
- Token length is 0 in Actions (secret name mismatch)

## Quick reference

```
NEW FILE?
├─ AI config / agent instructions?  → PRIVATE
├─ Internal docs / dev process?     → PRIVATE
├─ The sync workflow itself?        → PRIVATE
├─ Public protection (auto-close)?  → PUBLIC
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
| Debugging a sync push failure | `references/troubleshooting.md` |
| Need a standalone sync-guard for non-skill-aware tools | `SYNC-GUARD.md` |
