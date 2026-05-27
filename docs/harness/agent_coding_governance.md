# Agent 编码治理与审计规范

状态：高优先级规范  
适用范围：后续通过 Planner / Generator / Evaluator 三智能体推进 `st-platform` benchmark Web 平台实现的全部任务  
参考思路：Anthropic Engineering, "Harness design for long-running application development", 2026-03-24, https://www.anthropic.com/engineering/harness-design-long-running-apps

## 1. 目标

本规范用于保证每一轮 agent 编码都有可追踪、可复现、可审计的文件记录。后续不应只依赖聊天上下文判断项目状态，所有关键决策、任务输入、实现边界、验证命令、失败原因和产物位置都应写入本目录。

核心目标：

- 让 Planner / Generator / Evaluator 三个角色有明确分工。
- 让每个任务在编码前有可验收 contract。
- 让每轮实现后有独立 evaluator 报告。
- 让数据、运行结果和报告产物有 manifest。
- 让后续审计可以从文件系统恢复每一轮工作。
- 让每轮任务结束后都有对应 Git 提交，方便后续按提交审计和回滚。

## 2. Harness 模式

后续采用三角色闭环：

```text
用户目标
  -> Planner 生成或更新 spec、任务包、验收标准
  -> Generator 基于任务包提出 sprint contract
  -> Evaluator 审核 contract 是否可测
  -> Generator 实现代码并自测
  -> Evaluator 独立运行项目、测试 UI/API/worker/artifact
  -> 通过则进入下一任务，不通过则退回 Generator 修复
```

每轮任务闭环必须同时满足：

1. 会话记录已更新。
2. 任务包或 sprint 包状态已更新。
3. 验证命令和结果已记录。
4. 中间产物已写入 manifest 或被 `.gitignore` 排除。
5. 已创建一个只包含应纳入版本控制内容的 Git 提交。

### 2.1 Planner

职责：

- 把用户目标转成可执行 spec、任务包和验收标准。
- 维护 `docs/harness/tasks/`、`docs/harness/sprints/` 的计划文件。
- 识别依赖关系、风险、范围边界和优先级。

限制：

- 不直接修改运行时代码。
- 不把低层实现细节写死到不可调整的程度。
- 不替 Generator 宣称实现完成。

### 2.2 Generator

职责：

- 每次只实现一个 contract 明确的 sprint。
- 修改代码、测试、脚本和必要文档。
- 自测并写 `generator_handoff.md`。

限制：

- 不能跳过 sprint contract 直接编码。
- 不能把 stub 冒充完整功能。
- 不能批准自己的工作。

### 2.3 Evaluator

职责：

- 独立验证 sprint contract。
- 运行测试、启动服务、点击 Web、检查 API、检查数据库状态和 artifact。
- 写 `evaluator_report.md` 和 `acceptance_status.md`。

限制：

- 默认不修主实现代码。
- 不能因为功能“看起来差不多”而通过核心流程失败的 sprint。
- 如果无法验证，必须标记 blocked，而不是 passed。

### 2.4 Context Reset Protocol

上下文 reset 是 harness 的常规操作，不应被视为异常。目标是降低长对话中的遗漏、漂移和上下文焦虑，让后续 agent 可以从文件系统恢复状态，而不是依赖完整聊天历史。

触发条件：

- 一个 sprint 完成并已提交 Git。
- 上下文过长，agent 开始需要反复回忆旧决策。
- Generator 或 Evaluator 无法明确回答当前任务、验收标准、已改文件、剩余风险。
- 用户要求进入下一轮任务。
- 发生连续失败，需要重新收束任务边界。

reset 前必须完成：

1. 更新当前 `docs/harness/sessions/YYYY-MM-DD-HHMM-<topic>.md`。
2. 更新关联 `task_spec.md`、`status.md` 或 `sprint_contract.md`。
3. 如果有实现改动，写 `generator_handoff.md`。
4. 如果有评审，写 `evaluator_report.md` 和 `acceptance_status.md`。
5. 记录验证命令、失败原因、未决问题和下一步。
6. 检查中间产物是否被 `.gitignore` 排除或写入 manifest。
7. 创建 Git 提交。

reset 后恢复时只读取最小入口：

1. `docs/harness/README.md`。
2. `docs/harness/agent_coding_governance.md`。
3. `docs/harness/project_structure_map.md`。
4. 当前任务的 `task_spec.md` 和 `status.md`。
5. 当前 sprint 的 `sprint_contract.md`、最近 `generator_handoff.md`、最近 `evaluator_report.md`。
6. 最近 1-3 个相关 session record。
7. 必要时再读取 `docs/benchmark_platform_design_plan.md` 的相关章节。

reset 后禁止：

- 依赖“我记得之前说过”作为依据。
- 重新扫描全仓库替代读取当前任务包。
- 在未恢复当前 task / sprint 状态前直接编码。
- 把旧聊天内容中的未落盘信息当作已确认事实。

