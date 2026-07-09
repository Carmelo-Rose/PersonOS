# Hermes Agent 与 Mono 的定位关系与集成深度

## 元数据

- 状态：待验证
- 类型：架构判断
- 领域：ai_agent
- 最后更新：2026-07-07
- 标签：架构, Agent, Mono, Hermes, 集成

## 用户动作/判断来源

- 对 Mono 项目中 hermes 后端链路的技术探查
- current conversation：资产盘点与方向讨论

## 适用条件

- 当 Mono 项目需要评估 Agent 能力时
- 当决定集成外部 Agent 框架时
- 当需要向他人解释 Mono 架构时

## 核心内容

Mono 项目（~/Documents/Claude/code/chrome/Mono/）是一个 Chrome 扩展 + Web 前端项目，Hermes Agent（~/Documents/Claude/code/hermes-agent/）是外部克隆的完整开源 Agent 引擎。两者是独立项目，通过 HTTP 调用连接，Mono 未重写任何 Agent 核心代码。当前集成仅通聊天 API，Hermes 的工具（60+ 内置工具）、持久记忆（FTS5 召回）、技能系统（自主创建与改进）、子 Agent 调度、定时 cron、多消息平台能力全部闲置。正确方向是 Hermes 做内核引擎，Mono 的插件工具（图片反推、视频反推、Image2、素材下载）注册为 Hermes 工具，web 前端做终端界面

## 边界与例外

- 该判断基于 hermes-agent 0.18.0 版本，后续版本变更可能影响挂载方案
- 仅适用于当前 Mono + Hermes 并存的资产结构

## 失效风险

如果 Mono 后续在自身内核实现 Agent 能力或更换后端，该知识将过时

## 关联项

- 无

## 待确认或待验证

- 无
