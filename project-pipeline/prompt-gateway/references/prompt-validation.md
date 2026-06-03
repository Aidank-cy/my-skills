# Prompt Validation Reference

## Two-tier validation

### Tier A: Full spec (Claude Code processed)

Must have all four headers: `## Task`, `## Context`, `## Requirements`, `## Scope`.

### Tier B: Lightweight spec (user-written)

Must satisfy three conditions: **what** (clear change description), **where** (file/module), **done-when** (testable outcome).

---

## Tier A examples

```markdown
## Task
Add a dark mode toggle to the settings page.

## Context
Users have requested dark mode support. The design system already includes
dark color tokens in `src/styles/tokens.ts` but they are not wired up.
The toggle should persist preference to localStorage.

## Requirements
1. A toggle switch appears on the `/settings` page under "Appearance"
2. Toggling applies dark mode immediately without page reload
3. User preference persists across sessions (localStorage)
4. Default follows system preference (`prefers-color-scheme`)
5. All existing components render correctly in dark mode

## Scope
**In scope:**
- `src/pages/Settings.tsx` — add toggle UI
- `src/contexts/ThemeContext.tsx` — create new context
- `src/styles/tokens.ts` — wire up dark tokens
- `src/components/Layout.tsx` — consume theme context

**Out of scope:**
- Redesigning existing components
- Adding dark mode to the marketing site
- Email template theming

## Constraints
- Use CSS custom properties, not Tailwind dark: prefix
- No new dependencies

## Test Plan
1. Toggle switch toggles `data-theme` attribute on `<html>`
2. Refresh page → preference persists
3. Clear localStorage → falls back to system preference
4. Visual regression: no broken layouts in dark mode
```

### Example 2: Fixing a bug

```markdown
## Task
Fix infinite redirect loop on expired JWT sessions.

## Context
When a user's JWT expires mid-session, the auth middleware redirects to
`/login`, which checks auth status, sees the expired token, and redirects
again, creating an infinite loop. Reported in issue #42.

## Requirements
1. Expired tokens are cleared before redirect to `/login`
2. `/login` page loads successfully even with expired/invalid tokens
3. After re-login, user is redirected to their original intended page
4. No redirect loop occurs under any token state (valid, expired, missing, malformed)

## Scope
**In scope:**
- `src/middleware/auth.ts` — fix redirect logic
- `src/pages/Login.tsx` — handle expired token cleanup

**Out of scope:**
- Token refresh mechanism (separate task)
- Auth middleware refactoring
```

### Example 3: Minimal spec (for trivial changes)

```markdown
## Task
Fix typo in README: "dependancies" → "dependencies"

## Scope
`README.md` line 23

## Requirements
1. Word is spelled correctly
```

---

## Tier B examples (lightweight spec)

### Passes — has what + where + done-when

```
Fix the login redirect loop in src/middleware/auth.ts.
After the fix, expired tokens are cleared before redirect
and /login loads without looping.
```
- **What:** fix redirect loop → ✅
- **Where:** src/middleware/auth.ts → ✅
- **Done-when:** tokens cleared, no loop → ✅

```
Add a "last updated" timestamp to the footer component
(src/components/Footer.tsx). Should show the build date
from package.json.
```
- **What:** add timestamp → ✅
- **Where:** src/components/Footer.tsx → ✅
- **Done-when:** shows build date from package.json → ✅

### Fails — missing one or more conditions

```
Fix the auth bug
```
- **What:** fix auth bug → vague but present
- **Where:** ❌ no file/module
- **Done-when:** ❌ no testable outcome
- **Verdict:** REJECT (0-1 met)

```
Refactor the user service to be faster
```
- **What:** refactor for speed → present
- **Where:** "user service" → somewhat present
- **Done-when:** ❌ "faster" is unmeasurable
- **Verdict:** ASK for done-when ("How do you measure faster? Target latency?")

---

## Detection patterns

### Regex patterns for quick validation

```bash
# ---- Tier A: Full spec ----
has_task=$(grep -ci '^## Task' <<< "$prompt")
has_requirements=$(grep -ci '^## Requirements' <<< "$prompt")
has_scope=$(grep -ci '^## Scope' <<< "$prompt")
has_context=$(grep -ci '^## Context' <<< "$prompt")

if [[ $has_task -gt 0 && $has_requirements -gt 0 && $has_scope -gt 0 && $has_context -gt 0 ]]; then
  echo "TIER A: full spec detected"
  exit 0
fi

# ---- Tier B: Lightweight spec ----
# Check for what (non-trivial description, >10 words)
word_count=$(wc -w <<< "$prompt")
has_what=$( [[ $word_count -gt 10 ]] && echo 1 || echo 0 )

# Check for where (file paths or module names)
has_where=$(grep -cE '(src/|lib/|app/|components/|pages/|routes/|middleware/|services/|utils/|\.[tj]sx?|\.(py|rs|go))' <<< "$prompt")

# Check for done-when (should/must/after/expect/pass)
has_done=$(grep -ciE '(should|must|after|expect|pass|verify|true|correct|work|render|return|display)' <<< "$prompt")

met=0
[[ $has_what -gt 0 ]] && ((met++))
[[ $has_where -gt 0 ]] && ((met++))
[[ $has_done -gt 0 ]] && ((met++))

if [[ $met -eq 3 ]]; then
  echo "TIER B: lightweight spec detected"
elif [[ $met -eq 2 ]]; then
  echo "PARTIAL: ask user to fill gap"
else
  echo "REJECT: insufficient structure"
fi
```

### Structural scoring (Tier A only)

| Signal | Points |
|--------|--------|
| Has `## Task` header | +3 |
| Has `## Requirements` with numbered items | +3 |
| Has `## Scope` with file paths | +3 |
| Has `## Context` | +2 |
| Has explicit "Out of scope" | +2 |
| Has `## Constraints` | +1 |
| Has `## Test Plan` | +1 |
| Has metadata tag `[source: claude-code]` | +5 |

**Tier A threshold: 8+ points = full spec.** Below 8 with headers present → tell user which sections need fleshing out.

**Tier B doesn't use scoring** — it uses the three binary conditions (what/where/done-when). Either all three are met or they aren't.

---

## Common rejection patterns

| User input | Why it fails | What to tell them |
|-----------|-------------|-------------------|
| "Add a login page" | No structure at all | Need Task + Requirements + Scope |
| "Fix the bug in auth" | No specifics, no scope | Which bug? What file? What's the expected behavior? |
| "Improve performance" | Unmeasurable, no criteria | Need specific metrics and target values |
| "Add login and fix header and update footer" | Mixed concerns | Split into separate tasks, one spec each |
| "Make it better" | Completely vague | Better how? By what measure? |
