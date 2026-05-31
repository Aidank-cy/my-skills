# Handoff Scenarios

Use these scenario templates only when the default task-complete
handoff is not enough.

## Handoff direction 1 scenarios

### After a task completes (PR workflow alternative)

When the user prefers code review before remote merge, instruct
`prompt-gateway` to skip Step 6E auto-merge. The agent commits
on the feature branch but does not merge. Then present:

```
Task committed on branch {type}/{name}.

Verify the changes:
  git diff main..HEAD                # review what changed
  {build_command}                    # confirm build passes
  {inspect_command}                  # visually inspect the result

Your next steps:
  git push origin {type}/{name}
  gh pr create --title "{type}: {subject}"

After PR is approved and merged:
  git checkout main
  git pull origin main
  git branch -d {type}/{name}
```

Use this path only when the user explicitly requests PR-based review.
The default is auto-merge.

### After a release commit

```
Release committed and tagged locally.

Sync to remote:
  git push origin main --follow-tags

Optional — create a GitHub Release:
  gh release create v{x.y.z} --notes-from-tag
```

### After a hotfix task

Hotfixes follow the same auto-merge flow. After merge:

```
Hotfix merged to main locally.

Verify the fix:
  git diff HEAD~1                    # review what changed
  {build_command}                    # confirm build passes
  {test_or_inspect_command}          # confirm the fix works

Sync to remote:
  git push origin main

Consider an immediate patch release:
  Tell the agent: "release a patch" or "ship the hotfix"
```

## Gap handling scenarios

### Gap 1: User forgot to push after multiple tasks

The agent detects local main is ahead of origin/main. Remind:

```
Your local main has {N} unpushed commits:
  git push origin main
```

### Gap 2: Feature branch left open (interrupted session)

The agent detects an unmerged feature branch from a previous session.

```
□ Is the branch work complete?
  → YES: merge it now.
    git checkout main
    git merge {branch} --no-ff
    git branch -d {branch}
  → NO: resume work on the branch, then merge.
  → ABANDONED: delete it.
    git checkout main
    git branch -D {branch}
```

### Gap 3: CI failed after pushing main

The user reports CI failure. Extract:
- which check failed (lint, test, typecheck, build)
- error message and file location if provided

Enter `prompt-gateway` as a fix task. The user's CI error report
counts as a Tier B prompt if it contains what (CI failure), where
(file/test name), and done-when (CI passes).

### Gap 4: CHANGELOG conflicts after push

When pushing introduces CHANGELOG conflicts (rare in single-developer
flow, possible with multiple collaborators):

```
CHANGELOG.md had a conflict. After resolving:
  - Keep all entries from both sides
  - Re-sort entries under the correct categories
  - Ensure [Unreleased] section is intact at the top
```

### Gap 5: Release partially completed

The user pushed the release commit but forgot `--follow-tags`,
or tagged locally but did not push:

```
Tag v{x.y.z} exists locally but may not be on remote:
  git push origin v{x.y.z}
```

## Resume phrases

| User says | Agent does |
|---|---|
| "resume" / "continue" / "where was I" | Run context recovery, summarize state |
| "I pushed" / "already pushed" | Acknowledge, verify remote sync, ready for next task |
| "CI failed" / "CI broke" + error info | Treat as a fix task, enter `prompt-gateway` |
| "release" / "ship it" / "cut a release" | Delegate to `versioning-and-changelog` Flow 2 |
| "check status" / "project status" / "what's pending" | Run full context recovery, present summary |

## Presentation rules

- Always present in this order: task summary → verify → push.
- Verification commands must be real, runnable commands from the
  project's actual toolchain. Never use placeholder commands.
- Include at minimum: a diff command, a build/test command, and a
  way to inspect the result (dev server, open file, run CLI).
- Tailor verification to what the task actually changed.
- Include only the git commands relevant to the current scenario.
- Use actual branch names, commit types, and version numbers.
- Do not explain what each command does unless the user asks.
- End with a brief note on what to tell the agent next.
