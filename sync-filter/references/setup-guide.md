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
PUBLIC:  app/ components/ lib/ config/ package.json README.md LICENSE
         .github/workflows/auto-close-pr.yml
PRIVATE: AGENTS.md .project-rules/ .github/workflows/sync-public.yml
REVIEW:  .env.example Makefile
```

## Step 3: Create the PAT

### Option A: Classic token (recommended)

GitHub avatar → Settings → Developer settings → Personal access tokens
→ Tokens (classic) → Generate new token:

- Note: descriptive name (e.g. `portfolio-sync`)
- Expiration: choose an appropriate period
- Scopes: check **`repo`** (top-level, selects all sub-scopes)
  AND **`workflow`** (required if syncing any `.github/workflows/` files)

Click Generate token. Copy using the **copy button**, not manual
text selection.

### Option B: Fine-grained token

GitHub avatar → Settings → Developer settings → Personal access tokens
→ Fine-grained tokens → Generate new token:

- Token name: descriptive name
- Resource owner: your username
- Repository access: **Only select repositories** → select the
  **public** repo only
- Permissions → Repository permissions:
  - **Contents**: Read and write
  - **Metadata**: Read-only (auto-selected)
  - **Workflows**: Read and write

Generate and copy with the copy button.

### Verify the token locally

Before saving as a secret, confirm the token works:

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer ghp_xxxxx" \
  https://api.github.com/repos/OWNER/PUBLIC-REPO
```

Must return `200`. If `401`, the token is invalid or was copied
incorrectly. Regenerate and try again.

**Never paste a token into chat, issues, or any shared context.**

## Step 4: Store the secret

In the **private** repo → Settings → Secrets and variables → Actions
→ **Repository secrets** (not Variables) → New repository secret:

- Name: `{TARGET_REPO_SHORT}_PAT` (e.g. `PORTFOLIO_PAT`)
- Value: paste the token

Naming convention — use the target public repo's short name so
different projects have distinct, identifiable secrets:

| Private repo | Secret name | Target |
|---|---|---|
| `portfolio-dev` | `PORTFOLIO_PAT` | `portfolio` |
| `project-b-dev` | `PROJECT_B_PAT` | `project-b` |

## Step 5: Create the workflow

Copy the sync template from `references/workflow-template.md`. Fill in:

- Your GitHub username (in `git config user.name` is `github-actions[bot]`,
  but in `~/.git-credentials` use your actual username)
- Your public repo name in the remote URL
- The secret name in `${{ secrets.PORTFOLIO_PAT }}`
- The full `rm` list from your classification

Also copy the auto-close-pr.yml template. Replace `your-username` in the
`allowed` array with your actual GitHub username.

## Step 6: Configure branch protection on the public repo

Public repo → Settings → Rules → Rulesets → New branch ruleset:

- Name: `protect-main`
- Enforcement: **Active**
- Bypass list: add **Repository admin**
- Target branches: Add target → Include by pattern → `main`
- Rules to enable:
  - **Restrict updates** (blocks direct push from non-bypass users)
  - **Restrict deletions**
  - **Block force pushes** (bypass users can still force push)

Save. This ensures only your PAT (which maps to your admin account)
can push to main. Everyone else is blocked.

## Step 7: Test

Push a change to the private repo's main branch. Verify:

1. The Action runs successfully (green check)
2. On the public repo:
   - All private files are absent
   - All public files are present and correct
   - `auto-close-pr.yml` exists in `.github/workflows/`
3. Commit author shows `github-actions[bot]`

### If the Action fails

Read `references/troubleshooting.md` for common error patterns and fixes.
