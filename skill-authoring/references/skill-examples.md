# Skill structure examples

## Minimal skill (simple knowledge)

```
skill-name/
└── SKILL.md
```

Use when: no complex resources needed, everything fits in < 2,000 words.

## Standard skill (recommended)

```
skill-name/
├── SKILL.md                  (1,500–2,000 words)
├── references/
│   └── detailed-guide.md
└── examples/
    └── working-example.sh
```

Use when: core workflow is simple but has detailed docs worth separating.

## Complete skill (complex domain)

```
skill-name/
├── SKILL.md                  (1,500–2,000 words)
├── references/
│   ├── patterns.md
│   ├── advanced.md
│   └── api-reference.md
├── examples/
│   ├── basic-usage.sh
│   └── config-template.json
├── scripts/
│   └── validate.sh
└── assets/
    └── template.html
```

Use when: complex domain with validation utilities, templates, and
extensive documentation.

## Real-world example: hook-development (from Claude Code)

```
hook-development/
├── SKILL.md                  (1,651 words — lean core)
├── references/
│   ├── patterns.md           (detailed hook patterns)
│   ├── advanced.md           (advanced techniques)
│   └── api-reference.md      (hooks API docs)
├── examples/
│   ├── pre-tool-use.sh
│   ├── post-tool-use.sh
│   └── stop-hook.sh
└── scripts/
    ├── validate-hook-schema.sh
    ├── test-hook.sh
    └── create-hook.sh
```

Why it works: SKILL.md stays lean, trigger description includes exact
phrases ("create a hook", "add a PreToolUse hook"), references are one
level deep, all resources are clearly pointed to from SKILL.md.

## SKILL.md pointer table pattern

Always end SKILL.md with a table that tells the model when to read
each reference file:

```markdown
## References

| When | Read |
|------|------|
| Writing a new hook | `references/patterns.md` |
| Advanced validation logic | `references/advanced.md` |
| Hook API details | `references/api-reference.md` |
```

This is the most reliable way to ensure the model discovers and loads
the right file at the right time.

## Description examples

Good (specific triggers, third person):
```yaml
description: >
  This skill should be used when the user asks to "create a hook",
  "add a PreToolUse hook", "validate tool use", or mentions hook
  events (PreToolUse, PostToolUse, Stop). Provides hooks API
  guidance and validation utilities.
```

Bad (vague, wrong person):
```yaml
description: Helps with hooks.
description: Use this when you need hook help.
description: Load when user needs guidance.
```

## Anti-patterns in real skills

### Anti-pattern: Monolithic SKILL.md

Symptom: SKILL.md exceeds 3000 words or 500 lines.
Example: A 319-line handoff skill that inlines every scenario.
Fix: Extract scenario-specific content to `references/`, keep
only decision logic and core workflow in SKILL.md.

### Anti-pattern: Duplicated content across skills

Symptom: Two skills share 40%+ identical paragraphs.
Example: init and transform skills duplicating AGENTS.md generation rules.
Fix: Extract shared content into a common reference file. One skill
owns the file, the other points to it via relative path.

### Anti-pattern: Missing decay mechanism

Symptom: Anti-rationalization section only adds constraints, never removes.
Example: Rules accumulate across sessions but are never audited for relevance.
Fix: Add explicit decay rules. Review anti-rationalization entries every
3+ phases; remove any that have never been triggered.

### Anti-pattern: Thin reference files

Symptom: A reference file exists but contains less useful content than
the SKILL.md body that points to it.
Fix: Either merge the content back into SKILL.md (if total stays under
budget) or expand the reference with concrete examples and templates.

### Anti-pattern: No agent-profile adaptation

Symptom: Skill assumes a single execution environment.
Example: git-workflow assumes full git access but Codex runs in a sandbox.
Fix: Add conditional branches for different agent capabilities.
Detect environment constraints and adapt the workflow automatically.

### Anti-pattern: Task prompt overrides project-level Always rules

Symptom: A task-scoped Codex prompt says "Do NOT modify CHANGELOG.md"
and the agent obeys, even though AGENTS.md says "Always update
CHANGELOG after completed work."
Example: Refactoring task marks harness files as out-of-scope;
agent finishes without changelog or progress entry.
Fix: In the prompt-gateway skill, add a final step (6F) that lists
project-level Always obligations that cannot be overridden by
task-level scope restrictions. Add matching anti-rationalization.
