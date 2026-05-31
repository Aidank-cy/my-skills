# AGENTS.md

## Language rule

Always think and respond in English regardless of the language used in
skill descriptions or trigger phrases. Internal reasoning, planning,
and all output must be in English.

This applies to:
- Chain-of-thought and intermediate reasoning
- Task decomposition and execution plans
- Commit messages and CHANGELOG entries
- Progress updates in `.harness/progress.md`
- All agent-generated content

## Chinese input trigger mapping

When the user inputs Chinese that is semantically equivalent to a
skill's English trigger phrases, treat it as a valid trigger for that
skill. The agent must still think, plan, and respond entirely in
English.

### prompt-gateway triggers

| Chinese input | Maps to |
|---|---|
| 添加功能 / 新增功能 | "add feature" |
| 修改功能 / 修改X | "modify X" |
| 修复 / 修bug | "fix bug" |
| 新增 / 新加 | "add new" |
| 实现X | "implement X" |
| 接下来修改 | "next change" |
| 下一个功能 | "next feature" |
| 重构 | "refactor" |
| 删除X / 移除X | "remove X" |

### git-workflow triggers

| Chinese input | Maps to |
|---|---|
| 提交代码 | "commit code" |
| 创建分支 | "create branch" |
| 切换分支 | "switch branch" |
| 合并分支 | "merge branch" |
| git操作 | "git operations" |
| 推送 / 推代码 | "push" |

### versioning-and-changelog triggers

| Chinese input | Maps to |
|---|---|
| 发版 / 发布 | "release" / "cut a release" |
| 更新版本 / 版本迭代 | "bump version" |
| 打标签 / 打tag | "tag a release" |
| 上线 | "ship it" |

### harness-init triggers

| Chinese input | Maps to |
|---|---|
| 新项目 / 新建项目 | "new project" |
| 创建项目 | "create a project" |
| 初始化项目 / 初始化仓库 | "init a repo" |
| 搭脚手架 | "scaffold a project" |
| harness项目 | "harness project" |

### harness-engineering-transform triggers

| Chinese input | Maps to |
|---|---|
| 让我的项目支持AI agent | "make my repo agent-friendly" |
| 给项目加约束 / 加规则 | "set up coding agent rules" |
| harness工程 | "harness engineering" |
| 添加agent规则 | "add agent rules" |
| 加钩子 / 加质量门禁 | "add hooks / quality gates" |

### harness-remote-handoff triggers

| Chinese input | Maps to |
|---|---|
| 继续 / 接着做 | "resume" / "continue" |
| 已推送 / 推了 | "I pushed" |
| CI挂了 / CI失败了 | "CI failed" |
| 项目状态 / 当前状态 | "check status" |
| 接下来做什么 | "what should I do next" |

### sync-filter triggers

| Chinese input | Maps to |
|---|---|
| 设置同步 | "set up dev-to-public sync" |
| 添加文件到同步 | "add a file to the sync workflow" |
| 这个文件公开还是私有 | "classify a file as private or public" |
| 调试同步失败 | "debug a sync push failure" |

### skill-authoring triggers

| Chinese input | Maps to |
|---|---|
| 写一个skill / 创建skill | "write a skill" |
| 审查skill / 检查skill | "review a skill" |
| 改进skill / 优化skill | "improve a skill" |
| 重构SKILL.md | "refactor a SKILL.md" |

## Behavior notes

- When Chinese input matches a trigger above, activate the
  corresponding skill immediately. Do not ask the user to rephrase
  in English.
- All generated artifacts (code, docs, commits, changelogs, plans)
  must be in English regardless of user input language.
- If the user communicates in Chinese, respond in English but
  acknowledge understanding of their request.
- Audit skill anti-rationalization sections every 3+ phases.
  Remove entries that have never been triggered by a real failure.
- When a skill exceeds the 500-line / 3000-word budget, refactor
  before adding new content.
