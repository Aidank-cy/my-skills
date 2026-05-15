# Bootstrap Layout

## Standard scaffold

```text
{project-root}/
├── AGENTS.md
├── CLAUDE.md
├── CHANGELOG.md
├── .harness/
│   ├── task-template.md
│   ├── plan-template.md
│   ├── impact-map.sh
│   ├── progress.md
│   └── anti-rationalization.md
├── skills/
│   ├── using-skills/
│   │   └── SKILL.md
│   ├── spec-driven-development/
│   │   └── SKILL.md
│   ├── incremental-implementation/
│   │   └── SKILL.md
│   └── versioning-and-changelog/
│       └── SKILL.md
├── agents/
│   └── code-reviewer.md
├── hooks/
│   ├── post-file-edit.sh
│   └── pre-commit.sh
├── .github/workflows/
│   └── ai-quality-gate.yml
└── {standard project files}
```

## Decision rules

| Project size or type | Generate |
|----------------------|----------|
| Any project | `AGENTS.md`, `CHANGELOG.md`, `.harness/`, `hooks/`, `skills/versioning-and-changelog/` |
| Small or solo | above + `spec-driven-development` and `incremental-implementation` |
| Medium or team | above + more domain skills + `agents/code-reviewer.md` |
| Has API | add `api-design/SKILL.md` |
| Has database | add `database-migration/SKILL.md` |
| Has auth or payments | add `security-hardening/SKILL.md` and security reviewer persona |
| Has frontend | add `frontend-component/SKILL.md` |
| Monorepo | add workspace-boundary rules and package-scoped impact mapping |

## Post-generation checklist

1. `chmod +x .harness/impact-map.sh hooks/post-file-edit.sh hooks/pre-commit.sh`
2. `git init` if needed
3. `git add .`
4. `git commit -m "feat: initial project scaffold with harness engineering structure"`
5. Brief the user on `AGENTS.md`, hooks, skills, `.harness/progress.md`, and the ratchet principle

## Key briefing points

- `AGENTS.md` is the highest-leverage file.
- Hooks provide deterministic enforcement.
- Skills activate on demand.
- `.harness/progress.md` stores cross-session state.
- The scaffold should evolve in response to real agent failures.
