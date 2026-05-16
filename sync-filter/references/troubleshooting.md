# Troubleshooting — Sync Push Failures

Common errors and fixes, ordered by frequency.

## Error: `Invalid username or token` (401)

```
remote: Invalid username or token.
Password authentication is not supported for Git operations.
fatal: Authentication failed
```

### Cause 1: Secret name mismatch

The workflow references `secrets.PORTFOLIO_PAT` but the secret is
stored under a different name (e.g. `PUBLIC_REPO_TOKEN`).

**Diagnose:** Add a debug step before the push:

```yaml
- name: Debug auth
  env:
    TOKEN: ${{ secrets.PORTFOLIO_PAT }}
  run: |
    echo "Token length: ${#TOKEN}"
    echo "Token prefix: ${TOKEN:0:4}"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
      -H "Authorization: Bearer ${TOKEN}" \
      https://api.github.com/repos/OWNER/PUBLIC-REPO)
    echo "API response: ${STATUS}"
```

- Token length `0` → secret name does not match. Check the exact
  name in Settings → Secrets → Repository secrets.
- Token prefix not `ghp_` → wrong value was stored.
- API response `401` → token itself is invalid (expired, revoked,
  or copied with extra characters).
- API response `200` but push still fails → git credential issue,
  see Cause 2.

**Fix:** Delete and recreate the secret with the correct name. Use the
copy button on GitHub when copying the token value.

### Cause 2: Token stored in Variables instead of Secrets

Repository variables are plaintext and accessed via `vars.NAME`,
not `secrets.NAME`.

**Fix:** Move the value to Repository secrets.

### Cause 3: Token copied incorrectly

Extra whitespace, missing characters, or newlines in the pasted value.

**Fix:** Regenerate the token, copy with the copy button, paste into
a new secret. Verify locally first with `curl`.

## Error: `Permission denied` (403)

```
remote: Permission to owner/repo.git denied to username.
fatal: unable to access: The requested URL returned error: 403
```

### Cause 1: Token lacks required scopes

Classic token missing `repo` scope, or fine-grained token missing
Contents Read & Write permission.

**Fix:** Edit or regenerate the token with correct scopes. Update
the secret.

### Cause 2: Fine-grained token targets wrong repository

The token was created with repository access set to a different repo
or "All repositories" but the owner doesn't match.

**Fix:** Regenerate with **Only select repositories** → select the
target public repo.

## Error: `push declined due to repository rule violations`

```
remote: - refusing to allow a Personal Access Token to create or
update workflow `.github/workflows/auto-close-pr.yml`
without `workflow` scope
```

### Cause: Missing `workflow` scope

GitHub requires a separate `workflow` scope/permission to push any
file under `.github/workflows/`. This is a security measure — workflow
files can execute arbitrary code.

**Fix (Classic token):** Check both `repo` AND `workflow` scopes.
Regenerate. Update the secret.

**Fix (Fine-grained token):** Add Workflows → Read and write under
Repository permissions. Regenerate. Update the secret.

**Alternative:** If adding `workflow` scope is undesirable, exclude
workflow files from sync and manage them manually in the public repo:

```yaml
rm -f .github/workflows/auto-close-pr.yml
```

## Error: `push declined` (Ruleset blocking)

```
remote: error: GH013: Repository rule violations found
! [remote rejected] HEAD -> main (push declined due to repository
rule violations)
```

### Cause: Bypass list misconfigured

The public repo's Ruleset does not include the pushing identity in
the bypass list.

**Fix:** Public repo → Settings → Rules → Rulesets → edit the ruleset
→ Bypass list → add **Repository admin**. The PAT maps to your admin
account, so it needs admin bypass.

## Error: `Token length: 0` in debug output

### Cause: Secret not found by Actions

The secret name in the workflow does not match any secret in the repo's
settings. GitHub silently returns an empty string for missing secrets.

**Fix:** Go to Settings → Secrets → Repository secrets and verify the
exact name. Names are case-sensitive and must not contain spaces.

## General debugging workflow

1. Add the debug step (see above) before the push step
2. Check token length — if 0, fix the secret name
3. Check token prefix — should be `ghp_` for classic, `github_pat_`
   for fine-grained
4. Check API response — 200 means token is valid, 401/403 means
   token issue
5. If API returns 200 but push fails, the issue is git credential
   configuration or Ruleset blocking
6. Remove the debug step after the issue is resolved