### 2.5 Skill / Tool Policy

每个 sprint contract 必须声明本轮需要使用的工具和验证方式。Generator 可以补测试工具，Evaluator 必须独立运行验证；如果关键工具不可用，应标记 blocked 或先创建“测试设施补齐”任务。

任务类型和最低工具要求：

| 任务类型 | Generator 必须做 | Evaluator 必须验证 |
|---|---|---|
| 后端 API | 添加/更新 API 测试或 smoke 脚本 | 运行 API 测试，检查请求/响应、错误码和持久化状态 |
| Worker / 队列 | 添加状态流转和失败路径测试 | 验证 queued -> running -> succeeded/failed，检查重试/错误记录边界 |
| 数据 / OSS | 添加 reader、URI、临时缓存和清理测试 | 验证 OSS URI 读写策略、SQLite 索引、本地临时文件清理 |
| 算法 adapter | 添加小数据 smoke test | 运行真实小数据或 demo 数据，检查 artifact 和错误信息 |
| 指标 / 报告 | 添加固定输入的指标测试 | 检查 CSV/Markdown/图表 artifact 真实生成且指标非伪造 |
| 前端 UI | 遵循当前环境可用的前端设计规范；若存在前端设计 skill，应先使用并记录 | 使用 Playwright 或等价浏览器 E2E 工具点击核心流程、截图检查、验证无明显布局遮挡 |
| 部署 | 提供 Compose/env/healthcheck smoke 方案 | 验证服务可启动、API 可访问、worker 可运行、OSS/SQLite 配置可用 |

前端设计补充要求：

- 设计阶段必须先确认用户工作流，而不是只堆页面。
- 如果当前环境提供专门的前端设计 skill，应在 session record 中记录使用情况。
- 如果没有专门 skill，应按项目内前端设计约束执行，并在 sprint contract 中写明 fallback。
- 前端验收不能只靠截图，必须覆盖至少一个用户可完成的操作流。

Playwright / 浏览器验证要求：

- 涉及 React 页面、布局、导航、表单、报告展示或下载的 sprint，默认需要 Playwright。
- 若 Playwright 未安装，Generator 应把安装和最小 E2E 脚本纳入 sprint，或单独创建测试设施任务。
- Evaluator 必须记录启动命令、浏览器测试命令、截图或失败证据。
- 如果无法启动浏览器或服务，结论为 blocked，不得标记 passed。

## 3. 目录和命名

### 3.1 会话记录

每一轮重要对话创建一个文件：

```text
docs/harness/sessions/YYYY-MM-DD-HHMM-<topic>.md
```

用途：

- 记录用户请求。
- 记录本轮做了什么。
- 记录修改了哪些文件。
- 记录运行了哪些验证。
- 记录下一步等待用户确认的事项。

### 3.2 任务包

每个可执行任务创建一个目录：

```text
docs/harness/tasks/TASK-YYYYMMDD-NNN-<slug>/
├─ task_spec.md
├─ planner_notes.md
├─ data_manifest.md
├─ artifact_manifest.md
└─ status.md
```

任务包用于跨多轮对话持续追踪一个功能目标。

### 3.3 Sprint 包

每个编码 sprint 创建一个目录：

```text
docs/harness/sprints/SPRINT-YYYYMMDD-NNN-<slug>/
├─ sprint_contract.md
├─ generator_handoff.md
├─ evaluator_report.md
├─ acceptance_status.md
└─ changed_files.md
```

Sprint 包用于约束“这一次具体实现什么”和“如何判定完成”。

### 3.4 Review 包

独立评审或回归检查放在：

```text
docs/harness/reviews/REVIEW-YYYYMMDD-NNN-<slug>.md
```

### 3.5 Data 和 Artifact manifest

大型数据和二进制产物不直接放入 `docs/harness/`。只保存 manifest：

```text
docs/harness/data/DATA-YYYYMMDD-NNN-<dataset>.md
docs/harness/artifacts/ARTIFACTS-YYYYMMDD-NNN-<experiment>.md
```

## 4. Git 和产物管理

### 4.1 每轮任务必须提交

每完成一轮 task 或 sprint，必须创建一次 Git 提交。提交信息建议格式：

```text
docs(harness): record <task-or-sprint-id>
feat(api): implement <task-or-sprint-id>
fix(worker): address evaluator findings for <task-or-sprint-id>
```

如果某轮被 Evaluator 判定为 failed 或 blocked：

- 已通过验证的文档、报告和问题清单仍应提交，形成审计快照。
- 未通过的运行时代码默认不合入主提交；如必须保留，应使用明确的 WIP 提交信息，并在 `acceptance_status.md` 标记 failed 或 blocked。
- 不允许在最终回复中宣称该轮完成。

### 4.2 Git 提交白名单

默认允许进入 Git 的内容：

