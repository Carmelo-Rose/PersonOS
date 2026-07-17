# PersonOS 三层收割架构与确认式确定性写入

## 元数据

- 状态：待验证
- 类型：架构判断
- 领域：ai_agent
- 最后更新：2026-07-16
- 标签：PersonOS, 收割架构, 蒸馏, 确定性写入, Skill架构, AI Agent

## 用户动作/判断来源

- 用户诊断 PersonOS 头重脚轻并主导设计三层收割
- 本次会话建成 distill/profile-promote 并改 session-capture

## 适用条件

- 设计从累积记录产出聚合资产（规则/评测/画像）的知识或判断系统时
- 要决定新增聚合层还是修改进料层时

## 核心内容

- 分两类职责：进料层（session-capture + 专项 capture）记录单会话；聚合层跨案例蒸馏——distill 治 02_organs/06_eval，profile-promote 治 00_profile（阈值≥2 个不同真实案例、跨项目优先）
- 写入模式：scan 只读 → 候选板 → 人确认 → 冻结 manifest → 脚本 dry-run + 原子写，且强制案例溯源（无真实案例编号拒写）
- 运行时 skill 只读，改动需重打包 .skill.zip 在 Settings 重装
- 增量侧：session-capture 强制浮出 organ/profile 候选，避免判断规则/偏好被 case 默认吞掉

## 边界与例外

- 单会话不产成熟聚合物（规则/评测/画像），这些应由聚合层多案例蒸馏
- profile 需多案例阈值支撑，不从单会话写入

## 失效风险

若 PersonOS skill 机制或写入方式变更，具体脚本细节可能过时；分层与确认式写入的原则较稳定。

## 关联项

- 03_knowledge/ai_agent/skill-dispatch-is-model-orchestration.md
- 03_knowledge/ai_agent/proactive-capture-reminders-need-hooks.md

## 待确认或待验证

- 长期使用效果待验证
