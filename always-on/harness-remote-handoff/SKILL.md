---
name: harness-remote-handoff
description: >
  This skill should be used when the user returns after performing
  remote git operations (push, release publish), asks "what should
  I do next" after a task completes, reports CI failure after pushing,
  says things like "I pushed", "CI failed", "already pushed", "CI broke",
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

The agent has already merged to main. Present the output in this
order: summary → verification → push.

```
✅ Task merged to main locally.

Verify the changes:
  git diff HEAD~1                    # review what changed
  {build_command}                    # confirm build passes
  {inspect_command}                  # visually inspect the result

Sync to remote:
  git push origin main
```

Replace `{build_command}` and `{inspect_command}` with the project's
real commands. Every verification command must be runnable as-is.
Tailor to what the task actually changed:
- Visual change → include dev server URL or page path
- API change → include a curl or test command
- Config change → include a way to confirm the config loads
- Test change → include the specific test suite command

If the project accumulates multiple tasks before pushing, all
merged commits go up in one push.

For release, hotfix, PR workflow, and presentation variants, read
`references/handoff-scenarios.md`.

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

For resume phrase routing and common gap handling, read
`references/handoff-scenarios.md`.

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
- Keeping rules that have never been triggered by a real failure
- Treating skill file count or word count as a quality signal

## References

| When needed | Read |
|---|---|
| Need command templates for release, hotfix, or PR handoff | `references/handoff-scenarios.md` |
| Need standard handoff commands | `references/handoff-commands.md` |
