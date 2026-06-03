# Anthropic and Open Standard Best Practices

Use this reference when authoring or auditing cross-platform Agent
Skills. Apply it as execution guidance, not as tutorial material.

## Core Principles

### Concise is key

Treat the context window as shared space. Include only instructions
the agent needs to execute the task. Remove background explanations,
generic tutorials, and repeated rationale once the action is clear.

### Progressive disclosure

Organize content so the agent loads only what the current task needs:

1. Metadata: `name` and `description` load at discovery time.
2. `SKILL.md`: core workflow loads after activation.
3. Bundled resources: references load on demand; scripts execute
   without loading source code into context.

### Degrees of freedom

Match instruction specificity to task fragility:

| Freedom | Use when | Authoring pattern |
|---|---|---|
| High | Many valid approaches exist | Give criteria and review heuristics |
| Medium | A preferred approach exists | Provide pseudocode or a template |
| Low | Consistency and safety are critical | Provide exact scripts or command sequences |

### Test with target agents

Test the skill with the agents and models that will load it. Add
detail only where testing shows underperformance.

## Description As Primary Trigger

Write descriptions as the skill-selection contract. The agent reads
the description before it reads the body, references, or scripts.

- Keep descriptions under 1,024 characters for the open standard.
- Respect Claude Code's larger 1,536-character budget when targeting
  Claude-specific environments, but keep the first 1,024 characters
  sufficient for other clients.
- Front-load the most important trigger phrases because clients may
  truncate descriptions when many skills are installed.
- Make descriptions slightly "pushy" because agents tend to
  undertrigger when adjacent scenarios are omitted.
- Include what the skill does, when it applies, and clear exclusions
  for always-on skills.

Move all trigger information out of body sections such as
"When to Use This Skill." Body sections load too late to influence
activation.

## Writing Style

Use imperative or infinitive instructions:

- Use: "Extract text with pdfplumber."
- Use: "Validate the output before continuing."
- Avoid: "You should extract text with pdfplumber."
- Avoid: "Claude needs to validate the output."

Explain why when a constraint matters. Prefer reusable reasoning over
rigid all-caps rules. Keep terminology consistent across the skill
and references.

## Loading Model

Author for this loading sequence:

1. Agent sees all skill names, descriptions, and paths.
2. Agent chooses a skill based on the description.
3. Agent reads the selected `SKILL.md`.
4. Agent reads referenced files only when the body points to them.
5. Agent executes scripts when deterministic behavior or validation
   is more reliable than re-generating code.

## Common Patterns

### Template pattern

Use templates when the output format matters. Keep the template in
`SKILL.md` if short; move large templates to `references/`.

### Examples pattern

Use examples for transformations that are hard to describe abstractly.
Place reusable examples in `examples/` or compact before/after pairs
in `references/`.

### Conditional workflow

Use decision trees when a task has modes. Keep the branch decision in
`SKILL.md`; move branch-specific details to `references/`.

### Domain-specific organization

Split large domain knowledge into one-level reference files. Point to
only the relevant file from the main workflow.

## Anti-Patterns

- Deeply nested references: flatten to one level from `SKILL.md`.
- Time-sensitive instructions: avoid date-conditional rules unless
  historical context is required.
- Inconsistent terminology: pick one term for each concept.
- Extraneous files: omit README, install guides, changelogs, and quick
  references inside skill directories unless the agent needs them.
- "When to Use" body sections: move trigger content into the
  description and delete the body section.
- Overloaded `SKILL.md`: extract detailed scenario content to
  `references/`.
- Untested scripts: run scripts after creating or modifying them.

## Security

Install skills only from trusted sources. Audit every file in a skill
directory before installation, including scripts, assets, references,
and platform metadata. Treat scripts as executable code with the same
review standards as project code.

## Source Attribution

- Anthropic Claude Docs: Skill authoring best practices,
  `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`
- Anthropic skill-creator guidance from the bundled system skill.
- Agent Skills open specification and overview,
  `https://agentskills.io/`
