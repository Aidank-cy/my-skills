# My Skills

A personal skill library for AI coding agents, organized by activation
scope so globally installed skills stay useful without intercepting
casual conversation.

These skills follow the open agent-skill pattern: each skill exposes a
`SKILL.md` file with optional `references/`, `examples/`, or supporting
assets loaded only when needed.

## Directory Structure

```text
my-skills/
├── always-on/
├── project-pipeline/
└── domain-skills/
```

## Skill Categories

### `always-on/`

Skills safe for permanent user-level installation. They activate on
explicit, narrow workflow triggers and must never reject or intercept
casual conversation.

Install these into `~/.codex/skills/` when you want them available in
every thread.

### `project-pipeline/`

Skills that gate input, create project scaffolds, or require project
context such as `AGENTS.md`, `.harness/`, or a git repository.

Do not install these at the user level. Install them per project only,
for example in that project's skill directory, so they activate only
while working inside an appropriate codebase.

### `domain-skills/`

Standalone topic-specific skills. Install these at the user level or
project level based on preference and how often the capability is
needed.

## Installation

Recommended user-level symlinks:

```bash
ln -s /Users/ninnnnk/my-skills/always-on/git-workflow ~/.codex/skills/git-workflow
ln -s /Users/ninnnnk/my-skills/always-on/versioning-and-changelog ~/.codex/skills/versioning-and-changelog
ln -s /Users/ninnnnk/my-skills/always-on/harness-remote-handoff ~/.codex/skills/harness-remote-handoff
ln -s /Users/ninnnnk/my-skills/always-on/skill-authoring ~/.codex/skills/skill-authoring
```

Optional domain skill symlink:

```bash
ln -s /Users/ninnnnk/my-skills/domain-skills/frontend-design-audit ~/.codex/skills/frontend-design-audit
```

Project-pipeline skills should be linked only inside the project that
needs them. For example:

```bash
mkdir -p /path/to/project/.codex/skills
ln -s /Users/ninnnnk/my-skills/project-pipeline/prompt-gateway /path/to/project/.codex/skills/prompt-gateway
```

## Skills

| Skill | Category | Purpose |
|---|---|---|
| [git-workflow](always-on/git-workflow/) | `always-on` | Standardizes branches, commits, merges, pushes, and PR flow. |
| [versioning-and-changelog](always-on/versioning-and-changelog/) | `always-on` | Maintains changelog entries, version bumps, tags, and release notes. |
| [harness-remote-handoff](always-on/harness-remote-handoff/) | `always-on` | Recovers project status after pushes, CI failures, or resumed work. |
| [skill-authoring](always-on/skill-authoring/) | `always-on` | Guides writing, reviewing, and refactoring skill content. |
| [prompt-gateway](project-pipeline/prompt-gateway/) | `project-pipeline` | Routes explicit project code changes through validation and task execution. |
| [harness-init](project-pipeline/harness-init/) | `project-pipeline` | Bootstraps a new harness-managed project. |
| [harness-engineering-transform](project-pipeline/harness-engineering-transform/) | `project-pipeline` | Adds harness engineering rules and quality gates to an existing project. |
| [sync-filter](project-pipeline/sync-filter/) | `project-pipeline` | Classifies files and maintains dev-to-public sync boundaries. |
| [frontend-design-audit](domain-skills/frontend-design-audit/) | `domain-skills` | Audits and improves frontend usability, accessibility, and visual hierarchy. |

## Adding New Skills

Place new skills by activation risk:

| Question | If yes | If no |
|---|---|---|
| Does it intercept or gate user input? | `project-pipeline/` | Continue evaluating. |
| Does it require project context such as `AGENTS.md`, `.harness/`, or git? | `project-pipeline/` | Continue evaluating. |
| Is it a standalone domain capability? | `domain-skills/` | `always-on/` |
| Could it accidentally reject casual chat? | `project-pipeline/` | `always-on/` |

Keep every `SKILL.md` under 500 lines and 3,000 words. Move detailed
guides to `references/`, reusable examples to `examples/`, and helper
scripts to `scripts/`.

## License

Personal use. Feel free to reference the structure for your own skill
libraries.
