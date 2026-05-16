# Project Patterns

Common private/public splits by project type. Use as a starting point,
then adjust per project.

## Next.js / React

```
PRIVATE: AGENTS.md, CLAUDE.md, EDITING.md, CHANGELOG.md, TODO.md,
         .project-rules/, .harness/, .cursor/, skills/, hooks/,
         .github/copilot-instructions.md,
         .github/workflows/ai-quality-gate.yml,
         .github/workflows/sync-public.yml

PUBLIC:  app/, components/, lib/, config/, public/,
         package.json, package-lock.json, next.config.ts,
         tsconfig.json, eslint.config.mjs, postcss.config.mjs,
         .gitignore, README.md, LICENSE,
         .github/workflows/auto-close-pr.yml
```

## Python / FastAPI

```
PRIVATE: AGENTS.md, CLAUDE.md, .cursor/, .project-rules/,
         scripts/internal/, tests/internal/,
         .github/workflows/sync-public.yml

PUBLIC:  src/, tests/ (public tests), requirements.txt,
         pyproject.toml, Dockerfile, README.md, LICENSE,
         .github/workflows/auto-close-pr.yml
```

## Monorepo

```
PRIVATE: Root AI/tooling files (same as above),
         packages/internal-*/, tools/dev-only/

PUBLIC:  packages/public-*/, apps/,
         root configs, README.md, LICENSE,
         .github/workflows/auto-close-pr.yml
```

## Rust / Cargo

```
PRIVATE: AGENTS.md, CLAUDE.md, .cursor/, .project-rules/,
         benches/internal/, scripts/,
         .github/workflows/sync-public.yml

PUBLIC:  src/, Cargo.toml, Cargo.lock, tests/,
         README.md, LICENSE,
         .github/workflows/auto-close-pr.yml
```
