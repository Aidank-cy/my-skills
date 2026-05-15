# Branching and PR Reference

Detailed conventions for branch management, PR workflow, and merge
strategy in a harness-managed project.

---

## Branch naming examples

### Good

```
feat/add-dark-mode
feat/42-user-profile-page
fix/auth-redirect-loop
fix/87-memory-leak-websocket
refactor/extract-auth-middleware
docs/update-api-reference
chore/upgrade-vitest-v2
test/add-e2e-login-flow
release/v2.0.0
```

### Bad

```
feature/addDarkMode          # camelCase, wrong prefix
my-fix                       # no type prefix
bugfix/stuff                 # vague, non-standard prefix
feat/add-new-dark-mode-toggle-to-the-settings-page-with-system-preference  # too long
main-backup                  # meaningless
```

---

## Branch protection rules (recommended)

Configure these on the `main` branch in GitHub:

| Rule | Setting |
|------|---------|
| Require PR before merging | Yes |
| Require approvals | 1 minimum |
| Require status checks to pass | Yes (lint, test, typecheck) |
| Require branches to be up to date | Yes |
| Require linear history | Yes (enforces rebase or squash) |
| Allow force pushes | No |
| Allow deletions | No |

---

## PR template

Save as `.github/pull_request_template.md`:

```markdown
## Summary

<!-- What changed and why? Link to the issue or spec. -->

Closes #

## Changes

<!-- List the key changes. One bullet per logical change. -->

-

## Changelog entries

<!-- Copy the entries you added to CHANGELOG.md -->

###

-

## Checklist

- [ ] Branch is rebased on latest `main`
- [ ] All tests pass locally
- [ ] Lint and typecheck pass
- [ ] CHANGELOG.md updated under `[Unreleased]`
- [ ] No unrelated changes included
- [ ] Commit messages follow Conventional Commits
```

---

## PR review guidelines

### As author

- Keep PRs small: under 400 lines changed when possible.
- Split large features into stacked PRs when practical.
- Respond to review comments within 24 hours.
- Resolve conversations after addressing feedback.
- Re-request review after making changes.

### As reviewer

- Review within 24 hours of request.
- Focus on correctness, clarity, and adherence to AGENTS.md rules.
- Check that CHANGELOG entries match the actual changes.
- Verify commit messages follow Conventional Commits.
- Approve only when all checklist items are met.

---

## Merge strategy decision tree

```
Is this a feature branch with a single logical change?
├── YES → Squash merge
│         (one clean commit on main)
│
Is this a feature branch with multiple meaningful commits?
├── YES → Rebase and merge
│         (preserve individual commit history on main)
│
Is this a release branch?
├── YES → Regular merge commit
│         (preserve release history)
│
Is this a hotfix?
├── YES → Squash merge
│         (one fix commit on main)
│
Is this a long-running branch with stacked dependencies?
└── YES → Rebase and merge
          (preserve individual commits)
```

### How to tell single vs multiple

If the branch has one `prompt-gateway` Step 5→6D cycle, it is single.
If it has 2+ cycles (each with its own CHANGELOG entry and commit),
it is multiple. When in doubt, check `git log --oneline` on the branch:
meaningful distinct messages = rebase-and-merge; WIP/fixup messages
= squash.

### Squash merge message format

When GitHub squash-merges a PR, set the commit message to match
Conventional Commits:

```
feat: add dark mode toggle (#14)

Add dark mode toggle to settings page with system preference
fallback. Preference persists via localStorage.

Closes #14
```

Do not accept the default GitHub format that lists all intermediate
commit messages.

---

## Rebase workflow (detailed)

### Simple rebase

```bash
git fetch origin
git rebase origin/main
# Resolve conflicts if any, then:
git push --force-with-lease origin feat/my-branch
```

Always use `--force-with-lease` instead of `--force` to prevent
overwriting others' work.

### Interactive rebase (cleanup before PR)

```bash
git rebase -i origin/main
```

In the editor:

```
pick abc1234 feat: add dark mode context
squash def5678 wip: fix token reference
squash ghi9012 fix lint errors
pick jkl3456 test: add dark mode toggle tests
```

Result: two clean commits instead of four messy ones.

### When NOT to rebase

- On a shared branch with other contributors actively pushing.
- On `main` — never rebase main.
- After a PR is already in review — use additional commits instead,
  then squash on merge.

---

## Stacked PRs

For large features that benefit from incremental review:

```
main
 └── feat/auth-foundation      (PR #1: auth context + middleware)
      └── feat/auth-login      (PR #2: login page, depends on #1)
           └── feat/auth-signup (PR #3: signup page, depends on #2)
```

Rules:
- Each PR must independently pass all checks.
- Merge bottom-up: #1 first, then rebase #2 on main, then #3.
- Each PR gets its own CHANGELOG entries.
- Keep the stack shallow: max 3 deep.

---

## Git hooks (recommended)

### pre-commit

```bash
#!/usr/bin/env bash
# Run lint and typecheck before allowing commit
set -e

echo "Running lint..."
pnpm lint --quiet

echo "Running typecheck..."
pnpm typecheck

echo "Pre-commit checks passed."
```

### commit-msg

```bash
#!/usr/bin/env bash
# Validate conventional commit format
COMMIT_MSG=$(cat "$1")
PATTERN="^(feat|fix|refactor|docs|test|chore|perf|ci|build|style|revert)(\(.+\))?(!)?: .{1,72}$"

if ! echo "$COMMIT_MSG" | head -1 | grep -qE "$PATTERN"; then
  echo "ERROR: Commit message does not follow Conventional Commits."
  echo "Format: {type}[(scope)]: {subject}"
  echo "Example: feat(auth): add JWT refresh"
  exit 1
fi
```

### pre-push

```bash
#!/usr/bin/env bash
# Verify tests pass before pushing
set -e

echo "Running tests before push..."
pnpm test --run

echo "Pre-push checks passed."
```

Install hooks:

```bash
chmod +x hooks/pre-commit hooks/commit-msg hooks/pre-push
git config core.hooksPath hooks/
```

---

## Common git operations quick reference

### Undo last commit (keep changes)

```bash
git reset --soft HEAD~1
```

### Amend last commit message

```bash
git commit --amend -m "feat: corrected commit message"
```

### Cherry-pick a commit to another branch

```bash
git checkout main
git cherry-pick abc1234
```

### View what would be in a PR

```bash
git log origin/main..HEAD --oneline
git diff origin/main...HEAD --stat
```

### Clean up merged branches

```bash
git branch --merged main | grep -v 'main' | xargs -r git branch -d
```

---

## Conflict resolution protocol

1. Identify the conflict source: `git log --merge --oneline`.
2. Understand both sides before resolving.
3. Prefer the incoming change when it represents a newer decision.
4. Re-run all tests after resolution.
5. If the conflict touches CHANGELOG.md, keep both entries and re-sort
   under the correct categories.
6. If unsure, abort and ask: `git rebase --abort`.
