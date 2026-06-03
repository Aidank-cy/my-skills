---
name: frontend-design-audit
description: >
  This skill should be used when the user asks to "audit this UI",
  "review this page for UX", "improve this frontend design",
  "evaluate accessibility", "audit a website", "make this interface
  easier to use", or provides front-end code or a URL and wants
  usability findings. Handles local source audits and live website
  report-only audits across UX, accessibility, visual hierarchy,
  interaction patterns, and design consistency. Also trigger on
  symptoms like abandoned forms, confusing pages, checkout complaints,
  conversion drops, or "something feels off." Do NOT trigger for
  building new interfaces from scratch, performance optimization,
  security audits, or backend logic.
---

# Frontend Design Audit

Audit and improve existing front-end interfaces using established
usability principles.

## Scope guard

Activate for existing local front-end code or live website URLs.
Skip new-interface generation, backend logic, security audits, and
performance-only requests.

## Core principles

Evaluate against these 15 principles:

| # | Principle |
|---|---|
| 1 | Visibility of System Status |
| 2 | Match Between System and Real World |
| 3 | User Control and Freedom |
| 4 | Consistency and Standards |
| 5 | Error Prevention |
| 6 | Recognition Over Recall |
| 7 | Flexibility and Efficiency |
| 8 | Aesthetic and Minimalist Design |
| 9 | Error Recovery |
| 10 | Help and Documentation |
| 11 | Affordances and Signifiers |
| 12 | Structure |
| 13 | Accessibility |
| 14 | Perceptibility |
| 15 | Tolerance and Forgiveness |

Read `references/heuristics.md` before evaluation.

## Severity scale

Rate every finding by user impact:

| Rating | Label | Meaning |
|---|---|---|
| 0 | Not a problem | No usability issue |
| 1 | Cosmetic | Aesthetic issue only |
| 2 | Minor | Users notice but work around it |
| 3 | Major | Users struggle significantly |
| 4 | Catastrophe | Users cannot complete tasks or make serious errors |

Weigh frequency, impact, and persistence. Rate severity based on
what users experience, not how easy the fix is.

## Input modes

### Local project

Read source files, shared layout, global CSS, application shell,
pages, and reusable components. Implement fixes after reporting unless
the user asks for evaluation only.

### Live website URL

Inspect served HTML/CSS and visible structure. Produce a report only.
State limitations clearly: JavaScript behavior, computed CSS,
client-side routing, dynamic states, and actual rendering may be only
partially observable.

## Workflow

1. Discover the interface type, stack, user flows, and design system.
2. Evaluate every principle at component, hidden-state, visual, and
   system levels.
3. Report findings by severity with user impact and specific fixes.
4. Discuss trade-offs and skipped findings in discussion mode.
5. Implement local fixes through a coherent design foundation.
6. Verify changes with a post-implementation review.

Read `references/audit-workflow.md` for detailed execution steps,
report format, implementation phases, communication rules, and
invocation modes.

## Evaluation requirements

- Read all relevant UI files for local projects. For projects with
  more than 20 UI files, ask which flows to focus on after reading
  shared layout and representative pages.
- Fetch up to 5 key pages for multi-page URL audits.
- Check hidden and dynamic UI: modals, dialogs, dropdowns, drawers,
  tooltips, toasts, accordions, tabs, validation states, loading
  states, empty states, and destructive confirmations.
- Check visual design: typography hierarchy, spacing, visual weight,
  color purpose, information density, alignment, and interactive
  states.
- Check system behavior: cross-page consistency, interaction pattern
  consistency, design token use, navigation, wayfinding, metadata, and
  signifiers.
- Note strengths as well as problems. Do not fabricate violations.

## Implementation requirements

Read `references/patterns.md` before implementation.

Apply fixes in this order:

1. Establish design tokens and component vocabulary.
2. Apply findings through the design system.
3. Run a design coherence pass across spacing, typography, color,
   icons, component patterns, states, transitions, alignment, and
   semantic-visual sync.

Preserve existing visual identity while improving hierarchy,
accessibility, and clarity. Test that fixes do not break existing
functionality.

## Report requirements

Include:
- scope and source files or URLs
- interface type and limitations
- severity summary
- quick wins
- findings grouped by severity
- at least 3 specific strengths

For each finding, include:
- principle violated
- exact file/line or page element
- issue
- concrete user impact
- actionable fix

## References

| When | Read |
|------|------|
| Need detailed audit workflow, report format, implementation phases, or communication rules | `references/audit-workflow.md` |
| Need principle definitions, violation patterns, severity guidance, or visual checks | `references/heuristics.md` |
| Need concrete accessibility, interaction, or visual-design fix examples | `references/patterns.md` |
