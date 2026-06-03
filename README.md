# my-skills

User-level and project-level agent skills for harness engineering
workflows. Agent-agnostic — works with any tool that supports the
Agent Skills open standard (Codex, Claude Code, Cursor, Gemini CLI,
etc.).

## Structure

Skills are organized by activation scope:

| Directory | Scope | Installation |
|---|---|---|
| `always-on/` | User-level | Symlink to your agent's user skills dir |
| `project-pipeline/` | Project-level | Auto-linked by `bootstrap-project` into project `skills/` |
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
via symlinks into the project's `skills/` directory.

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

Symlink each always-on skill to your agent's user-level skills
directory. The path varies by agent:

| Agent | User skills directory |
|---|---|
| Codex | Check Codex docs or use a generic compatible user skills directory |
| Claude Code | Check Claude Code docs |
| Any agentskills.io compatible | Check agent docs |

```bash
# Example: symlink to your agent's user skills dir
AGENT_SKILLS_DIR="$HOME/.agents/skills"  # adjust for your agent
mkdir -p "$AGENT_SKILLS_DIR"
for skill in "$HOME/my-skills/always-on"/*/; do
  skill_name=$(basename "$skill")
  ln -sf "$skill" "$AGENT_SKILLS_DIR/$skill_name"
done
```

### Project-level (automatic)

When you say "create a project X", the bootstrap-project skill
automatically:
1. Creates `~/Projects/X/`
2. Creates `skills/` inside it
3. Symlinks all `project-pipeline/` skills into `skills/`

Then enter the project directory and tell the agent about your
project to trigger harness-init.

## Workflow

```text
Casual chat                → always-on skills stay passive
"Create project X"         → bootstrap-project activates
cd ~/Projects/X            → project-pipeline skills now available
"Add feature Y"            → prompt-gateway activates (project-level)
```
