# Setup Guide — New Dev → Public Pipeline

## Step 1: Inventory

```bash
find . -not -path './.git/*' -not -path './node_modules/*' \
  -type f | head -100
```

## Step 2: Classify

Walk through the classification decision tree in SKILL.md for each
top-level file/directory. Create a table:

```
PUBLIC:  app/ components/ lib/ config/ package.json README.md LICENSE ...
PRIVATE: AGENTS.md .project-rules/ .github/workflows/sync-public.yml ...
REVIEW:  EDITING.md .env.example ...
```

## Step 3: Create the workflow

Copy the template from `references/workflow-template.md`. Fill in:
- Your GitHub username (2 places: `user.name` and remote URL)
- Your public repo name in the remote URL
- The full `rm` list from your classification

## Step 4: Set up the secret

In the private repo → Settings → Secrets and variables → Actions:
- Name: `PUBLIC_REPO_TOKEN`
- Value: A GitHub Personal Access Token with `repo` scope for the public repo

## Step 5: Test

Push to main. Verify on the public repo:
- All private files are absent
- All public files are present and correct
- Commit history shows a single "sync: update from dev" commit
