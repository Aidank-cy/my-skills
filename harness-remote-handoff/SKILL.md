---
name: harness-remote-handoff
description: >
  This skill should be used when the user returns after performing
  remote git operations (push, PR, merge), asks "what should I do
  next" after a local commit, reports CI failure after pushing,
  says things like "I pushed", "PR merged", "CI failed", "已推送",
  "已合并", "CI挂了", or needs guidance on maintaining harness
  integrity across the boundary between agent-managed local commits
  and user-owned remote operations. Also trigger when the user
  comes back after a break and asks to resume work, check project
  state, or confirm sync status.
---

# Harness Remote Handoff

Maintain harness integrity across the agent-user boundary.
The agent owns local work up to commit. The user owns remote
operations. This skill governs the handoff protocol in both
directions and the recovery path when the user returns.

## Core rules

- Never assume the user completed remote operations. Verify from project state.
- Never block on missing remote confirmation. Start the next task from actual state.
- Always check `CHANGELOG.md`, `.harness/progress.md`, latest tag, and recent git log when resuming.
- Guide the user with exact commands, not vague instructions.

## Handoff direction 1: Agent → User

When `prompt-gateway` Step 6E returns remote operations to the user,
present the appropriate command set based on the task type.

### After a feature commit

```
Your next steps:
  git push origin {branch}
  gh pr create --title "{type}: {subject}"

After PR is approved and merged:
  git checkout main
  git pull origin main
  git branch -d {branch}
```

### After a release commit

```
Your next steps:
  git push origin main --follow-tags

Optional — create a GitHub Release:
  gh release create v{x.y.z} --notes "$(sed -n '/## \[{x.y.z}\]/,/## \[/p' CHANGELOG.md | sed '1d;$d')"
```

### After a hotfix commit

```
Your next steps:
  git push origin {branch}
  gh pr create --title "fix: {subject}" --label "hotfix"

After merge, consider an immediate patch release:
  Tell the agent: "发版" or "release a patch"
```

### Presentation rules

- Include only the commands relevant to the current task type.
- Use the actual branch name, commit type, and version number.
- Do not explain what each command does unless the user asks.
- End with a brief note on what to tell the agent next.

## Handoff direction 2: User → Agent

When the user returns after remote operations, recover context
from project state rather than asking the user to report.

### Context recovery procedure

1. Read `.harness/progress.md` for the last recorded task.
2. Read `CHANGELOG.md` for unreleased entries and latest version.
3. Read `git log --oneline -10` for recent commit history.
4. Read `git tag --sort=-v:refname | head -3` for recent tags.
5. Check current branch with `git branch --show-current`.
6. Check for uncommitted changes with `git status --short`.

### State interpretation

| Observed state | What happened | Agent action |
|---------------|---------------|-------------|
| On `main`, progress.md has recent completion, no uncommitted changes | User pushed and merged successfully | Ready for new task |
| On feature branch, no uncommitted changes, commits ahead of main | User has not yet pushed or PR is pending | Remind user of pending push/PR |
| On `main`, new tag exists that matches CHANGELOG release section | User completed a release push | Ready for new task |
| On feature branch, uncommitted changes present | Work in progress, session interrupted | Resume or commit |
| On `main`, CHANGELOG has unreleased entries, no new tag | Features merged but no release cut yet | Inform user of pending release |
| On `main`, progress.md is stale (last entry > 7 days) | User was away | Summarize current state and pending items |

### What the user can say to resume

Teach the agent to recognize these re-entry patterns:

| User says | Agent does |
|-----------|-----------|
| "继续" / "resume" / "where was I" | Run context recovery, summarize state |
| "已推送" / "I pushed" / "PR merged" | Acknowledge, check state, ready for next task |
| "CI挂了" / "CI failed" + error info | Treat as a fix task, enter `prompt-gateway` |
| "review要改" / "PR needs changes" | Treat as a modification task on current branch |
| "发版" / "release" / "ship it" | Delegate to `versioning-and-changelog` Flow 2 |
| "项目状态" / "check status" / "what's pending" | Run full context recovery, present summary |

## Handling common gaps

### Gap 1: User forgot to push

The agent detects commits on a feature branch with no evidence of
remote activity. Remind:

```
You have local commits on {branch} that haven't been pushed yet:
  git push origin {branch}
```

### Gap 2: User merged but didn't pull main

The agent detects `main` is behind `origin/main`. Suggest:

```
Your local main is behind remote. Pull before starting:
  git checkout main
  git pull origin main
```

### Gap 3: User pushed but CI failed

The user reports a CI failure. Extract:
- which check failed (lint, test, typecheck, build)
- error message and file location if provided

Then enter `prompt-gateway` as a fix task. The user's CI error report
counts as a Tier B prompt if it contains what (CI failure), where
(file/test name), and done-when (CI passes).

### Gap 4: User merged PR but CHANGELOG conflicts

When a merge introduces CHANGELOG conflicts (common when multiple
features land close together), guide:

```
CHANGELOG.md had a merge conflict. After resolving:
  - Keep all entries from both sides
  - Re-sort entries under the correct categories
  - Ensure [Unreleased] section is intact at the top
```

### Gap 5: Release was partially completed

The user pushed the release commit but forgot `--follow-tags`,
or tagged locally but didn't push. Detect from tag and remote state:

```
Tag v{x.y.z} exists locally but may not be on remote:
  git push origin v{x.y.z}
```

## Integration points

### With prompt-gateway

`prompt-gateway` Step 6E is the handoff trigger. This skill defines
what the agent presents at that boundary and how it recovers when
the user returns.

### With git-workflow

`git-workflow` defines the branch, commit, PR, and merge conventions.
This skill uses those conventions when generating the user's command
set. Defer naming and formatting decisions to `git-workflow`.

### With versioning-and-changelog

When the user returns and the observed state suggests a release is
pending (unreleased entries, no new tag), this skill can suggest
entering `versioning-and-changelog` Flow 2.

## Anti-rationalization

Reject these shortcuts:
- asking the user "did you push?" when git state can answer that
- assuming remote operations succeeded without checking
- skipping context recovery and starting a task from stale state
- giving vague resumption advice instead of specific commands
- ignoring uncommitted changes when the user requests a new task

## References

| When needed | Read |
|-------------|------|
| Need detailed command templates for each handoff scenario | `references/handoff-commands.md` |
