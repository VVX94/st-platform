# Decision: 平台首期批量默认决策

日期：2026-05-27  
状态：accepted  
关联文档：`docs/benchmark_platform_design_plan.md`

## 背景

用户一次性确认了后端框架、OSS 数据流、公开访问策略、前端技术栈、算法镜像策略、指标范围、数据集首期范围、部署验收和 harness/CI 审计要求。

## 决策

1. 后端采用 FastAPI + Pydantic schema。
2. SQLite 访问层采用 SQLAlchemy / SQLModel，不直接使用裸 `sqlite3`。
3. OSS 数据登记支持 `oss://bucket/key` 和 `oss://bucket/prefix/`。
4. 浏览器上传优先使用 OSS 预签名 URL；服务端只负责签名、校验和登记 metadata。
5. 项目是公益科研网站，公开匿名使用，不做登录、用户系统、RBAC 或 API 权限校验。
6. 前端采用 React + Vite + TypeScript。
7. 主 Docker 镜像保持轻量，重依赖算法后续拆成可选 runner 镜像或独立环境。
8. 首期指标固定为 `core_spatial_v1`：ARI、NMI、runtime、spatial neighbor agreement、artifact completeness。
9. STARmap 作为 smoke demo；DLPFC 151673 和 osmFISH 首期要求可登记和解析 metadata，完整 benchmark 后续推进。
10. Docker Compose 验收必须跑通 Web、API、SQLite、OSS 写读、dataset 登记、experiment 创建、worker smoke run、OSS artifact 和 Web 报告查看。
11. 每个 sprint 必须包含 task spec、sprint contract、generator handoff、evaluator report 和 Git commit。

## 影响

- 主文档不再把登录/RBAC列为未来必须能力。
- API 设计应面向公开匿名使用，但保留格式校验、规模限制和低并发保护。
- 后续实现时应优先交付 STARmap smoke 链路，而不是一次性跑通所有示例数据。
- 产物继续只写 manifest，不进入 Git。

