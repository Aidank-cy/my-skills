# Harness Component Catalog

Reference for all harness components and when to use each. The SKILL.md references this file when deciding which components to generate for a project.

---

## Component decision matrix

| Component | Complexity threshold | Value | Effort |
|-----------|---------------------|-------|--------|
| AGENTS.md | Any project | Highest | Low |
| Lint rules (error not warn) | Any project with linter | High | Low |
| Task template | Any project | High | Low |
| Impact map script | >10 source files | High | Medium |
| Planning gate template | Any multi-step task | High | Low |
| Post-edit hooks | Any project with lint/typecheck | High | Medium |
| Pre-commit hooks | Any project | Medium | Low |
| Skills folder | >20 files or multiple domains | Medium | Medium |
| Subagent personas | >50 files or team project | Medium | Medium |
| CI quality gate | Project with CI already | Medium | Medium |
| Anti-rationalization table | Long-running / autonomous work | Medium | Low |
| Progress / handoff files | Multi-session work | Medium | Low |
| CLAUDE.md (extra) | Claude Code users | Low | Low |
| .cursor/rules/ | Cursor users | Low | Low |

---

## AGENTS.md — anatomy of a good rule

### Good rules (concrete, actionable, traceable)

```
- Use `pnpm` not `npm`. Our lockfile is pnpm-lock.yaml; npm will generate a conflicting package-lock.json.
- Log with `logger.info({event: 'name', ...data})` not `console.log`. Our log pipeline parses structured JSON.
- New API routes go in `src/routes/{resource}/` following the pattern in `src/routes/users/index.ts`.
- After every edit, run `pnpm lint && pnpm typecheck`. Fix before proceeding.
```

### Bad rules (vague, unenforceable, noise)

```
- Write clean code.
- Follow best practices.
- Be careful with security.
- Make sure the code is well-tested.
```

### The three-tier boundary pattern

**Always (do this every time, no exceptions):**
- Log all API calls with request ID
- Use UTC for all timestamps
- Run the test suite before declaring done

**Ask first (check with human before proceeding):**
- Adding a new dependency to package.json
- Creating a new database migration
- Changing retry intervals or timeout values
- Modifying any file in `infrastructure/`

**Never (hard prohibitions, deterministically enforced where possible):**
- Send emails/notifications without verified opt-in
- Modify the unsubscribe flow
- Delete or skip existing tests
- Hardcode secrets or connection strings
- Use `eval()`, `exec()`, or dynamic code execution
- Push directly to main/master

---

## Skills — anatomy

### Frontmatter (always required)
```yaml
---
name: skill-name
description: "Trigger description. Be specific about WHEN to use."
---
```

### Recommended sections

1. **Overview** — what this skill ensures (2-3 sentences)
2. **Triggering conditions** — when the agent should activate this
3. **Process** — numbered steps with concrete actions
4. **Anti-rationalization table** — agent excuses and rebuttals
5. **Red flags** — patterns indicating the agent went off-track
6. **Verification** — concrete commands proving the skill was followed

### Progressive disclosure

The meta-skill (`using-skills/SKILL.md`) is loaded at session start. It acts as a router — listing each skill with a one-line description and trigger condition. Individual skills are only loaded when the task matches their trigger.

This matters because every token in context degrades performance. A 20-skill library in a 5K-token slot works only with progressive disclosure.

---

## Hooks — enforcement patterns

### Lifecycle events (Claude Code)

| Event | Hook file | Use case |
|-------|-----------|----------|
| After file edit | `post-file-edit.sh` | Lint, typecheck, format |
| Before tool call | `pre-tool-call.sh` | Block dangerous commands |
| Before commit | `pre-commit.sh` | Block test suppression, secret leaks |
| Session start | `on-session-start.sh` | Load progress, check environment |

### Design principle
- **Success = silent.** If the check passes, agent gets no output.
- **Failure = verbose + actionable.** Error message includes what went wrong AND how to fix it. The message itself becomes a prompt.
- **All rules set to error, not warn.** Warnings train the agent to ignore output.
- **Disable inline suppression.** Block `eslint-disable`, `# noqa`, `@ts-ignore` — agents use these to suppress violations rather than fixing them.

---

## Persistence files — cross-session state

### progress.md (agent reads and writes)
```markdown
## Session progress

### Completed
- [x] Set up JWT middleware (commit abc123)
- [x] Migrate user routes to JWT auth

### In progress
- [ ] Update admin routes — blocked on permission model decision

### Decisions made
- Using PyJWT 2.x with HS256 (same as existing api_keys module)
- JWT secrets from env var JWT_SECRET

### Known issues
- test_admin_access flaky — intermittent timeout, not related to JWT migration

### Next session should
1. Resolve permission model for admin routes (ask user)
2. Update remaining route files
3. Run full integration test suite
```

### Handoff file (for context resets)
When context window approaches capacity, the harness tears the session down and rebuilds from this file. Structure:

```markdown
## Handoff brief

### Original task
{1-2 sentence description of the overall goal}

### What's been done
{Bullet list of completed work with commit hashes}

### Current state
{What the codebase looks like right now — which files changed, what tests pass}

### What's left
{Remaining work, in priority order}

### Critical context
{Any decisions, constraints, or gotchas the next session MUST know}
```

This is closer to onboarding a new engineer than to "memory" — give the next session exactly what it needs to be productive, nothing more.
