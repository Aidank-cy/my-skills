# Generated Artifacts Reference

## Core scaffold

```text
project-root/
├── AGENTS.md
├── CHANGELOG.md
├── .harness/
│   ├── task-template.md
│   ├── plan-template.md
│   └── impact-map.sh
```

## Optional scaffold

```text
├── CLAUDE.md
├── .cursor/rules/
│   └── {domain}.mdc
├── .github/copilot-instructions.md
├── skills/
│   ├── using-skills/
│   │   └── SKILL.md
│   ├── versioning-and-changelog/
│   │   └── SKILL.md
│   ├── {domain-specific-skill}/
│   │   └── SKILL.md
│   └── ...
├── agents/
│   ├── code-reviewer.md
│   ├── test-engineer.md
│   └── security-auditor.md
├── hooks/
│   ├── post-file-edit.sh
│   └── pre-commit.sh
├── .github/workflows/
│   └── ai-quality-gate.yml
├── .harness/
│   ├── progress.md
│   ├── learning-log.md
│   └── anti-rationalization.md
```

## Decision rules

| Condition | Generate |
|-----------|----------|
| Any project | `CHANGELOG.md` if missing + `skills/versioning-and-changelog/` |
| Project uses Claude Code | `CLAUDE.md` |
| Project uses Cursor | `.cursor/rules/` |
| Project has more than 20 files or multiple domains | `skills/` with 2-5 domain skills |
| Project has more than 50 files or is a monorepo | `agents/` personas |
| Project has CI already | extend existing workflow |
| Project has no CI | create `.github/workflows/ai-quality-gate.yml` |
| Project touches auth, payments, or infra | stronger hooks + security reviewer |
| Project is long-running or multi-session | `.harness/progress.md` + `.harness/learning-log.md` |

## AGENTS.md template rules

Generate `AGENTS.md` with:
- 60 lines or fewer
- actual install, test, lint, build, and dev commands
- `Always`, `Ask first`, and `Never` sections
- concrete architecture boundaries
- concrete pattern references
- `[INFERRED]` tags on inferred rules

## Task template outline

```markdown
## Task: {title}

### Scope
Files to modify:
  - {path} → {change description}

Files to read (do not modify):
  - {path} → {why}

### Pattern to follow
{existing code reference}

### Acceptance criteria
1. `{test command}` passes
2. `{lint command}` passes
3. {project-specific check}

### Out of scope
{explicit non-goals}

### Assumptions
{each marked with [ASSUMPTION]}
```

## Plan template outline

```markdown
## Plan: {task title}

1. **Files to modify**: [list]
2. **Files to create**: [list]
3. **Dependencies**: [list]
4. **Verification steps**: [commands]
5. **Assumptions**: [[ASSUMPTION] items]
6. **Risk assessment**: [reversible vs risky]
```

## Impact map guidance

Generate `.harness/impact-map.sh` for the detected stack.
Examples:
- TypeScript or JavaScript: module files, dependents, tests, exports
- Python: module files, importers, tests, public API
- Rust or Go: adapt to the real tooling rather than copying JS patterns blindly

## Hooks guidance

Generate hooks from the real toolchain.
Use the principle: success is silent, failure is verbose.

Typical responsibilities:
- `hooks/post-file-edit.sh`: run typecheck and lint for touched file types
- `hooks/pre-commit.sh`: block skipped tests, hardcoded secrets, and suppression comments

## Skills guidance

Always generate a router skill when you generate a skill library.
Pick 2-5 domain skills based on the project profile.
Typical options:
- `versioning-and-changelog`
- `spec-driven-development`
- `incremental-implementation`
- `test-first`
- `code-review-checklist`
- `api-design`
- `frontend-component`
- `database-migration`
- `security-hardening`
- `documentation`

## Persona guidance

Generate personas only for larger or multi-domain projects.
Each persona should define:
- scope
- review criteria
- output format
- invoked skills
- composition rules

## CI gate guidance

If CI exists, extend it.
If not, create an AI quality gate workflow.
Typical checks:
- skipped tests
- suppression comments
- hardcoded secrets
- project-specific complexity or lint gates

## Anti-rationalization content

Generate `.harness/anti-rationalization.md` when repeated agent drift is likely.
Use concrete rebuttals for common shortcuts such as:
- "I'll add tests later"
- "This change is too small for tests"
- "I need to refactor adjacent code first"
- "I'll suppress the lint rule"
