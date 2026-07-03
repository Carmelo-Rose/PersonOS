# 证据记录：本次会话的用户确认与纠偏（2026-06-14）

用于支撑案例 `04_cases/project_cases.jsonl` 中 `project_20260614_002`。
记录用户本人在本次 Cowork 会话中的关键判断、纠偏与最终确认（主体为用户）。

## 用户的纠偏（按发生顺序）

1. 指出 Agent 未经确认就向 `04_cases/` 写入，要求撤回擅自新增的四条记录。
2. 指出同一事件不应拆成四类案例冗余写入。
3. 纠正定性：当前是「Cowork 调用 Codex 的单向 MCP 集成」，不是双向互联。
4. 纠正配置：真实启动参数为 `workspace-write + approval never`、进程 cwd 为 `/`；`read-only` 只是单次调用状态，须区分 MCP server 启动配置与单次会话配置。
5. 纠正措辞：「纯本地」改为「本地 stdio 通信，模型推理分别访问 Anthropic/OpenAI 云端」。
6. 要求区分：原始工具名（`codex`/`codex-reply`）与 Cowork 命名空间（`mcp__codex__codex`）；「本地 Codex」改为「本地运行的 Codex CLI」。
7. 要求把 Channels 不支持、TCC 致脚本不可执行等标为「本机观察/待验证」，不当通用结论。
8. 明确「官方接口」不等于「低风险」；要求区分通用结论 / 本机实测 / 主观判断。
9. 指出旧 README 只是追加而非真正修正，要求精简为弃用声明。
10. 确立准则：PersonOS 案例必须以用户本人为主体，Agent 仅作背景/证据/结果。
11. 案例改写后仍指出残留 Agent 视角，要求按 Codex 审查意见修正三处问题。

## 用户的确认与流程要求

- 要求两个 Agent（Cowork、Codex）交叉核验关键事实，不接受单方结论。
- 坚持每次写入前先看草稿，由本人明确回复「确认写入」才落库。
- 对 `project_20260614_002` 的写入与每次修订，均经本人「确认写入」放行。

## 性质（与权威归档一致）

载体为 Cowork→Codex 的单向 MCP 集成；详见 `01_projects/cowork_codex_bridge/README.md`。
