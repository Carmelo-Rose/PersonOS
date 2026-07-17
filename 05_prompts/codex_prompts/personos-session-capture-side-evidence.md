# PersonOS session capture 合并 side conversation 证据的调用模板

## 元数据

- 状态：已验证
- 分类：codex_prompts
- 工具或场景：Codex / PersonOS session capture
- 版本：v1
- 最后更新：2026-07-05
- 标签：PersonOS, session-capture, side-conversation, 证据边界, Codex

## 用户动作/判断来源

- 用户在一次 local-project-index MCP 实现后的 PersonOS 记录请求中，明确要求以主会话为记录主体，并把 side conversation 作为补充证据。
- 用户校准了冲突处理规则：侧边内容与主会话重复或冲突时，以主会话中最终确认过的表述为准。
- 本次候选板按该边界执行：MCP 原型作为主事件，side conversation 只补强 stdio、本机配置和 capture 边界。

## 输入要求

- 存在一个主会话或主工作流，且 side conversation 只用于补充事实、边界或校准。
- 用户能明确说明 side conversation 中哪些内容应作为补充证据。
- 需要保留 PersonOS session-capture 的统一候选板和一次确认写入流程。

## 提示词正文

```text
记录这次。

以主会话为主进行 session capture，同时把本次 side conversation 作为补充证据一起纳入。侧边内容不要单独当成独立事件；如与主会话表述重复或冲突，以主会话里我最终确认过的表述为准。

补充证据重点：
1. 当前这个 local-project-index MCP 已验证本机 stdio 通路可用，说明同机客户端可调用，但不代表外部网络接入已打通。
2. mcpServers 那段配置可供同机、支持 MCP 的客户端使用；不是给远程外部机器直接访问的配置。
3. 关于 PersonOS capture，结论是主会话应作为本次记录主体，side conversation 作为补充证据纳入更合适。

请按这个边界抽取 candidates、查重、出统一候选板，再让我一次性确认写入。
```

## 输出格式

- 按 personos-session-capture 流程抽取 candidates。
- 查重后输出统一候选板。
- 候选板中把 side conversation 标记为补充证据来源，而不是独立事件。
- 等待用户一次性确认写入。

## 成功标准

- 主会话事件保持为记录主体。
- side conversation 不被拆成独立案例。
- 重复或冲突内容以主会话最终确认表述为准。
- 补充证据能修正或收紧边界，而不是扩大未验证结论。

## 验证结果

已在本次 local-project-index MCP 的 PersonOS capture 中使用：候选板把主会话实现作为 success case 主体，并把 side conversation 的 stdio、本机配置、capture 边界作为补充证据纳入。

## 适用边界

- 适用于同一工作主题下，主会话和 side conversation 都与同一次记录相关的场景。
- 不适用于 side conversation 本身已经形成独立项目事件、独立决策或独立失败/成功案例的场景。
- 如果 side conversation 与主会话出现事实冲突，以用户最终确认过的主会话表述为准，除非用户明确指定替换。

## 变更原因

用户给出了一段可复用的 PersonOS session capture 调用边界，解决多会话证据合并时的主体、冲突和写入确认问题。

## 版本历史

- v1: 从 local-project-index MCP 记录请求中抽取，保留主会话为主体、side conversation 为补充证据的边界。

## 待确认或待验证

- 未来是否适用于所有 side conversation 场景仍需更多使用样本验证。
