# 主 skill 分发专项 skill 属于模型层编排

## 元数据

- 状态：已验证
- 类型：架构判断
- 领域：ai_agent
- 最后更新：2026-06-17
- 标签：PersonOS, Skill架构, 模型层编排, 路由调度, AI Agent

## 用户动作/判断来源

- 用户在设计 PersonOS 主入口 skill 时，追问主 skill 在用户发起后是否可以内部调用其他 skill 来分配。
- 用户引入 Claude 对 skill 机制的说明：skill 不是函数，所谓主从调度发生在模型推理层，而不是代码层直接 call 子 skill。
- 用户据此修正 PersonOS 方案方向：只调用一次主入口，由主入口整理、路由并把后续写入交给专项 skill。

## 适用条件

- 设计多 skill 协作的 Agent 工作流时。
- 需要区分模型路由与脚本硬编码分发时。
- 希望用户只调用一次入口 skill，但后续仍由多个专项 skill 分工处理时。

## 核心内容

- Skill 本质上是被模型加载到当前上下文的一段指令，不是可直接返回结果的函数。
- 所谓主 skill 分发子 skill，本质是主 skill 先定义路由规则、输出 handoff 信息，再由 Agent 在同一任务里继续使用相应专项 skill。
- 如果需要确定性分发，应把分类和路由写成脚本或结构化规则；这是代码编排，不等于 skill 调 skill。
- 轻量且强相关的任务适合同一上下文路由；重任务、需要隔离或并行的场景更适合 subagent 编排。

## 边界与例外

- 不要把主 skill 可以继续触发其他 skill 误写成代码层函数调用能力。
- 不要把所有子流程都堆进一个上下文；当 token、隔离或并行成本成为主问题时，应改用子 agent。
- 这条知识只说明调度机制，不自动证明某个具体路由规则已经合理。

## 失效风险

若目标 Agent 未来为 skill 提供真正的代码级调用接口，这条判断需要重审；当前适用于 prompt-based skills。

## 关联项

- 04_cases/decision_cases.jsonl#decision_20260616_001
- 03_knowledge/ai_agent/personos_session_capture_usage.md

## 待确认或待验证

- 不同 Agent 对多 skill 自动装载与继续调用的稳定性仍需实测。
