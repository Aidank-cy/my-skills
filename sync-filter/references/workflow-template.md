# Sync Workflow Template

Reference template for `.github/workflows/sync-public.yml`.
Adapt the `rm` list, secret name, and repo URLs to your project.

## Sync workflow

```yaml
name: Sync to public repo

on:
  push:
    branches: [main]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false

      - name: Remove private files
        run: |
          # === AI AGENT CONFIGS ===
          rm -rf AGENTS.md CLAUDE.md
          rm -rf .cursor .github/copilot-instructions.md

          # === INTERNAL DOCS ===
          rm -rf CHANGELOG.md DEVLOG.md TODO.md EDITING.md

          # === DEV TOOLING & RULES ===
          rm -rf .project-rules .harness skills hooks

          # === PRIVATE WORKFLOWS ===
          rm -f .github/workflows/ai-quality-gate.yml
          rm -f .github/workflows/sync-public.yml

          # === GRAY ZONE (uncomment per project) ===
          # rm -f .env.example
          # rm -rf .vscode

      - name: Push to public repo
        env:
          TOKEN: ${{ secrets.PORTFOLIO_PAT }}
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

          git config credential.helper store
          echo "https://your-username:${TOKEN}@github.com" > ~/.git-credentials

          git add -A

          if git diff --cached --quiet; then
            echo "No changes to sync, skipping."
            exit 0
          fi

          git commit -m "sync: update from dev ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
          git remote add public https://github.com/your-username/your-public-repo.git
          git push public HEAD:main --force
```

## Auto-close external PRs

Place in the private repo. Classify as **PUBLIC** (do NOT add to the
`rm` list) so it syncs to the public repo where it runs.

```yaml
# .github/workflows/auto-close-pr.yml
name: Auto Close External PRs

on:
  pull_request_target:
    types: [opened, reopened]

jobs:
  close:
    runs-on: ubuntu-latest
    steps:
      - name: Close external PR
        uses: actions/github-script@v7
        with:
          script: |
            const pr = context.payload.pull_request;
            const allowed = ['your-username', 'github-actions[bot]'];

            if (allowed.includes(pr.user.login)) {
              console.log(`PR by ${pr.user.login} is allowed, skipping.`);
              return;
            }

            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: pr.number,
              body: [
                '⚠️ This repository is automatically synced from a private dev repo.',
                '',
                'Direct pull requests are not accepted here.',
                'If you have suggestions or found a bug, please [open an issue](../../issues/new) instead.',
                '',
                'Thank you for your interest!'
              ].join('\n')
            });

            await github.rest.pulls.update({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: pr.number,
              state: 'closed'
            });

            console.log(`Closed PR #${pr.number} by ${pr.user.login}`);
```

## Debug step (temporary)

Insert before the push step when diagnosing authentication failures.
Remove after the issue is resolved.

```yaml
      - name: Debug auth
        env:
          TOKEN: ${{ secrets.PORTFOLIO_PAT }}
        run: |
          echo "Token length: ${#TOKEN}"
          echo "Token prefix: ${TOKEN:0:4}"
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
            -H "Authorization: Bearer ${TOKEN}" \
            https://api.github.com/repos/your-username/your-public-repo)
          echo "API response: ${STATUS}"
```

## Key points

- **`fetch-depth: 0`** — full history so force-push works cleanly.
- **`persist-credentials: false`** — prevents default GITHUB_TOKEN from
  interfering with the custom remote.
- **Credential helper** — token stored in `~/.git-credentials`, not
  embedded in the remote URL. Avoids URL parsing issues and reduces
  token exposure in error logs.
- **`github-actions[bot]`** as committer — distinguishes automated syncs
  from manual commits in the public repo history.
- **`git diff --cached --quiet`** — skip commit and push when nothing
  changed, instead of creating empty commits with `--allow-empty`.
- **Timestamp in commit message** — aids traceability for when a sync ran.
- **`--force`** — public repo is always a clean mirror, never merged.
- **Group deletions by category** with comments for maintainability.
- **`pull_request_target`** for auto-close — triggers on fork PRs and
  runs the repo owner's version of the workflow, not the PR author's.
