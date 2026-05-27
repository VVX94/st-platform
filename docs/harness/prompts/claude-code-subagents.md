# Claude Code Subagent Configuration

日期：2026-05-27  
状态：active

Claude Code 项目级 subagent 文件已放在：

```text
.claude/agents/planner.md
.claude/agents/generator.md
.claude/agents/evaluator.md
```

这些文件采用 Claude Code 官方格式：

```text
---
name: <agent-name>
description: <when to invoke this subagent>
model: inherit
tools: <allowed Claude Code tools>
color: <ui color>
---

<system prompt body>
```

使用方式：

```text
@agent-planner create the next sprint contract
@agent-generator implement the approved sprint
@agent-evaluator evaluate the sprint contract and generator handoff
```

也可以使用项目命令：

```text
/start-st-platform-longrun
```

Claude Code 会在会话启动时加载项目级 subagent。如果新增或修改 `.claude/agents/*.md` 后当前会话没有识别到这些 agent，需要重启 Claude Code。

`.claude/commands/start-st-platform-longrun.md` 仍可用；Claude Code 当前更推荐 skills，但官方文档说明 `.claude/commands/` 文件仍然工作。后续如果需要更复杂的支持文件，可以把该命令迁移为 `.claude/skills/start-st-platform-longrun/SKILL.md`。

设计原则：

- Planner / Generator / Evaluator 分离，避免同一个 agent 同时规划、实现和批准。
- 通过 `docs/harness/` 文件交接，不依赖聊天上下文。
- 每轮 sprint 必须可验证、可审计、可提交。
- 当前目标是保证程序能运行；Docker 化后置。
