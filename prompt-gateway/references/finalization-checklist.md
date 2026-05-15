# Finalization Checklist Reference

This file details the automated closing sequence (Step 5) in granular detail.

---

## Pre-finalization gate

Before entering the finalization sequence, ALL of these must be true:

- [ ] All acceptance criteria from the spec are met
- [ ] Lint passes with zero errors
- [ ] Typecheck passes (if applicable)
- [ ] Tests pass (existing + any new ones)
- [ ] No files outside of scope were modified
- [ ] No new dependencies were added without spec authorization

If any fail, **do not enter finalization**. Fix or report to user.

---

## 5A: CHANGELOG update rules

### Mapping task type to changelog category

| Spec / commit type | Changelog category |
|--------------------|-------------------|
| New feature, new endpoint, new page | **Added** |
| Modified behavior, refactored logic | **Changed** |
| Marked as deprecated | **Deprecated** |
| Removed code, removed feature | **Removed** |
| Bug fix, error correction | **Fixed** |
| Vulnerability fix, auth hardening | **Security** |

### Entry format

Each entry is a single line, human-readable, present tense:

```
- Add dark mode toggle to settings page with system preference fallback
- Fix infinite redirect loop on expired JWT sessions (#42)
- Remove legacy XML export endpoint (deprecated in v2.1.0)
```

Rules:
- Start with a verb (Add, Fix, Remove, Update, Change, Deprecate)
- Include issue/PR number if available
- One entry per logical change (not per file)
- No implementation details (don't say "modify auth.ts line 42")

### Insertion logic

```bash
# Find the [Unreleased] section and insert after the appropriate category header
# If the category header doesn't exist yet, create it

# Example: Adding a "Fixed" entry
CHANGELOG="CHANGELOG.md"
CATEGORY="### Fixed"
ENTRY="- Fix infinite redirect loop on expired JWT sessions (#42)"

if grep -q "$CATEGORY" <(sed -n '/## \[Unreleased\]/,/## \[/p' "$CHANGELOG"); then
  # Category exists — append under it
  sed -i "/$CATEGORY/a $ENTRY" "$CHANGELOG"
else
  # Category doesn't exist — add it under [Unreleased]
  sed -i "/## \[Unreleased\]/a \\
\\
$CATEGORY\\
$ENTRY" "$CHANGELOG"
fi
```

---

## 5B: Rules file update decision tree

```
Did execution reveal a new pattern or failure mode?
├── YES → Is it project-wide (affects all future tasks)?
│   ├── YES → Add to AGENTS.md with [NEW] tag
│   └── NO → Is it module-specific?
│       ├── YES → Add to relevant .cursor/rules/ or skill file
│       └── NO → Log in .harness/progress.md as observation
└── NO → Skip rules update
```

### What qualifies as a new rule

| Observation | Rule to add |
|-------------|-------------|
| "I discovered the project uses a custom logger, not console.log" | `[NEW] Use src/lib/logger.ts for all logging, never console.log` |
| "The API always returns wrapped responses via responseHelper" | `[NEW] All API responses use src/utils/responseHelper.ts` |
| "Tests must use the factory pattern in tests/factories/" | `[NEW] Create test data using factories in tests/factories/, never inline` |
| "I was tempted to modify an adjacent module" | No rule needed — AGENTS.md already says "stay in scope" |

### Update format for AGENTS.md

```markdown
## Always
- [EXISTING] Run lint before commit: `pnpm lint`
- [NEW] Use ResponseHelper for all API responses — never raw res.json()
```

The `[NEW]` tag tells the user: "I added this during task execution. Review it."

---

## 5C: Progress state format

```markdown
## {YYYY-MM-DD} — {Task title from spec}
- **Status:** Complete | Partial (reason) | Blocked (reason)
- **Commit:** {short hash} — {commit message first line}
- **Changes:** {1-2 sentence summary}
- **CHANGELOG:** {category}: {entry text}
- **Rules updated:** {Yes: what was added | No}
- **Follow-ups:**
  - {Any out-of-scope items discovered}
  - {Any tech debt noted}
  - {Any related tasks suggested}
```

---

## 5D: Commit message format

### Structure

```
{type}[!][(scope)]: {description}

[optional body]

[optional footer]
```

### Type selection

| If the task... | Commit type |
|---------------|-------------|
| Adds new functionality | `feat` |
| Fixes a bug | `fix` |
| Restructures without behavior change | `refactor` |
| Only changes docs | `docs` |
| Only changes tests | `test` |
| Build/tooling/config changes | `chore` |
| Breaks backward compatibility | `feat!:` or `fix!:` |

### Scope (optional, from spec's ## Scope)

If the spec targets a specific module, use it as scope:
- `feat(auth): add JWT refresh on expiry`
- `fix(settings): resolve dark mode persistence issue`

### Examples

```bash
# Simple feature
git commit -m "feat: add dark mode toggle to settings page"

# Bug fix with issue reference
git commit -m "fix(auth): resolve infinite redirect on expired JWT

Clear expired tokens before redirecting to /login.
Store intended destination for post-login redirect.

Closes #42"

# Breaking change
git commit -m "feat!(api): change response envelope format

All API responses now use { data, error, meta } envelope.
Previous { result, status } format is no longer supported.

BREAKING CHANGE: API response format changed."
```

---

## 5E: Summary output template

```
✅ Task complete and committed locally.

┌─────────────────────────────────────────┐
│ Commit   {short_hash} {first_line}      │
│ Files    {N} changed                    │
│ CHANGELOG  [Unreleased] → {category}    │
│ Rules    {Updated: +{N} rules | None}   │
│ Tests    {N passed, N added}            │
└─────────────────────────────────────────┘

Remote operations (your call):
  git push origin {branch}
  gh pr create --title "{title}"
```
