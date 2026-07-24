# AI Workbench 的能力层、素材层与模型适配分层方法

## 元数据

- 状态：待验证
- 类型：架构判断
- 领域：ai_agent
- 最后更新：2026-07-24
- 标签：ai_agent, Workbench, hexagonal, command-handler, assetId, worker

## 用户动作/判断来源

- 用户对 Workbench 多次入口回归的复盘
- 本次确认的分阶段架构治理方案

## 适用条件

- 已有聊天入口、工具入口和 MCP/扩展兼容入口
- 能力同时涉及图片、视频、文件和异步任务
- 模型供应商和请求协议会变化

## 核心内容

- 采用模块化单体 + Ports & Adapters；能力注册表和类型化 Command Bus 是唯一业务入口。
- API/chat 只做鉴权、消息解析、编排和流式输出；业务能力、数据库和 provider 调用下沉到模块。
- 统一逻辑 assetId，内部映射 local-storage/toolbox/tos/remote-url 等 location；UI 用结构化 data-asset 消息部件，不把 fileId 文本标记或 Base64 历史当协议。
- 聊天模型是输入适配器/规划器，显式工具入口绕过模型并直接执行同一命令；视觉、图片生成和视频模型通过 provider profile 与能力矩阵适配。
- Web 进程只持久化 job，独立 Worker 负责 lease、heartbeat、retry、幂等和恢复；JobQueuePort 为未来替换队列保留接口。
- 用类型化错误和 traceId 贯穿入口、能力、provider 与 Worker，兼容旧 API/MCP/扩展由适配器承担。

## 边界与例外

- 不在当前阶段引入 Temporal/Redis 等新基础设施
- 不以一次性重写替代可回滚的分阶段迁移
- 不允许聊天入口和工具入口各自实现一套业务逻辑

## 失效风险

中：具体 SDK 和 provider 协议会变化，但入口与业务命令分离、逻辑素材 ID、Worker 边界等原则较稳定。

## 关联项

- 04_cases/decision_cases.jsonl: 新增 Workbench 架构治理决策
- 04_cases/failure_cases.jsonl: failure_20260722_001

## 待确认或待验证

- 无
