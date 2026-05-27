# Agent Harness 管理入口

状态：高优先级项目管理文档  
适用范围：`st-platform` 后续通过 Planner / Generator / Evaluator 三智能体推进的代码实现、测试、评审和审计留痕

## 1. 文档优先级

后续涉及 agent 编码、任务拆分、实现验收和审计留痕时，优先级按以下顺序处理：

1. 用户当前明确指令。
2. `docs/harness/agent_coding_governance.md`。
3. `docs/benchmark_platform_design_plan.md`。
4. `docs/st_platform_project_management_spec.md`。
5. 其他已有设计文档和 README。

如果文档之间冲突，应在本目录下新增或更新会话记录，说明冲突点、采用的决策和影响范围。

## 2. 目录用途

```text
docs/harness/
├─ README.md                         # 本入口文档
├─ agent_coding_governance.md         # agent 编码治理和固定记录格式
├─ project_structure_map.md           # 当前项目结构审计
├─ sessions/                          # 每轮对话和操作的审计记录
├─ tasks/                             # 具体任务包：需求、约束、验收、状态
├─ sprints/                           # 每个实现 sprint 的 contract 和交付记录
├─ reviews/                           # Evaluator 独立评审报告
├─ artifacts/                         # 产物清单，不存放大型二进制产物
├─ data/                              # 数据集清单、来源、checksum、字段说明
├─ decisions/                         # 关键架构/范围决策记录
├─ prompts/                           # Planner / Generator / Evaluator 提示词配置
└─ templates/                         # 固定记录模板
```

## 3. 基本原则

- 每一轮重要对话都必须在 `sessions/` 留下记录。
- 每个可执行任务都必须在 `tasks/` 有独立任务包。
- 每个编码 sprint 都必须先有 contract，再有实现，再有 evaluator report。
- 真实运行产物可以继续放在 `runs/` 或 `presentation_results/`，但必须在 `artifacts/` 中登记清单。
- 大型原始数据不放入 `docs/harness/`，只记录来源、版本、路径、checksum 和字段映射。

