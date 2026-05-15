# Sync Workflow Template

Reference template for `.github/workflows/sync-public.yml`.
Adapt the `rm` list and git config to your project.

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
          rm -rf CHANGELOG.md DEVLOG.md TODO.md

          # === DEV TOOLING & RULES ===
          rm -rf .project-rules .harness skills hooks

          # === PRIVATE WORKFLOWS ===
          rm -f .github/workflows/ai-quality-gate.yml
          rm -f .github/workflows/sync-public.yml

          # === GRAY ZONE (uncomment per project) ===
          # rm -f EDITING.md
          # rm -rf .vscode

      - name: Push to public repo
        env:
          TOKEN: ${{ secrets.PUBLIC_REPO_TOKEN }}
        run: |
          git config user.name "your-username"
          git config user.email "your-username@users.noreply.github.com"
          git add -A
          git commit -m "sync: update from dev" --allow-empty
          git remote add public https://your-username:${TOKEN}@github.com/your-username/your-public-repo.git
          git push public HEAD:main --force
```

## Key Points

- **`fetch-depth: 0`** — Full history so force-push works cleanly.
- **`persist-credentials: false`** — Prevents default GITHUB_TOKEN from
  interfering with the custom remote.
- **`--allow-empty`** — Commit succeeds even if nothing changed after filtering.
- **`--force`** — Public repo is always a clean mirror, never merged.
- **Group deletions by category** with comments for maintainability.
