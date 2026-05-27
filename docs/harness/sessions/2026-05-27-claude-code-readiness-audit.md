# Session: Claude Code readiness audit

日期：2026-05-27  
参与角色：Planner  
关联任务：确认 Claude Code 长时间运行准备情况

## 用户请求

用户要求确认：

1. 当前核心规则文档有没有旧内容残留。
2. 当前只需要保证程序能运行，Docker 化可以项目完成后再打包，这和文档是否一致。
3. Planner / Generator / Evaluator 三个智能体提示词和交流协作方式是否按 Claude Code 要求形式写好，并符合 Anthropic harness 思路。
4. 核心算法指标、可视化等内容是否已有对应展示工具和设计。

## 审计结论

- 主目标文档仍有 Docker Compose 作为首期验收目标的旧表述，已修正为“先保证程序运行，Docker 后置打包”。
- `.claude/agents/` 原本不存在，已新增 Planner / Generator / Evaluator 三个项目级 subagent。
- 新增 `CLAUDE.md` 作为 Claude Code 项目入口规则。
- 新增 `.claude/commands/start-st-platform-longrun.md` 作为长任务启动命令。
- 根据 Claude Code 官方 subagent 文档，项目级 subagent 放在 `.claude/agents/*.md`，使用 YAML frontmatter；已补充 `model`、`tools`、`color` 字段。
- 根据 Claude Code 当前 slash/skill 文档，`.claude/commands/` 仍可用；已为项目命令补充 frontmatter。
- 指标和可视化已有设计、历史演示产物和首期验收标准，但 Web 展示工具还没有完整实现；后续长任务需要优先把 STARmap smoke 链路跑通。
- 已新增首个可执行 task 和 sprint contract，便于 Claude Code 直接开始长任务。

## 修改文件

| 文件 | 修改类型 | 说明 |
|---|---|---|
| `CLAUDE.md` | 新增 | Claude Code 项目入口规则 |
| `.claude/agents/planner.md` | 新增 | Planner subagent |
| `.claude/agents/generator.md` | 新增 | Generator subagent |
| `.claude/agents/evaluator.md` | 新增 | Evaluator subagent |
| `.claude/commands/start-st-platform-longrun.md` | 新增 | Claude Code 长任务启动命令 |
| `docs/benchmark_platform_design_plan.md` | 修改 | Docker 后置、运行优先 |
| `docs/harness/decisions/2026-05-27-deployment-target.md` | 修改 | 标注 Docker 首期顺序已修正 |
| `docs/harness/decisions/2026-05-27-runtime-first-docker-later.md` | 新增 | 运行优先、Docker 后置决策 |
| `docs/harness/prompts/claude-code-subagents.md` | 新增 | Claude Code subagent 配置说明 |
| `docs/harness/tasks/TASK-20260527-001-runtime-smoke-platform/` | 新增 | 首个长任务 task spec |
| `docs/harness/sprints/SPRINT-20260527-001-runtime-foundation/` | 新增 | 首个可执行 sprint contract |

## 验证记录

| 命令/检查 | 结果 | 备注 |
|---|---|---|
| Claude Code 官方 subagent 文档 | 通过 | 项目级 subagent 使用 `.claude/agents/*.md` + YAML frontmatter |
| Claude Code 官方 commands/skills 文档 | 通过 | `.claude/commands/` 仍可用；后续复杂命令可迁移为 skill |
| `find .claude docs/harness/prompts -maxdepth 3 -type f` | 通过 | 检查 Claude Code agent、command 和 prompt 说明存在 |
| `rg "Docker Compose|Docker 化|先保证程序|planner|generator|evaluator|core_spatial_v1|可视化" docs/benchmark_platform_design_plan.md CLAUDE.md .claude docs/harness` | 通过 | 检查关键规则 |
| 旧 Docker 首期验收冲突检查 | 通过 | 核心规则和决策已改为程序运行优先，Docker 打包后置 |
| 首轮任务入口检查 | 通过 | `TASK-20260527-001-runtime-smoke-platform` 和 `SPRINT-20260527-001-runtime-foundation` 已创建 |
| `PYTHONPATH=src python -m pytest` | 失败 | 当前系统没有 `python` 命令，已把 Claude 指南改为 `python3` |
| `PYTHONPATH=src python3 -m pytest` | 失败 | 当前 Python 环境未安装 `pytest`，需要 Claude Code 后续使用 uv/venv 安装 dev 依赖或使用 `.venv-spagcn` |
| `PYTHONPATH=src python3 -m st_platform list-algorithms` | 通过 | 算法 registry 可列出已接入算法 |
| `PYTHONPATH=src python3 -m st_platform run-demo --task domain_detection --algorithm spagcn-lite` | 通过 | 轻量 demo 成功，生成的 `runs/` 产物被 `.gitignore` 排除 |
| `git commit -- ...` | 通过 | 创建本轮审计提交；提交哈希见最终回复 |

## 下一步

提交本轮 Git 快照，然后向用户说明如何启动 Claude Code 长任务。
