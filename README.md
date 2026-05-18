# My Skills

A personal user-level skill library for AI coding agents.

These skills are designed to work across multiple projects as user-level configurations — they are not copied into individual project repositories. They follow the [open agent-skill standard](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices) and are compatible with Claude Code, Cursor, Codex, and other skill-aware tools.

## How it works

Every code change follows a **task-based lifecycle**: one prompt = one task = one branch.

```
User prompt ("add feature X", "fix bug Y")
  │
  ▼
prompt-gateway
  ├─ Validate prompt structure
  ├─ Decompose into task + subtasks
  ├─ git checkout -b {type}/{name} from main
  ├─ Execute subtasks one by one
  ├─ Verify all subtasks
  │
  ├─► versioning-and-changelog ── update CHANGELOG.md
  ├─► git-workflow ── commit with Conventional Commits
  │
  ├─ git merge to main
  ├─ Delete feature branch
  │
  ▼
✅ Done. On main. Ready for next task.
  │
  ▼
harness-remote-handoff ── user pushes main to remote
```

Release flow:

```
User says "release" / "cut a release"
  │
  ▼
versioning-and-changelog ── review unreleased entries
                            compute SemVer bump
                            update version files
  │
  ▼
git-workflow ── release commit + tag
  │
  ▼
harness-remote-handoff ── user pushes with --follow-tags
```

## Skills

### Harness Engineering (project lifecycle)

| Skill                                                           | What it does                                                                                                              |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| [harness-init](harness-init/)                                   | Bootstrap a new project with a harness engineering scaffold (AGENTS.md, CHANGELOG.md, .harness/, hooks, CI) from day one  |
| [harness-engineering-transform](harness-engineering-transform/) | Audit an existing codebase and retrofit harness engineering — rules, hooks, templates, and project-specific domain skills |

### Development Pipeline

| Skill                                                 | What it does                                                                                                                                                                                                     |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [prompt-gateway](prompt-gateway/)                     | Gate every code-modification prompt through structured validation, decompose into task + subtasks, orchestrate execution on a feature branch, enforce CHANGELOG + commit discipline, and auto-merge back to main |
| [versioning-and-changelog](versioning-and-changelog/) | Manage CHANGELOG.md entries after every task, compute SemVer bumps, and cut releases with proper tagging                                                                                                         |
| [git-workflow](git-workflow/)                         | Standardize the task-based branch lifecycle (branch → subtasks → commit → merge), Conventional Commits format, merge strategy, and release git mechanics                                                         |
| [harness-remote-handoff](harness-remote-handoff/)     | Bridge the gap between agent-managed local work (including auto-merge to main) and user-owned remote operations (push), with context recovery when the user returns                                              |

### Tooling

| Skill                               | What it does                                                                                                                        |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| [sync-filter](sync-filter/)         | Classify files as private or public for dev→public repo sync pipelines, ensuring harness files never leak to the public mirror      |
| [skill-authoring](skill-authoring/) | Write, review, and refactor skills following the open standard — naming, progressive disclosure, description quality, and structure |

## Task lifecycle detail

Each user prompt goes through this pipeline:

| Step        | What happens                                                                          |
| ----------- | ------------------------------------------------------------------------------------- |
| **Step 0**  | Branch state gate — ensure on main, create `{type}/{name}` branch                     |
| **Step 1**  | Classify — code change vs read-only vs release vs harness setup                       |
| **Step 2**  | Validate prompt (Tier A full spec / Tier B lightweight spec), decompose into subtasks |
| **Step 3**  | Harness integrity check — verify AGENTS.md, CHANGELOG.md, .harness/ exist             |
| **Step 4**  | Build execution plan with impact level and subtask breakdown                          |
| **Step 5**  | Execute subtasks sequentially, verify each one                                        |
| **Step 6A** | CHANGELOG update via `versioning-and-changelog`                                       |
| **Step 6B** | Rules update if needed (AGENTS.md, CLAUDE.md)                                         |
| **Step 6C** | Progress update in `.harness/progress.md`                                             |
| **Step 6D** | Conventional commit                                                                   |
| **Step 6E** | Merge to main, delete branch                                                          |

After Step 6E, the project is on main and the user can either start the next task or push to remote.

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