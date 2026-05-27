# Session: agent harness structure setup

日期：2026-05-27  
参与角色：Planner  
关联任务：建立后续 agent 编码审计结构

## 用户请求

用户希望在写入 Planner / Generator / Evaluator 三智能体配置之前，先梳理整个项目目前结构，并建立一个通过 spec 管理 agent 编码情况的机制。每一轮对话都需要留下详尽文档、数据和产物记录，方便后期审计。

## 本轮上下文

- 当前项目根目录：`/home/wx/project/aaa/spatial-transcriptomic/经典算法/st-platform`
- 当前目标文档：`docs/benchmark_platform_design_plan.md`
- 已确认第 1 条修改：目标文档定位升级为完整可部署 Web benchmark 平台实施总纲。
- 第 2 条原方案按模块拆 agent 已被用户否定，改为参考 Anthropic harness 的 Planner / Generator / Evaluator 三角色。

## 执行动作

| 步骤 | 动作 | 文件/命令 | 结果 |
|---|---|---|---|
| 1 | 读取 skill 规则 | `read-repo`、`planning-with-files-zh` | 确认需要先梳理结构并持久化计划/发现 |
| 2 | 审计仓库结构 | `repo_inventory.py --max-depth 3` | 确认项目是 Python 包，入口为 CLI，当前无 Web/API |
| 3 | 读取入口文件 | `pyproject.toml`、`README.md`、`src/st_platform/cli.py`、`workflows/service.py` | 确认现有运行边界 |
| 4 | 读取现有文档标题 | `docs/*.md` | 确认已有架构、路线图、项目管理和 benchmark 设计文档 |
| 5 | 创建 harness 目录 | `docs/harness/*` | 为后续任务、会话、评审、数据和产物清单预留位置 |

## 修改文件

| 文件 | 修改类型 | 说明 |
|---|---|---|
| `docs/harness/README.md` | 新增 | Agent harness 管理入口 |
| `docs/harness/project_structure_map.md` | 新增 | 当前项目结构审计 |
| `docs/harness/agent_coding_governance.md` | 新增 | Agent 编码治理和固定记录格式 |
| `docs/harness/sessions/2026-05-27-agent-audit-structure.md` | 新增 | 本轮会话审计记录 |
| `docs/harness/templates/*.md` | 新增 | 后续记录模板 |
| `docs/harness/*/.gitkeep` | 新增 | 保留空目录 |

## 验证记录

| 命令/检查 | 结果 | 备注 |
|---|---|---|
| `find docs/harness -maxdepth 3 -type f` | 通过 | 确认 README、治理规范、结构审计、模板、会话记录和 `.gitkeep` 文件均已创建 |
| `rg "Planner|Generator|Evaluator|Session Record|Sprint Contract" docs/harness docs/benchmark_platform_design_plan.md` | 通过 | 确认关键 harness 术语和固定格式可检索 |
| `git status --short docs/benchmark_platform_design_plan.md docs/harness` | 通过 | 确认本轮只涉及 benchmark 目标文档和 `docs/harness/` 审计骨架 |

## 决策

- 使用 `docs/harness/` 作为后续 agent 编码审计根目录。
- 不把大型真实数据和二进制运行产物放入 `docs/harness/`。
- 使用 manifest 记录数据和 artifact 的路径、来源、checksum、生成命令和用途。
- 后续每轮对话至少新增或更新一个 session record。

## 风险和阻塞

- 当前只建立治理和审计骨架，尚未把 Planner / Generator / Evaluator 三角色配置写入主目标文档。
- 当前还没有实际 task 包和 sprint 包；后续进入实现前必须创建。

## 下一步

等待用户确认是否把 Planner / Generator / Evaluator harness 配置写入 `docs/benchmark_platform_design_plan.md`。
