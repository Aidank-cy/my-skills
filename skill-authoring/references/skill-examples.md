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
