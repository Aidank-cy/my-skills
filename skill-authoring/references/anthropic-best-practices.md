# Anthropic official best practices — summary

Source: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices

## Core principles

1. **Concise is key** — the context window is a shared resource. Every
   token in your skill competes with conversation history and other skills.
2. **Set appropriate degrees of freedom** — match specificity to task
   fragility. Fragile operations (migrations) need exact scripts.
   Flexible tasks (code review) need general guidance.
3. **Test with all models you plan to use** — what works for Opus may
   need more detail for Haiku.

## Loading model

- Startup: only name + description from all skills (~100 tokens each)
- On trigger: SKILL.md body is read
- On demand: references, scripts, assets loaded as needed
- Scripts can be executed without loading into context

## Description field

- Third person always
- Include both what it does and when to use it
- Be specific with key terms
- Max 1,024 characters

## Progressive disclosure patterns

### Pattern 1: High-level guide with references
SKILL.md has quick-start and pointers. Detailed docs in separate files.

### Pattern 2: Domain-specific organization
Split by domain (finance.md, sales.md, product.md). Only the relevant
domain file is loaded.

### Pattern 3: Conditional details
Basic content inline. Advanced content behind references, loaded only
when the task needs it.

## Workflows and feedback loops

- Break complex operations into clear sequential steps
- Provide checklists for multi-step workflows
- Implement validate → fix → repeat loops
- Scripts as validators improve output quality

## Common patterns

- **Template pattern**: provide output format templates
- **Examples pattern**: input/output pairs (like few-shot prompting)
- **Conditional workflow**: decision tree routing to different procedures

## Anti-patterns

- Windows-style paths (use forward slashes always)
- Offering too many options (provide a default with escape hatch)
- Deeply nested references (keep one level deep)
- Time-sensitive information
- Inconsistent terminology
- Scripts that punt errors to the model instead of handling them

## Token budgets

- SKILL.md body: under 500 lines
- Reference files: unlimited but include table of contents if > 100 lines
- Metadata description: max 1,024 characters
- Skill name: max 64 characters
