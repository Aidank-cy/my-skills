# Frontend Audit Workflow

Use this reference after `SKILL.md` activates and the task requires
detailed audit execution, reporting, implementation, or communication
rules.

## Discovery

### Local projects

Read enough source to understand the full interface:

- HTML, CSS, JS/TS, JSX/TSX, Vue, Svelte, or equivalent UI files.
- Application shell: `index.html`, metadata, viewport, `lang`,
  global CSS, layout components, and route wrappers.
- Shared components, pages, form flows, navigation, and error or empty
  states.
- Design system signals: tokens, recurring values, typography,
  spacing, colors, icon sources, and component patterns.

Read all pages for small and medium projects. For more than 20 UI
files, read shared layout and representative pages first, then ask
which user flows to prioritize.

### Live websites

Fetch the provided URL. For a whole-site request, fetch up to 5 key
pages such as homepage, feature page, pricing or product page, and
contact or form page.

Evaluate visible HTML/CSS structure:

- document metadata and viewport
- landmarks, heading order, navigation, main, footer
- form labels, ARIA attributes, roles, alt text
- link and button semantics
- responsive and focus-style clues

State URL audit limitations in the report: JavaScript-dependent
behavior, computed styles, hover/focus states, client routing,
loading states, and dynamic content may be partially observable only.

## Evaluation

Read `heuristics.md` before evaluating. Walk through all 15 principles
one by one. For each principle, record findings or strengths.

Check these layers:

### Component layer

- semantic HTML structure
- accessibility attributes and focus management
- labels, descriptions, form validation, and error messaging
- loading, success, failure, and empty states
- responsive layout and touch targets
- hover, active, disabled, and focus states

### Hidden and dynamic UI

Actively search for UI not visible on first render:

- modals and dialogs: `role="dialog"`, `aria-modal`, labels, Escape,
  focus trap, close behavior, return focus
- dropdowns and menus: `aria-haspopup`, `aria-expanded`, keyboard
  navigation, click-outside behavior
- drawers and sidebars: focus trap, Escape, mobile behavior
- tooltips and toasts: timing, dismissibility, `role="status"` or
  `aria-live`
- accordions and tabs: roles and keyboard patterns
- validation states: `aria-describedby`, `aria-invalid`, error focus,
  screen reader announcements
- empty, loading, and error states
- destructive confirmations

### Visual design

Check whether visual hierarchy and layout help users scan:

- typography hierarchy and readable body text
- spacing rhythm and related-item grouping
- visual weight for primary content and actions
- color purpose, semantic color use, and palette restraint
- information density
- alignment and grid consistency
- visible interactive states

### System layer

Compare across pages and components:

- color, spacing, typography, and component consistency
- interaction pattern consistency
- hardcoded values that should use tokens
- navigation and wayfinding
- metadata, title, Open Graph, viewport, and language
- visible signifiers for clickability and state

Do not fabricate findings. If a principle is well-handled, record it
as a strength. If fewer than 10 findings appear in a real-world UI,
review visual hierarchy, hidden UI, edge cases, and application shell
again before finalizing.

## Report Format

Use this structure:

```markdown
## UX Design Audit Report

**Scope:** [what was evaluated]
**Source:** [files reviewed or URLs fetched]
**Interface type:** [dashboard / form / e-commerce / etc.]
**Limitations:** [URL audits only]

### How to Read This Report
Findings are rated on a 0-4 severity scale. Start with the highest
severity findings.

### Summary

| Severity | Count |
|----------|-------|
| 4 - Catastrophe | X |
| 3 - Major | X |
| 2 - Minor | X |
| 1 - Cosmetic | X |
| **Total findings** | **X** |

### Quick Wins
1. [Finding title] (Severity X) - [one-line fix]

### Findings

#### [Severity X] Finding title
- **Principle:** [principle]
- **Location:** `file.tsx:42` or page element
- **Issue:** [what is wrong]
- **User impact:** [concrete consequence for users]
- **Fix:** [specific recommendation]

### Strengths
- [Specific strength and principle satisfied]
```

Include at least 3 strengths. Acknowledge well-implemented patterns so
the user knows what to preserve.

## Discussion Mode

After presenting the report, state that findings will be fixed by
default unless the user wants to skip or deprioritize any. Explain
trade-offs when asked. Respect exclusions because the user may know
business constraints the code does not reveal.

## Implementation

Read `patterns.md` before implementing. Apply fixes in three phases.

### Phase 1: Establish design foundation

Extract and consolidate the implicit design system:

- spacing scale
- type scale
- color palette
- shadow levels
- border radius values
- transition duration and easing
- icon source and size conventions
- reusable component vocabulary

### Phase 2: Apply fixes

Apply code-level fixes with the smallest change that solves the
violation. Apply visual fixes through the design system rather than
ad-hoc values. Preserve existing visual identity while improving
hierarchy, clarity, accessibility, and interaction continuity.

### Phase 3: Design coherence pass

Review the whole interface after individual fixes:

- spacing rhythm
- typography consistency
- color discipline
- icon consistency
- component pattern consistency
- hover, focus, active, and disabled states
- transition consistency
- alignment
- semantic-visual sync

Ensure ARIA state has visible state. For example, `aria-current` needs
a highlighted navigation style, and `aria-expanded` needs a visible
open/close indicator.

## Interface Type Calibration

| Type | Character | Key moves |
|---|---|---|
| Portfolio | Clean, spacious, work-centered | Let work breathe, keep chrome restrained |
| Dashboard | Dense, scannable, data-focused | Emphasize metrics, labels, and compact structure |
| Marketing | Bold, focused, conversion-oriented | Clarify one message and primary CTA per region |
| Form/App | Guided, structured, reassuring | Group fields, validate inline, show progress |
| E-commerce | Browseable, trustworthy, scannable | Standardize product cards, pricing, filters, and review cues |

## Implementation Anti-Patterns

- defaulting to generic indigo/purple palettes
- wrapping every group in a card
- making competing CTAs equal weight
- giving all content equal visual emphasis
- mixing design languages across sections
- using uniform padding instead of intentional whitespace
- organizing by system structure instead of user tasks
- using low-contrast text for readable content
- leaving too many visual elements competing in one region

## Post-Implementation Review

After implementing, re-read modified files with fresh eyes. Check for:

- ARIA changes without visible CSS state
- specificity conflicts that prevent new CSS from applying
- raw design values that bypass tokens
- visual balance changes around modified elements
- complex tables, navigation, accordions, or comparison layouts
- state combinations such as active+hover or selected+disabled
- long text, empty cells, single-item lists, and maximum-length values

Fix issues found. If more than 3 severity-2-or-higher issues remain,
mention that a follow-up round may be worthwhile.

## Communication

Start warmly and then work directly. Tell the user the outcome being
provided, not which internal references are loading. During findings,
connect each issue to the relevant principle and concrete user impact.

Be specific:

- cite file and line for local projects
- cite page element or section for URL audits
- name the principle
- state why users are affected
- give a concrete fix

Be honest:

- avoid inflated severity
- avoid fabricated issues
- acknowledge good implementation
- note context-dependent trade-offs

## Invocation Modes

- Full evaluation with discussion: default for audit, UI review, UX
  review, or usability improvement requests.
- Evaluate only: report without implementation when the user asks only
  to audit, review, evaluate, or report.
- Improve: implement fixes from an existing audit when the user asks
  to fix or improve findings.
- Quick mode: evaluate and implement without discussion when the user
  asks for quick mode, auto-fix, or "just fix it."
