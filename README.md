# my-skills

User-level and project-level Codex skills for harness engineering
workflows.

## Structure

Skills are organized by activation scope:

| Directory | Scope | Installation |
|---|---|---|
| `always-on/` | User-level | Symlink to `~/.codex/skills/` |
| `project-pipeline/` | Project-level | Auto-linked by `bootstrap-project` |
| `domain-skills/` | Either | Install where needed |

### always-on/

Safe for permanent user-level installation. Never reject casual
conversation.

| Skill | Purpose |
|---|---|
| bootstrap-project | Create project dir + symlink pipeline skills |
| git-workflow | Branch naming, commit format, merge strategy |
| versioning-and-changelog | CHANGELOG, SemVer, release management |
| harness-remote-handoff | Context recovery after remote ops or breaks |
| skill-authoring | Write, review, and refactor agent skills |

### project-pipeline/

Require project context. Installed per-project by bootstrap-project
via symlinks into `.codex/skills/`.

| Skill | Purpose |
|---|---|
| prompt-gateway | Task pipeline for code modifications |
| harness-init | New project harness scaffold |
| harness-engineering-transform | Add harness to existing projects |
| sync-filter | Dev-to-public repo sync |

### domain-skills/

Standalone capabilities. Install at either level.

| Skill | Purpose |
|---|---|
| frontend-design-audit | UX audit against 15 usability principles |

## Installation

### User-level (always-on skills)

```bash
# Symlink each always-on skill to Codex user skills
for skill in "$HOME/Projects/my-skills/always-on"/*/; do
  skill_name=$(basename "$skill")
  ln -sf "$skill" "$HOME/.codex/skills/$skill_name"
done
```

### Project-level (automatic)

When you say "create a project X", the bootstrap-project skill
automatically:
1. Creates `~/Projects/X/`
2. Creates `.codex/skills/`
3. Symlinks all `project-pipeline/` skills into it

Then enter the project directory and tell Codex about your project
to trigger harness-init.

## Workflow

```text
Casual chat with Codex     → always-on skills stay passive
"Create project X"         → bootstrap-project activates
cd ~/Projects/X            → project-pipeline skills now available
"Add feature Y"            → prompt-gateway activates (project-level)
```
