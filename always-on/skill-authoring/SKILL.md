---
name: skill-authoring
description: >
  This skill should be used when the user asks to "write a skill",
  "create a skill", "review a skill", "improve a skill", "audit a
  skill", "fix a SKILL.md", "refactor a SKILL.md", or when the
  agent is about to create or modify any SKILL.md file. Provides
  the execution standard for skill structure, description quality,
  progressive disclosure, scope classification, and cross-platform
  compatibility. Also trigger when reviewing any SKILL.md for
  quality or when another skill's description fails to trigger
  correctly. Do NOT trigger for casual conversation, general
  questions, greetings, or topics unrelated to skill authoring.
---

# Skill Authoring

Execution standard for writing, reviewing, and modifying Agent
Skills. Apply these rules whenever creating or auditing a SKILL.md.

## Activation guard

Activate only when explicitly asked to write, review, improve,
or refactor a skill or SKILL.md file. General conversations about
AI, coding, or workflow do not trigger this skill.

## Skill directory structure

Use this standard anatomy:

```text
skill-name/
├── SKILL.md              ← required
├── references/            ← loaded into context on demand
├── scripts/               ← executed via bash, not loaded
├── assets/                ← templates, images used in output
├── examples/              ← working code users can copy
└── agents/                ← optional, platform-specific metadata
    └── openai.yaml        ← Codex UI metadata and policy
```

Do not create extraneous files. No README.md, no
INSTALLATION_GUIDE.md, no CHANGELOG.md, no QUICK_REFERENCE.md.
A skill directory contains only what the agent needs to execute.

## Description field

The description is the ONLY signal the agent reads at startup.
The body, references, and scripts load AFTER the agent decides
to trigger. If trigger information is not in the description,
the skill will not activate.

### Writing a description

1. Start with third person: "This skill should be used when..."
2. State what the skill does in one sentence.
3. List 3+ specific trigger phrases users would say.
   Put the most important trigger phrases first — descriptions
   may be truncated when many skills are installed.
4. List adjacent scenarios the skill should also handle, even
   if not explicitly named. Agents undertrigger — write
   descriptions that are slightly "pushy."
5. End with negative triggers if the skill is always-on:
   "Do NOT trigger for [irrelevant contexts]."
6. Keep under 1,024 characters (open standard limit).

### Common description failures

| Symptom | Root cause | Fix |
|---|---|---|
| Skill never triggers | Description too vague | Add specific trigger phrases |
| Skill triggers for wrong requests | No negative triggers | Add "Do NOT trigger for..." |
| Skill triggers inconsistently | Trigger info is in body, not description | Move all "when to use" content into description |
| Skill crowded out by other skills | Important triggers buried late in description | Reorder: most critical triggers first |

### "When to Use" body sections are wasted

Never put trigger information in a "## When to Use This Skill"
body section. The agent does not read the body before deciding
to trigger. If such a section exists in a skill being reviewed,
move its content into the description and delete the section.

## Name field

- Lowercase letters, numbers, hyphens only.
- Max 64 characters.
- Verb-led when possible: `processing-pdfs`, `managing-hooks`.
- Namespace by tool when it improves clarity: `gh-address-comments`.
- Avoid vague names: `helper`, `utils`, `tools`, `general`.

## Progressive disclosure

Three layers, each loaded only when needed:

1. **Metadata** (name + description) — always loaded, ~100 tokens
2. **SKILL.md body** — loaded when skill triggers, target <500 lines
3. **Bundled resources** — loaded or executed on demand, unlimited

### What goes where

| SKILL.md body (loaded on trigger) | references/ (loaded on demand) |
|---|---|
| Core workflow and decision logic | Detailed patterns, advanced techniques |
| Quick-reference tables and decision trees | Comprehensive schemas, API docs |
| Pointers to reference files | Migration guides, edge cases |

Budget: SKILL.md body targets 1,500–2,000 words. Max 3,000 words
or 500 lines. Move anything beyond that to references/.

### Large reference files

- Over 300 lines: add a table of contents at the top.
- Over 10,000 words: add grep search hints in the SKILL.md
  pointer table so the agent can search efficiently:

| When | Read |
|------|------|
| Need endpoint details | `references/api.md` (grep: "endpoint", "route") |

### One level of references only

SKILL.md → references/guide.md is fine.
SKILL.md → references/guide.md → references/detail.md is not.
The agent may partially read nested files. Flatten to one level.

## Writing instructions

### Form

Use imperative/infinitive form throughout:
- ✓ "Extract text using pdfplumber."
- ✓ "Validate the output before proceeding."
- ✗ "The agent should extract text using pdfplumber."
- ✗ "Validation needs to happen before proceeding."

### Explain why, not rigid rules

Prefer reasoning over rigid constraints. If writing ALWAYS or
NEVER in all caps, reframe as an explanation of why. The agent
generalizes better from understood reasoning than from rigid
rules that may not fit unseen cases.

- ✗ "NEVER modify files outside the project directory."
- ✓ "Restrict modifications to the project directory — changes
   outside it risk breaking unrelated projects and are difficult
   to trace or revert."

### Degrees of freedom

Match instruction specificity to task fragility:

