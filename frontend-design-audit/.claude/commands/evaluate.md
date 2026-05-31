---
name: frontend-design-audit:evaluate
description: Run a usability audit on front-end code and produce a structured report. No implementation — just the analysis.
---

# Frontend Audit: Evaluate Only

Run a usability audit and produce a report. Do not implement any changes.

## Required Reading

Before starting, read these files:
1. The main frontend design audit skill — The evaluation framework and workflow
2. `references/heuristics.md` — Detailed principle definitions and what to look for

## Usage

Ask the agent to evaluate common UI paths, a specific directory, or a specific file.

## Process

1. **Identify UI files** — Use the agent's file-search tools to find front-end files (tsx, jsx, vue, svelte, html, css). Prefer `rg` when available. If a path was provided, scope to that path. If not, look for common UI directories (src/components, src/pages, app/, pages/, etc.).

2. **Read the code** — Read the key UI files. For large projects, focus on the most important screens (index/home, main dashboard, primary form, key user flow).

3. **Evaluate systematically** — Go through all 15 principles. For each, inspect the code for violations. Reference `references/heuristics.md` for what to look for.

4. **Rate severity** — Apply the 0-4 scale to each finding. Consider frequency, impact, and persistence.

5. **Produce the report** — Use the structured format from SKILL.md. Include:
   - Summary table with severity counts
   - All findings grouped by severity (highest first)
   - Each finding with: principle reference, file location, issue description, user impact, recommended fix
   - A "Strengths" section noting what the interface does well

6. **Present to user** — Show the full report. Offer to explain any finding in more detail. Do NOT implement changes — this command is evaluation only.

## After the Report

Suggest next steps:
- "Would you like me to explain any of these findings in more detail?"
- "Ready to start fixing these? Ask me to improve the top-priority items."
- "Want the quick version? Ask me to auto-fix safe severity 3-4 issues."
