# Codex Best Practices

Use this reference when authoring skills for Codex. Keep instructions
portable unless Codex-specific behavior is required.

## Skill Directory Locations

Codex discovers skills from these locations:

| Scope | Location | Use |
|---|---|---|
| Project | `.agents/skills/` from CWD up to repo root | Repo or folder-specific workflows |
| User | `$HOME/.agents/skills/` | Personal skills available across repos |
| Admin | `/etc/codex/skills` | Shared machine or container skills |
| System | Bundled by OpenAI | Built-in skills available to all sessions |

Codex scans project skills from the current working directory upward
to the repository root. If skills share the same `name`, Codex does
not merge them; multiple entries can appear.

Codex follows symlink targets when scanning skill folders.

## Optional agents/openai.yaml

Add `agents/openai.yaml` only when Codex-specific UI metadata,
invocation policy, or tool dependencies are useful.

```yaml
interface:
  display_name: "Name shown to users"
  short_description: "Short description"
  default_prompt: "Use $skill-name to ..."
  icon_small: "./assets/small-logo.svg"
  icon_large: "./assets/large-logo.png"
  brand_color: "#3B82F6"

policy:
  allow_implicit_invocation: true
```

Use `interface` fields for Codex app display:
- `display_name`: human-readable title.
- `short_description`: compact one-line UI summary.
- `default_prompt`: short prompt snippet; mention `$skill-name`.
- `icon_small` and `icon_large`: paths relative to the skill root.
- `brand_color`: hex color for UI accents.

Use `policy.allow_implicit_invocation` to control automatic matching:
- `true` (default): Codex may invoke the skill when the prompt
  matches the description.
- `false`: Codex will not implicitly invoke the skill; explicit
  `$skill-name` invocation still works.

Set `allow_implicit_invocation: false` for skills with broad side
effects or skills that should only run when the user explicitly names
them.

## Description Truncation

Codex includes an initial list of available skills in context. The
list is capped at roughly 2% of the model context window, or 8,000
characters when the window is unknown. When many skills are installed,
Codex shortens descriptions first.

Front-load important trigger words and scope boundaries. Ensure the
first sentence alone gives Codex enough signal to choose or skip the
skill.

## Invocation Modes

Codex activates skills in two ways:

1. Explicit invocation: the user mentions `$skill-name`.
2. Implicit invocation: Codex matches the prompt to the skill
   `description`.

Test both modes after authoring a skill. Check that casual prompts do
not accidentally trigger always-on skills.

## Skills And Plugins

Use skills as the authoring format for reusable workflows. Use plugins
as the distribution format when sharing reusable skills, bundling
multiple skills, or packaging skills with apps, MCP servers, or
presentation assets.

Keep direct skill folders simple for local authoring and repo-scoped
workflows.

## Sandbox Considerations

Author skills so they can handle restricted environments. Codex
sessions may limit git, network, filesystem, or approval behavior.

- Check available tools before relying on network or browser access.
- Prefer local files and bundled references when possible.
- Make destructive operations explicit and reversible.
- Document required external tools in `agents/openai.yaml` only when
  the skill is packaged for Codex.

## Source Attribution

- OpenAI Developers: Agent Skills for Codex,
  `https://developers.openai.com/codex/skills`
- OpenAI Skills repository: `agents/openai.yaml` reference,
  `https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md`
- OpenAI Skills repository examples,
  `https://github.com/openai/skills`
