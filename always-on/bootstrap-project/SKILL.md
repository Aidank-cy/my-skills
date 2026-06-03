---
name: bootstrap-project
description: >
  This skill should be used when the user asks to "create a project",
  "new project", "start a project", "bootstrap a project", "init a
  project folder", or says a project name and wants to begin working
  on it. Creates a project directory under ~/Projects/, sets up the
  project-level skills/ directory, and symlinks
  project-pipeline skills from the user's my-skills repository.
  Does NOT initialize the tech stack or run harness-init — the user
  will do that as a separate step after entering the project directory.
  Do NOT trigger for casual conversation, general questions,
  greetings, or topics unrelated to project creation.
---

# Bootstrap Project

Create a new project directory with project-pipeline skills linked.

## Activation guard

This skill activates only when the user explicitly asks to create,
start, or bootstrap a new project. General conversation about
projects, questions about existing projects, or discussion of
project ideas without a creation request do not trigger this skill.

## What this skill does

1. Create `~/Projects/{project-name}/`
2. Create `skills/` inside it
3. Symlink all project-pipeline skills from `$HOME/my-skills/`
4. Report what was created

That is the entire scope. No tech stack init, no harness scaffold,
no git init. The user handles those next.

## Workflow

### Step 1: Extract project name

Derive a kebab-case directory name from the user's request.

Examples:
- "create a project called sigma" → `sigma`
- "new project: my-portfolio" → `my-portfolio`
- "start a project for the trading bot" → `trading-bot`

If the name is ambiguous, ask. Do not guess.

### Step 2: Validate

```text
□ Does ~/Projects/{project-name}/ already exist?
  → YES: warn the user and stop. Do not overwrite.
  → NO: proceed.

□ Does $HOME/my-skills/project-pipeline/ exist?
  → YES: proceed.
  → NO: warn that project-pipeline skills directory was not found.
        The user may need to reorganize my-skills first.
```

### Step 3: Create directory and symlink skills

```bash
# Create project directory
mkdir -p "$HOME/Projects/{project-name}"

# Create project-level skills directory
mkdir -p "$HOME/Projects/{project-name}/skills"

# Symlink each project-pipeline skill
for skill in "$HOME/my-skills/project-pipeline"/*/; do
  skill_name=$(basename "$skill")
  ln -s "$skill" "$HOME/Projects/{project-name}/skills/$skill_name"
done
```

All paths use `$HOME` so symlinks remain valid across environments.

### Step 4: Verify and report

```bash
ls -la "$HOME/Projects/{project-name}/skills/"
```

Report to the user:

```text
✅ Project "{project-name}" created at ~/Projects/{project-name}/

Linked project-pipeline skills:
  prompt-gateway     → ~/my-skills/project-pipeline/prompt-gateway
  harness-init       → ~/my-skills/project-pipeline/harness-init
  harness-engineering-transform → ...
  sync-filter        → ...

Next steps:
  cd ~/Projects/{project-name}
  Then tell me about your project and I will run harness-init.
```

## Skills that get symlinked

All directories under `$HOME/my-skills/project-pipeline/`.
If new skills are added there, the `for skill in ...` loop picks
them up automatically.

| Skill | Purpose |
|---|---|
| prompt-gateway | Task pipeline for code modifications |
| harness-init | Harness scaffold generator |
| harness-engineering-transform | Convert existing project to harness |
| sync-filter | Dev-to-public repo sync |

## What this skill does NOT do

- Initialize a tech stack (`npm init`, `cargo init`, etc.)
- Run harness-init or generate AGENTS.md
- Create a git repository
- Install dependencies

The user owns all of these as a deliberate next step.

## Anti-rationalization

- Do not run harness-init automatically
- Do not create files beyond the directory and symlinks
- Do not assume a tech stack
- Do not skip validation even if the user "seems sure"
