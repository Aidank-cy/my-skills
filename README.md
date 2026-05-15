# My Skills

A personal user-level skill library for AI coding agents.

These skills are designed to work across multiple projects as user-level configurations — they are not copied into individual project repositories. They follow the [open agent-skill standard](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices) and are compatible with Claude Code, Cursor, Codex, and other skill-aware tools.

## Skills

### Harness Engineering (project lifecycle)

| Skill                                                           | What it does                                                                                                              |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| [harness-init](harness-init/)                                   | Bootstrap a new project with a harness engineering scaffold (AGENTS.md, CHANGELOG.md, .harness/, hooks, CI) from day one  |
| [harness-engineering-transform](harness-engineering-transform/) | Audit an existing codebase and retrofit harness engineering — rules, hooks, templates, and project-specific domain skills |

### Development Pipeline

| Skill                                                 | What it does                                                                                                                                                                   |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [prompt-gateway](prompt-gateway/)                     | Gate every code-modification task through structured validation (Tier A full spec / Tier B lightweight spec), orchestrate execution, and enforce CHANGELOG + commit discipline |
| [versioning-and-changelog](versioning-and-changelog/) | Manage CHANGELOG.md entries after every change, compute SemVer bumps, and cut releases with proper tagging                                                                     |
| [git-workflow](git-workflow/)                         | Standardize branch naming, Conventional Commits format, PR conventions, merge strategy, and release git mechanics                                                              |
| [harness-remote-handoff](harness-remote-handoff/)     | Bridge the gap between agent-managed local commits and user-owned remote operations (push, PR, merge), with context recovery when the user returns                             |

### Tooling

| Skill                               | What it does                                                                                                                        |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| [sync-filter](sync-filter/)         | Classify files as private or public for dev→public repo sync pipelines, ensuring harness files never leak to the public mirror      |
| [skill-authoring](skill-authoring/) | Write, review, and refactor skills following the open standard — naming, progressive disclosure, description quality, and structure |

## How they work together

```
User request
  │
  ▼
prompt-gateway ─── validates prompt structure
  │                 checks harness integrity
  │                 builds execution plan
  │                 executes and verifies
  │
  ├─► versioning-and-changelog ─── updates CHANGELOG.md
  │
  ├─► git-workflow ─── commit format, branch conventions
  │
  ▼
Local commit (agent boundary)
  │
  ▼
harness-remote-handoff ─── guides user through push / PR / merge
                           recovers context on return
```

Release flow:

```
User says "发版" / "release"
  │
  ▼
versioning-and-changelog ─── reviews unreleased entries
                             computes SemVer bump
                             updates version files
  │
  ▼
git-workflow ─── release commit + tag
  │
  ▼
harness-remote-handoff ─── user pushes with --follow-tags
```

## Skill anatomy

Every skill follows the same structure:

```
skill-name/
├── SKILL.md          ← core instructions (loaded when triggered)
└── references/       ← detailed docs (loaded on demand)
```

`SKILL.md` stays under 500 lines. Detailed templates, examples, and edge cases go in `references/`. This keeps context usage efficient — only what's needed gets loaded.

## User-level vs project-level

These skills live at the **user level** and are always available across all projects. They do not get duplicated into any project's `skills/` directory.

A project's own `skills/` directory (if it has one) is reserved for **domain-specific skills** unique to that codebase — things like API routing conventions, database migration patterns, or frontend component guidelines.

The pipeline skills in this repo (`prompt-gateway`, `versioning-and-changelog`, `git-workflow`, etc.) handle the universal workflow that applies to every project.

## Adding new skills

Follow the [skill-authoring](skill-authoring/) guide. The short version:

1. Create `skill-name/SKILL.md` with YAML frontmatter (`name` + `description`)
2. Use third-person trigger descriptions: *"This skill should be used when..."*
3. Write the body in imperative form, under 500 lines
4. Move detailed content to `references/`
5. Keep one level of references only (no nesting)

## License

Personal use. Feel free to reference the structure for your own skill libraries.