---
name: skill-authoring
description: >
  This skill should be used when the user asks to "write a skill",
  "review a skill", "improve a skill", "organize skill content",
  "refactor a SKILL.md", or needs guidance on skill structure,
  progressive disclosure, naming, or trigger descriptions.
  Also trigger when reviewing any SKILL.md file for quality.
---

# Skill authoring

Guide for writing, reviewing, and refactoring Agent Skills that follow
the open standard (works across Claude Code, Codex, Cursor, Gemini CLI).

## Skill anatomy

```
skill-name/
├── SKILL.md              ← required, core instructions
├── references/            ← docs loaded into context on demand
├── scripts/               ← executed via bash, not loaded
├── assets/                ← templates/images used in output
└── examples/              ← working code users can copy
```

## Progressive disclosure

Three layers, each loaded only when needed:

1. **Metadata** (name + description) — always in system prompt, ~100 tokens
2. **SKILL.md body** — loaded when skill triggers
3. **Bundled resources** — loaded or executed as needed by the model

### What goes where

| SKILL.md (always loaded on trigger) | references/ (loaded on demand) |
|--------------------------------------|-------------------------------|
| Core workflow and decision logic | Detailed patterns, advanced techniques |
| Quick-reference tables | Comprehensive API docs, schemas |
| Pointers to reference files | Migration guides, edge cases |
| Most common use cases | Extensive examples and walkthroughs |

**Budget:** SKILL.md body targets 1,500–2,000 words. Max 3,000 words / 500 lines.
Move anything beyond that to `references/`.

## Frontmatter rules

```yaml
---
name: processing-pdfs
description: >
  This skill should be used when the user asks to "extract text
  from a PDF", "fill a PDF form", "merge PDF files", or works
  with .pdf files. Handles text extraction, form filling, merging,
  and page manipulation.
---
```

### name

- Lowercase letters, numbers, hyphens only
- Max 64 characters
- Prefer gerund form: `processing-pdfs`, `analyzing-data`, `managing-hooks`
- Avoid vague names: `helper`, `utils`, `tools`

### description

- **Third person** always ("This skill should be used when…")
- Include specific trigger phrases users would say
- Both what the skill does AND when to use it
- Max 1,024 characters
- No XML tags

## Writing style

Use **imperative/infinitive form** throughout the body:

```
✓  Extract text using pdfplumber.
✓  Validate the output before proceeding.
✗  You should extract text using pdfplumber.
✗  Claude needs to validate the output.
```

## Content principles

### Only add what the model doesn't know

Challenge every paragraph: "Does the model really need this explanation?"
A 50-token code snippet beats a 150-token explanation of what PDFs are.

### Consistent terminology

Pick one term and use it everywhere. Don't alternate between
"API endpoint", "URL", "route", and "path".

### No time-sensitive information

Avoid "before August 2025, use the old API." Use an "old patterns"
collapsible section if historical context is needed.

### One level of references only

SKILL.md → references/guide.md is fine.
SKILL.md → references/guide.md → references/detail.md is not.
The model may partially read nested files.

## Review checklist

Apply this when reviewing or refactoring any skill:

### Structure

- [ ] SKILL.md exists with valid YAML frontmatter (name + description)
- [ ] Body is under 500 lines / 3,000 words
- [ ] Detailed content lives in `references/`, not in SKILL.md
- [ ] References are one level deep, not nested
- [ ] All referenced files actually exist
- [ ] No information is duplicated across SKILL.md and references

### Description quality

- [ ] Third person ("This skill should be used when…")
- [ ] Includes 3+ specific trigger phrases
- [ ] Lists concrete scenarios, not vague categories
- [ ] Under 1,024 characters

### Writing style

- [ ] Imperative form, not second person
- [ ] Consistent terminology throughout
- [ ] No time-sensitive information
- [ ] Only contains knowledge the model doesn't already have

### Progressive disclosure

- [ ] Core workflow is in SKILL.md
- [ ] Templates, schemas, detailed docs are in `references/`
- [ ] Working examples are in `examples/`
- [ ] Utility scripts are in `scripts/`
- [ ] SKILL.md has a clear pointer table to reference files

## Refactoring workflow

When asked to improve an existing skill:

1. Read the current SKILL.md and measure word count
2. Run the review checklist above
3. Identify content to extract:
   - Templates and YAML/code blocks > 20 lines → `references/`
   - Repeated scripts → `scripts/`
   - Working examples → `examples/`
4. Rewrite SKILL.md to contain only the decision logic, core workflow,
   and a pointer table to extracted files
5. Verify all pointers resolve to real files
6. Confirm the description has specific trigger phrases in third person

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Everything in one 8,000-word SKILL.md | Split into core (1,800 words) + references |
| Vague description: "Provides guidance" | Add trigger phrases: "create X", "configure Y" |
| Second person: "You should…" | Imperative: "Extract…", "Validate…" |
| No resource references | Add pointer table at the bottom of SKILL.md |
| Nested references (A→B→C) | Flatten to one level from SKILL.md |
| Explaining what the model knows | Cut it — every token competes for context |

## References

| When | Read |
|------|------|
| Need the official Anthropic spec | `references/anthropic-best-practices.md` |
| Need structural examples | `references/skill-examples.md` |