| Level | When | Example |
|---|---|---|
| High (text guidance) | Multiple valid approaches | Code review, writing style |
| Medium (pseudocode) | Preferred pattern exists | API integration, config |
| Low (exact scripts) | Fragile, consistency critical | DB migrations, releases |

### Only add what the agent doesn't know

Challenge every paragraph: "Does the agent need this?"
A 50-token code snippet beats a 150-token explanation of
something the agent already understands.

### Consistent terminology

Pick one term and use it everywhere. Do not alternate between
"API endpoint", "URL", "route", and "path" for the same concept.

## Scripts as extracted patterns

When the same code is rewritten across 3+ skill invocations,
extract it into scripts/. Scripts execute without loading into
context — only the output consumes tokens.

Detection signal: if the agent repeatedly generates similar
helper scripts (e.g., every PDF task writes a rotate_pdf.py),
bundle it once in scripts/ and reference it from SKILL.md.

After creating a script, test it by running it. Do not assume
scripts work without verification.

## Activation scope

When authoring for a multi-skill library, classify the skill:

| Scope | Location | Characteristics |
|---|---|---|
| always-on | User-level skills dir | Reactive, narrow triggers, never rejects chat |
| project-pipeline | Project-level skills dir | Gatekeepers, require project context |
| domain-skills | Either level | Standalone, self-contained |

Decision procedure:
1. Does it intercept or gate user input? → project-pipeline
2. Does it require project context (AGENTS.md, .harness/)? → project-pipeline
3. Could it reject casual conversation? → project-pipeline
4. Is it a standalone capability? → domain-skills
5. Is it a passive, reactive helper? → always-on

For always-on skills:
- Add an "## Activation guard" section in the body.
- Add negative triggers in the description.

For project-pipeline skills:
- Add a conversation mode check that skips the skill when no
  project context is detected.
- Consider setting allow_implicit_invocation: false in
  agents/openai.yaml.

## Codex-specific metadata

Codex supports an optional agents/openai.yaml for UI metadata
and invocation policy:

```yaml
interface:
  display_name: "Human-Readable Name"
  short_description: "One-line summary for skill picker"

policy:
  allow_implicit_invocation: true
```

Set allow_implicit_invocation to false for skills that should
only activate on explicit $skill invocation.

This file is Codex-specific. Other agents ignore it. Include
it only for skills used with Codex.

## Review checklist

Apply when reviewing or refactoring any skill:

### Structure
- [ ] SKILL.md exists with valid YAML frontmatter (name + description)
- [ ] Body is under 500 lines / 3,000 words
- [ ] Detailed content lives in references/, not SKILL.md
- [ ] References are one level deep, not nested
- [ ] All referenced files exist and paths resolve
- [ ] No duplicated content across SKILL.md and references
- [ ] No extraneous files (README, CHANGELOG, INSTALL)

### Description quality
- [ ] Third person ("This skill should be used when...")
- [ ] 3+ specific trigger phrases
- [ ] Most important triggers appear first (truncation-safe)
- [ ] Adjacent scenarios listed ("pushy" enough)
- [ ] Under 1,024 characters
- [ ] No "When to Use" section in body (all trigger info in description)
- [ ] Negative triggers present if always-on skill

### Writing
- [ ] Imperative form, not second person
- [ ] Reasoning over rigid ALWAYS/NEVER rules
- [ ] Consistent terminology throughout
- [ ] Only contains knowledge the agent doesn't already know

### Scope
- [ ] Activation scope determined (always-on / project-pipeline / domain)
- [ ] Activation guard present if always-on
- [ ] Conversation mode check present if project-pipeline
- [ ] agents/openai.yaml present if used with Codex (optional)

### Progressive disclosure
- [ ] Core workflow is in SKILL.md
- [ ] Templates, schemas, detailed docs are in references/
- [ ] Scripts are in scripts/, tested and executable
- [ ] SKILL.md ends with a pointer table to reference files

## Refactoring workflow

When asked to improve an existing skill:

1. Read the current SKILL.md. Measure word count and line count.
2. Run the review checklist above. Record all failures.
3. Check the description:
   - Is all trigger info in the description, not the body?
   - Is it "pushy" enough?
   - Are negative triggers present if always-on?
4. Identify content to extract:
   - Templates and code blocks > 20 lines → references/
   - Repeated scripts → scripts/
   - Working examples → examples/
5. Rewrite SKILL.md to contain only decision logic, core workflow,
   and a pointer table to extracted files.
6. Verify all pointers resolve to real files.
7. Confirm word count is under 3,000 / line count under 500.

## Anti-rationalization

Reject these shortcuts:
- Adding rules without a concrete trigger or failure mode
- Keeping detailed scenario content in SKILL.md when a reference would do
- Treating a longer skill as a more complete skill
- Putting trigger information in the body instead of the description
- Writing rigid ALWAYS/NEVER rules when reasoning would generalize better
- Keeping rules that have never been triggered by a real failure
- Creating extraneous files (README, CHANGELOG) in skill directories
- Treating skill file count or word count as a quality signal

## References

| When | Read |
|------|------|
| Need Anthropic and open standard best practices | `references/anthropic-best-practices.md` |
| Need OpenAI Codex-specific skill guidance | `references/codex-best-practices.md` |
| Need structural examples and anti-patterns | `references/skill-examples.md` |
