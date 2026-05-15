# Harness Engineering — Tech Stack Quick Reference

This file is loaded by the SKILL.md when the agent needs stack-specific commands and patterns. Find the matching stack and use the exact commands listed.

---

## TypeScript / JavaScript (Node.js)

### Detection
`package.json` exists at root.

### Commands to discover
```bash
# Package manager
cat package.json | grep -E '"packageManager"'
ls pnpm-lock.yaml yarn.lock package-lock.json bun.lockb 2>/dev/null

# Test framework
cat package.json | grep -E '"test"' 
ls jest.config* vitest.config* .mocharc* cypress.config* playwright.config* 2>/dev/null

# Lint/format
ls .eslintrc* eslint.config* .prettierrc* biome.json 2>/dev/null
```

### Typical AGENTS.md commands
```
- Install: `pnpm install` (or npm/yarn/bun as detected)
- Test: `pnpm test` or `pnpm vitest run`
- Lint: `pnpm eslint . --max-warnings 0`
- Typecheck: `pnpm tsc --noEmit`
- Build: `pnpm build`
```

### Recommended lint rules for AI code (`.eslintrc.js`)
```javascript
rules: {
  "complexity": ["error", { "max": 10 }],
  "max-depth": ["error", 4],
  "max-lines-per-function": ["error", { "max": 50 }],
  "max-lines": ["error", { "max": 300 }],
  "max-params": ["error", 4],
  "max-statements": ["error", 15],
  "no-console": ["error", { allow: ["warn", "error"] }]
}
```

### Common failure modes
- Agent uses `npm` when project uses `pnpm` — causes lockfile conflicts
- Agent imports from `@/` alias incorrectly — check tsconfig paths
- Agent uses `any` type to bypass errors
- Agent adds `// @ts-ignore` instead of fixing types

---

## Python

### Detection
`pyproject.toml`, `setup.py`, `requirements.txt`, or `Pipfile` exists.

### Commands to discover
```bash
# Package manager / env
ls pyproject.toml setup.py setup.cfg requirements*.txt Pipfile 2>/dev/null
cat pyproject.toml 2>/dev/null | grep -A5 '\[tool\.'

# Test framework
cat pyproject.toml 2>/dev/null | grep -E 'pytest|unittest'
ls pytest.ini setup.cfg tox.ini 2>/dev/null

# Lint/format
ls .ruff.toml ruff.toml .flake8 .pylintrc .mypy.ini 2>/dev/null
```

### Typical AGENTS.md commands
```
- Install: `pip install -e ".[dev]"` or `poetry install`
- Test: `pytest tests/ -v`
- Lint: `ruff check .`
- Typecheck: `mypy src/`
- Format: `ruff format .`
```

### Common failure modes
- Agent doesn't activate virtualenv before running commands
- Agent uses `# type: ignore` to suppress mypy errors
- Agent uses `# noqa` to suppress lint warnings
- Agent imports `*` from modules
- Agent creates flat scripts instead of following project's module structure

---

## Rust

### Detection
`Cargo.toml` exists at root.

### Typical AGENTS.md commands
```
- Build: `cargo build`
- Test: `cargo test`
- Lint: `cargo clippy -- -D warnings`
- Format check: `cargo fmt -- --check`
```

### Common failure modes
- Agent uses `unwrap()` instead of proper error handling
- Agent adds `#[allow(...)]` attributes to suppress warnings
- Agent doesn't run `cargo clippy` after changes

---

## Go

### Detection
`go.mod` exists at root.

### Typical AGENTS.md commands
```
- Build: `go build ./...`
- Test: `go test ./... -v`
- Lint: `golangci-lint run`
- Format check: `gofmt -l .`
```

### Common failure modes
- Agent ignores error returns
- Agent doesn't run `go vet` after changes
- Agent creates files in wrong package directory

---

## Monorepo patterns

### Detection
Multiple `package.json` / `Cargo.toml` / `go.mod` at different levels, or `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`.

### AGENTS.md additions for monorepos
```markdown
## Architecture
This is a monorepo with the following packages:
- `packages/core` — shared utilities (no UI dependencies)
- `packages/web` — frontend application
- `packages/api` — backend API
- `apps/` — deployable applications

## Never
- Import from `packages/web` into `packages/core` (dependency flows down, not up)
- Run install/test at root without specifying the package filter
- Modify shared packages without checking all consumers
```

### Scope the impact map
```bash
# For monorepos, scope to the affected package
.harness/impact-map.sh packages/core
```
