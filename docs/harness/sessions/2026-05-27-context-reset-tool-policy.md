# Session: context reset and tool policy

日期：2026-05-27  
参与角色：Planner  
关联任务：补充 agent context reset 和工具验证策略

## 用户请求

用户要求把两条 agent 协作能力写入文档：

1. 上下文过长时自动 reset，避免上下文焦虑。
2. 验证效果时 agent 自己使用 Playwright 等 skill 测试，设计前端时使用对应前端设计 skill。

## 本轮上下文

- 当前 harness 已采用 Planner / Generator / Evaluator。
- 已要求每轮只做一个工作点，并每轮任务结束后 Git 提交。
- 需要把 reset 和工具策略写成可执行治理规则，而不是只写原则。

## 执行动作

| 步骤 | 动作 | 文件/命令 | 结果 |
|---|---|---|---|
| 1 | 读取治理规范 | `sed -n '1,260p' docs/harness/agent_coding_governance.md` | 找到适合新增 reset 和 tool policy 的位置 |
| 2 | 读取目标文档 | `sed -n '1,130p' docs/benchmark_platform_design_plan.md` | 找到多智能体 harness 配置章节 |
| 3 | 新增 Context Reset Protocol | `docs/harness/agent_coding_governance.md` | 写入触发条件、reset 前后读写规则和禁止事项 |
| 4 | 新增 Skill / Tool Policy | `docs/harness/agent_coding_governance.md` | 写入 API、worker、OSS、算法、报告、前端、部署的最低工具要求 |
| 5 | 同步目标文档摘要 | `docs/benchmark_platform_design_plan.md` | 在 harness 配置中加入上下文和工具约束 |

## 修改文件

| 文件 | 修改类型 | 说明 |
|---|---|---|
| `docs/harness/agent_coding_governance.md` | 修改 | 新增 Context Reset Protocol 和 Skill / Tool Policy |
| `docs/benchmark_platform_design_plan.md` | 修改 | 同步多智能体上下文和工具约束 |
| `docs/harness/sessions/2026-05-27-context-reset-tool-policy.md` | 新增 | 本轮审计记录 |

## 验证记录

| 命令/检查 | 结果 | 备注 |
|---|---|---|
| `rg "Context Reset Protocol|Skill / Tool Policy|Playwright|front|前端设计|blocked|handoff" docs/benchmark_platform_design_plan.md docs/harness/agent_coding_governance.md docs/harness/sessions/2026-05-27-context-reset-tool-policy.md` | 通过 | 检查关键策略已写入 |
| `git commit -- docs/benchmark_platform_design_plan.md docs/harness/agent_coding_governance.md docs/harness/sessions/2026-05-27-context-reset-tool-policy.md` | 通过 | 创建本轮审计提交；提交哈希见最终回复 |

## 决策

- reset 是常规流程，不是异常。
- reset 前必须写 session、状态、handoff、评审和 Git 提交。
- reset 后只读最小入口文档恢复上下文。
- 前端 sprint 默认要求 Playwright 或等价浏览器 E2E。
- 如果关键测试工具不存在，先补测试设施或标记 blocked。

## 风险和阻塞

- 当前仓库还没有 React 项目和 Playwright 配置；后续前端 sprint 需要先补测试设施。
- 当前没有明确名为 `frontdesign` 的 skill；文档采用“如果环境提供前端设计 skill 则必须使用，否则按项目内前端设计约束并记录 fallback”的方式约束。

## 下一步

验证关键策略并提交本轮 Git 快照。