- `src/` 下源码。
- `tests/` 下测试。
- `docs/` 下规范、任务包、评审、manifest 和会话记录。
- `scripts/` 下可复现脚本。
- `web/` 下前端源码和配置。
- `deploy/` 下部署配置。
- `pyproject.toml`、`README.md`、`.gitignore` 等项目配置。

### 4.3 Git 提交黑名单

默认不进入 Git 的内容：

- `runs/` 运行目录。
- 本地虚拟环境和缓存。
- 上传数据、原始数据和预处理中间数据。
- SQLite / Postgres dump / queue state 等本地数据库文件。
- 模型权重、训练 checkpoint、临时 embedding。
- 生成的 CSV、JSON、PNG、PDF、HTML 报告。
- 前端构建产物和 `node_modules/`。

这些内容如需审计，只记录到 `docs/harness/data/` 或 `docs/harness/artifacts/` manifest 中。

## 5. 固定记录格式

### 5.1 Session Record

```markdown
# Session: <topic>

日期：
参与角色：
关联任务：

## 用户请求

## 本轮上下文

## 执行动作

| 步骤 | 动作 | 文件/命令 | 结果 |
|---|---|---|---|

## 修改文件

| 文件 | 修改类型 | 说明 |
|---|---|---|

## 验证记录

| 命令/检查 | 结果 | 备注 |
|---|---|---|

## 决策

## 风险和阻塞

## 下一步
```

### 5.2 Task Spec

```markdown
# Task: <name>

任务 ID：
状态：draft / ready / in_progress / blocked / done
负责人角色：
创建日期：

## 背景

## 目标

## 非目标

## 输入

## 输出

## 影响范围

## 验收标准

## 依赖

## 风险

## 审计要求
```

### 5.3 Sprint Contract

```markdown
# Sprint Contract: <name>

Sprint ID：
关联任务：
状态：draft / agreed / implemented / evaluating / accepted / rejected

## 本轮目标

## 明确不做

## 预期改动文件

## 用户可见行为

## API / 数据库 / 前端变更

## 验收测试

| 验收点 | 验证方式 | 必须通过 |
|---|---|---|

## 回滚和兼容性

## Evaluator 审核意见
```

### 5.4 Generator Handoff

```markdown
# Generator Handoff: <name>

关联 sprint：
生成日期：

## 实现摘要

## 文件变更

| 文件 | 说明 |
|---|---|

## 自测命令

| 命令 | 结果 |
|---|---|

## 已知问题

## 需要 Evaluator 重点检查
```

### 5.5 Evaluator Report

```markdown
# Evaluator Report: <name>

关联 sprint：
评估日期：
结论：passed / failed / blocked

## 验证环境

## Contract 覆盖检查

| 验收点 | 结果 | 证据 |
|---|---|---|

## UI 检查

## API 检查

## Worker / 数据库 / Artifact 检查

## 发现的问题

| 严重级别 | 问题 | 证据 | 建议 |
|---|---|---|---|

## 最终结论
```

### 5.6 Data Manifest

```markdown
# Data Manifest: <dataset>

数据 ID：
来源：
本地路径：
格式：
样本规模：
标签列：
空间坐标字段：
checksum：
许可/引用：

## 字段映射

## 预处理记录

## 可用于哪些测试
```

### 5.7 Artifact Manifest

```markdown
# Artifact Manifest: <experiment or run>

产物 ID：
关联任务：
关联 run：
生成日期：

## 产物列表

| 路径 | 类型 | 生成命令 | 用途 |
|---|---|---|---|

## 指标摘要

## 可复现命令

## 注意事项
```

## 6. 通过/失败规则

Evaluator 必须使用硬阈值：

- 核心用户流程失败：failed。
- UI 显示成功但后端 run 失败：failed。
- 生成空 artifact 或假指标：failed。
- 使用 stub 冒充真实 benchmark：failed。
- 无法复现或缺少验证命令：blocked。
- 只有文档改动但任务要求实现代码：failed。

## 7. Benchmark 平台专用验收链路

完整平台 sprint 涉及运行能力时，至少覆盖以下链路之一：

```text
登记/上传数据集 -> 选择算法 -> 创建 experiment -> worker 执行 run
-> 写入 metrics/artifacts -> Web 展示 -> 下载报告
```

如果 sprint 只实现链路的一部分，contract 必须写明本轮覆盖的边界和后续缺口。

## 8. 审计最低要求

每轮结束前必须完成：

1. 更新 `docs/harness/sessions/` 中的会话记录。
2. 如果创建或推进任务，更新对应 `tasks/` 或 `sprints/` 文件。
3. 记录所有验证命令和结果。
4. 记录未解决风险。
5. 检查 `.gitignore` 是否覆盖本轮产生的中间文件。
6. 创建本轮 Git 提交，且不包含黑名单产物。
7. 在最终回复中说明修改文件、验证结果、提交哈希和下一步确认项。
