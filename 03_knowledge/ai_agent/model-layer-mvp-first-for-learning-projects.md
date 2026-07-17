# 学习型 Agent 项目的模型层应先做单 Provider MVP 再扩展

## 元数据

- 状态：已验证
- 类型：架构判断
- 领域：ai_agent
- 最后更新：2026-07-14
- 标签：agent, model-layer, mvp, architecture, learning-project

## 用户动作/判断来源

- 用户要求按边学边开发方式评估 ChatGPT 给出的完整模型层蓝图
- 用户确认采用单 provider MVP 路线，并继续落地实现模型调用层
- 本次实现产物包括统一 schemas、OpenAI provider、ModelService、/api/chat 路由和测试

## 适用条件

- 项目仍处于早期学习阶段，需要先建立清晰、可运行、可验证的最小闭环
- 上层能力尚未大量依赖模型层，重抽象的边际收益低于实现成本
- 目标是先隔离 provider 细节，为后续 Tool Calling、Agent Loop 提供统一入口

## 核心内容

- 模型层第一版优先统一 message、request、response、usage 和 service 入口，而不是先做完整平台抽象。
- 第一版只接一个 provider 即可，重点是证明上层不直接依赖 SDK 或 provider 细节。
- 推荐先打通 Provider -> Service -> API 的最小链路，再补 streaming、retry、logging 和多 provider。
- 如果当前主要目标是学习与验证，过早引入 manager、全家桶 provider 适配和复杂可扩展设计，通常会增加理解成本并削弱阶段成果的清晰度。

## 边界与例外

- 当系统已明确需要同时支持多家模型、复杂路由策略或生产级容错时，这条做法不足以覆盖全部需求。
- 如果项目目标不是学习型 MVP，而是直接交付稳定生产平台，则应提前补上更完整的 provider 抽象和运行保障。

## 失效风险

中；当项目进入多 provider、流式输出或复杂运维阶段后，需要补充新的分层与能力。

## 关联项

- project_20260713_001

## 待确认或待验证

- 无
