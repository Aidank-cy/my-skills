---
name: harness-remote-handoff
description: >
  This skill should be used when the user returns after performing
  remote git operations (push, release publish), asks "what should
  I do next" after a task completes, reports CI failure after pushing,
  says things like "I pushed", "CI failed", "已推送", "CI挂了",
  or needs guidance on maintaining harness integrity after the agent
  has merged a task to main locally. Also trigger when the user comes
  back after a break and asks to resume work, check project state,
  or confirm sync status. In the task-based workflow, the agent
  auto-merges to main after each task, so the handoff is primarily
  about syncing local main with remote.
---

# Harness Remote Handoff

Maintain harness integrity across the agent-user boundary.
In the task-based workflow, the agent owns the full local cycle:
branch → subtasks → commit → merge to main. The user owns remote
operations. This skill governs the handoff after each task and the
recovery path when the user returns.

## Core rules

- Never assume the user completed remote operations. Verify from project state.
- Never block on missing remote confirmation. Start the next task from actual state.
- Always check `CHANGELOG.md`, `.harness/progress.md`, latest tag, and recent git log when resuming.
- Guide the user with exact commands, not vague instructions.

## Handoff direction 1: Agent → User

After `prompt-gateway` Step 6E completes, the task is merged to
main locally and the feature branch is deleted. The user receives
a completion summary. Present the appropriate remote sync commands.

### After a task completes (default)

The agent has already merged to main. The user only needs to sync
with remote:

```
✅ Task merged to main locally.

Sync to remote:
  git push origin main
```

If the project accumulates multiple tasks before pushing, all
merged commits go up in one push.

### After a task completes (PR workflow alternative)

When the user prefers code review before remote merge, instruct
`prompt-gateway` to skip Step 6E auto-merge. The agent commits
on the feature branch but does not merge. Then present:

```
Task committed on branch {type}/{name}.

Your next steps:
  git push origin {type}/{name}
  gh pr create --title "{type}: {subject}"

After PR is approved and merged:
  git checkout main
  git pull origin main
  git branch -d {type}/{name}
```

This path is only used when the user explicitly requests PR-based
review. The default is auto-merge.

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

Sync to remote:
  git push origin main

Consider an immediate patch release:
  Tell the agent: "发版" or "release a patch"
```

### Presentation rules

- Include only the commands relevant to the current scenario.
- Use actual branch names, commit types, and version numbers.
- Do not explain what each command does unless the user asks.
- End with a brief note on what to tell the agent next.

## Handoff direction 2: User → Agent

When the user returns after remote operations or a break, recover
context from project state rather than asking the user to report.

### Context recovery procedure

1. Read `.harness/progress.md` for the last recorded task.
2. Read `CHANGELOG.md` for unreleased entries and latest version.
3. Read `git log --oneline -10` for recent commit history.
4. Read `git tag --sort=-v:refname | head -3` for recent tags.
5. Check current branch with `git branch --show-current`.
6. Check for uncommitted changes with `git status --short`.

### State interpretation

| Observed state | What likely happened | Agent action |
|---|---|---|
| On `main`, clean, progress.md has recent task completion | Normal post-task state | Ready for new task |
| On `main`, local ahead of remote | User has not pushed yet | Remind: `git push origin main` |
| On `main`, new tag matches CHANGELOG release section | User completed a release push | Ready for new task |
| On `main`, CHANGELOG has unreleased entries, no new tag | Tasks merged but no release cut | Inform user of pending release option |
| On `main`, progress.md stale (last entry > 7 days) | User was away | Summarize current state and pending items |
| On feature branch, uncommitted changes | Session interrupted mid-task | Resume: finish subtasks → commit → merge |
| On feature branch, committed but not merged | Auto-merge was skipped or failed | Run merge protocol: checkout main → merge → delete branch |

### What the user can say to resume

| User says | Agent does |
|---|---|
| "继续" / "resume" / "where was I" | Run context recovery, summarize state |
| "已推送" / "I pushed" | Acknowledge, verify remote sync, ready for next task |
| "CI挂了" / "CI failed" + error info | Treat as a fix task, enter `prompt-gateway` |
| "发版" / "release" / "ship it" | Delegate to `versioning-and-changelog` Flow 2 |
| "项目状态" / "check status" / "what's pending" | Run full context recovery, present summary |

## Handling common gaps

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
or tagged locally but didn't push:

```
Tag v{x.y.z} exists locally but may not be on remote:
  git push origin v{x.y.z}
```

## Integration points

### With prompt-gateway

`prompt-gateway` Step 6E is the handoff trigger. After auto-merge,
this skill defines what the agent presents and how it recovers
when the user returns.

### With git-workflow

`git-workflow` defines branch, commit, and merge conventions.
This skill uses those conventions when generating commands.

### With versioning-and-changelog

When the observed state suggests a release is pending (unreleased
entries, no new tag), suggest entering `versioning-and-changelog`
Flow 2.

### With sync-filter

When the project uses dev→public sync, remind after push:

```
The sync workflow will run on push. Verify:
  - Public repo does not contain harness files
  - Public repo has the latest app source
```

## Anti-rationalization

Reject these shortcuts:
- Asking the user "did you push?" when git state can answer
- Assuming remote operations succeeded without checking
- Skipping context recovery and starting a task from stale state
- Giving vague resumption advice instead of specific commands
- Ignoring an unmerged feature branch when the user requests a new task

## References

| When needed | Read |
|---|---|
| Need detailed command templates for each handoff scenario | `references/handoff-commands.md` |
