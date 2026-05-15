---
name: harness-engineering-transform
description: >
  This skill should be used when the user asks to add harness
  engineering to an existing project, create AGENTS.md or CLAUDE.md,
  add agent rules, set up hooks or AI quality gates, scaffold skills or
  subagent personas, or says things like "make my repo agent-friendly",
  "set up coding agent rules", "agent harness", "harness 工程", or
  "让我的项目支持 AI agent". Audit the current codebase, infer likely
  failure modes, scaffold only the harness files the project actually
  needs, and generate model-agnostic agent guidance, hooks, templates,
  skills, and CI that fit the existing architecture.
---

# Harness Engineering Transform

Transform an existing codebase into a harness-engineering-compliant project.
Audit first, scaffold second, generate third.

## Core rules

- Execute the workflow in order: audit, scaffold, generate.
- Base every generated rule on real project structure or a plausible failure mode.
- Mark inferred rules with `[INFERRED]`.
- Keep `AGENTS.md` short, concrete, and runnable.
- Prefer cross-tool-compatible primary artifacts.
- Keep remote git operations user-owned unless explicitly requested.

## Workflow

1. Audit the existing project.
2. Present the audit summary and proposed harness plan.
3. Scaffold the needed harness structure.
4. Generate tailored harness content.
5. Verify the generated harness before handing it over.

## Phase 1: Audit

Read the project before writing anything.

### Audit goals

Identify:
- language and framework
- package manager
- test framework
- lint and format tools
- architecture pattern
- existing agent configuration
- CI or deployment pipeline
- sensitive areas such as auth, payments, migrations, infra, or secrets
- version tracking state, including changelog files, version files, and git tags

### Failure-mode analysis

Infer the top likely agent failure modes from the codebase.
Use categories such as:
- architecture drift
- import violations
- style inconsistency
- dependency chaos
- test sabotage
- security gaps
- scope creep
- convention violations

### Audit output

Present all of the following before generating files:
- project profile
- ranked failure modes
- proposed harness structure
- open questions that affect boundaries or conventions

Wait for user confirmation or correction before proceeding.

For project-shape heuristics and stack-specific command patterns, read `references/tech-stack-reference.md`.

## Phase 2: Scaffold

Create only the harness structure the project actually needs.

### Always generate

- `AGENTS.md`
- `CHANGELOG.md` if missing
- `.harness/`
  - `task-template.md`
  - `plan-template.md`
  - `impact-map.sh`

### Generate conditionally

Add these only when justified by the audit:
- `CLAUDE.md`
- `.cursor/rules/`
- `.github/copilot-instructions.md`
- `skills/`
- `agents/`
- `hooks/`
- `.github/workflows/ai-quality-gate.yml`
- `.harness/progress.md`
- `.harness/learning-log.md`
- `.harness/anti-rationalization.md`

### Scaffold decisions

Use these rules:
- any project gets `CHANGELOG.md`; versioning logic is handled by the user-level `versioning-and-changelog` skill
- Claude Code projects get `CLAUDE.md`
- Cursor projects get `.cursor/rules/`
- larger or multi-domain projects get project-specific domain skills in `skills/`
- large or multi-domain projects may justify reviewer personas
- existing CI should be extended instead of duplicated
- sensitive projects should receive stronger hooks and a security reviewer

Core pipeline skills (`prompt-gateway`, `versioning-and-changelog`,
`git-workflow`) are user-level and always available. Do not duplicate
them into the project. The project's `skills/` directory is reserved
for domain-specific skills unique to that codebase.

For the full scaffold matrix, read `references/generated-artifacts.md`.

## Phase 3: Generate

Generate content that fits the real codebase.

### AGENTS.md

Generate `AGENTS.md` with these standards:
- 60 lines or fewer
- real commands for install, test, lint, build, and dev when applicable
- three-tier boundaries: `Always`, `Ask first`, `Never`
- concrete architecture and pattern guidance
- `[INFERRED]` markers on rules that come from inferred failure modes

### Harness templates and scripts

Generate:
- `.harness/task-template.md`
- `.harness/plan-template.md`
- `.harness/impact-map.sh`

Tailor the impact map and templates to the project's actual language and workflow.

### Hooks and CI

Generate hooks and CI only from the real toolchain.
Pair important probabilistic rules with deterministic enforcement where possible.

### Skills and personas

Generate 2-5 project-specific domain skills in `skills/` when the
codebase justifies them (e.g. API routing, database migrations,
frontend components, security policies). These complement the
user-level pipeline skills, not replace them.
Include a router skill only when generating 3+ project-specific skills.
Generate personas only for larger or clearly multi-domain codebases.

### Progress and anti-rationalization files

Generate `.harness/progress.md` and `.harness/anti-rationalization.md` when the project will benefit from cross-session continuity or repeated agent work.

For full templates for AGENTS, task templates, hooks, CI, skills, personas, and anti-rationalization content, read `references/generated-artifacts.md`.
For examples of useful domain skills, read `references/component-catalog.md`.

## Verification

Before finishing, confirm all of the following:
- `AGENTS.md` is short and contains real commands
- inferred rules are labeled
- `CHANGELOG.md` exists and matches the repo's version history state
- templates and hooks reference real project commands
- generated skills match the project's real domains
- generated files do not point to nonexistent tools or paths
- executable scripts received executable permissions

## User handoff

Brief the user on these priorities:
- start with `AGENTS.md`
- pair rules with hooks and CI where possible
- expand skills gradually based on real failures
- use `CHANGELOG.md` continuously, not only at release time
- ratchet new rules and hooks in response to actual mistakes

## Principles

Apply these principles during generation:
- use the ratchet principle
- distinguish probabilistic guidance from deterministic enforcement
- prefer progressive disclosure over loading everything at once
- keep context small and structured
- separate generation from evaluation when reviewer personas are available
- keep the output model-agnostic whenever possible

## Anti-rationalization

Reject these shortcuts:
- generating files before auditing the codebase
- inventing rules with no project evidence or plausible failure mode
- dumping every optional harness file into every project
- writing AGENTS guidance with vague statements instead of commands
- treating hooks or CI as optional when they enforce critical constraints
- copying generic templates without tailoring them to the actual repo

## References

| When needed | Read |
|-------------|------|
| Need stack-specific commands, heuristics, or audit hints | `references/tech-stack-reference.md` |
| Need examples of domain skills and harness components | `references/component-catalog.md` |
| Need the full scaffold matrix and generation templates | `references/generated-artifacts.md` |
