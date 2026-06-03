# Sync Audit

Run this audit when asked, or proactively every ~20 commits.

## Quick Audit (one-liner)

```bash
# Files marked for removal in the sync workflow
grep -oP '(?<=rm -rf |rm -f ).+' .github/workflows/sync-public.yml \
  | tr ' ' '\n' | sort > /tmp/private-files.txt

# All repo files (excluding .git and node_modules)
find . -not -path './.git/*' -not -path './node_modules/*' \
  -type f -o -type d | sed 's|^\./||' | sort > /tmp/all-files.txt

# Unclassified files — verify each is intentionally public
comm -23 /tmp/all-files.txt /tmp/private-files.txt
```

## Full Checklist

1. Run the quick audit above
2. For each unclassified file, apply the classification decision tree
3. Flag any files that should be private but are missing an `rm` rule
4. Check that no private patterns were accidentally removed from the workflow
5. Verify the public repo does not contain any files from the private list
   (clone it and diff if needed)
6. Verify `auto-close-pr.yml` is NOT in the `rm` list (it must sync)
7. Check that the secret name in the workflow matches the actual secret
   in Settings → Secrets → Repository secrets
8. Confirm the public repo's Ruleset is still active with correct
   bypass list
9. Report findings to the user
