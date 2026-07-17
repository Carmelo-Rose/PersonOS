# cowork_codex_bridge

> 项目归档：Cowork 调用 Codex 的单向 MCP 集成
> 日期：2026-06-14 ｜ 状态：单向集成已验证
> 标注图例：【实测】本机本会话验证 ｜【通用】外部资料/通用结论 ｜【观察】本机观察，待进一步验证 ｜【判断】主观选型或评估

## 背景

AI 应用开发者希望让 Cowork（Claude 桌面端）与本地运行的 Codex CLI 协同；需求最初模糊，无现成一键方案。（用户陈述）

## 目标

让 Cowork 作为编排方调用本地运行的 Codex CLI，执行写码 / 跑命令类任务。（用户陈述）

## 约束

- 通信走本地 stdio；但模型推理分别访问 Anthropic（Cowork）与 OpenAI（Codex）云端，并非纯本地。【通用】
- macOS 环境；希望可随时停掉 connector。（用户陈述）

## 性质界定

- 当前为 **Cowork → Codex 单向 MCP 集成**：Cowork 调用 Codex 暴露的工具，Codex 执行并回传。【实测】
- 工具命名：Codex MCP server 暴露的**原始工具名**为 `codex` 与 `codex-reply`；在 **Cowork 中以命名空间前缀**呈现为 `mcp__codex__codex`、`mcp__codex__codex-reply`。【实测】
- 未发现 Codex → Cowork 的反向调用通道；Codex 本体仅配置内置 `node_repl`。【实测，截至本会话】
- 因此不应描述为双向互联。【判断】

## 关键决策（选型）

- 候选：路线1 MCP 编排 / 路线2 双向实时桥（依赖 Claude Code Channels）/ 路线3 A2A 协议桥。【通用】
- 选择路线1。理由：
  - `codex mcp-server` 官方提供但标记 Experimental。【通用】
  - Cowork 桌面端疑未暴露 Claude Code Channels 原语，路线2 不适用。【观察，待验证】
  - A2A 适合多 Agent 集群，当前两方互联属过度设计。【判断】

## 技术实现

- Codex 以 `codex mcp-server`（stdio，官方提供但标记 Experimental）暴露。【通用】
- Cowork 在 `claude_desktop_config.json` 的 `mcpServers.codex` 直连二进制 `/Applications/Codex.app/Contents/Resources/codex`。【实测】
- 暴露工具：`mcp__codex__codex`、`mcp__codex__codex-reply`（原始名 `codex` / `codex-reply`）。【实测】

## 配置现状（区分两层）

- **MCP server 启动参数（权威）**：`--sandbox workspace-write --ask-for-approval never`，进程 cwd = `/`。（args 为用户提供的权威值；cwd=`/` 经探针【实测】证实）
- **单次会话状态**：每次调用可不同（探针某次为 `read-only`）。【实测】不可把单次会话状态当作启动配置。

## 过程与踩坑

- 初版包装脚本置于 `~/Documents` 启动失败：`Operation not permitted`（EPERM）。【实测】疑因 macOS TCC 对 Documents 等受保护目录限制执行。【观察，待验证】
- 改为直连 `/Applications` 二进制后接通。【实测】
- GUI 启动通常不继承 shell PATH（故采用绝对路径，本例并非失败主因）。【通用】
- 全局 `--cd` 对 `mcp-server` 不生效，pwd 仍为 `/`。【实测】
- `echo hello-from-codex` 验证 Cowork→Codex 链路通。【实测】

## 安全与风控

- 启动参数是软默认，非硬边界：`codex` 工具允许调用方每次传 `sandbox`（含 `danger-full-access`）、`cwd`、`approval-policy`、任意 `config` 覆盖。【实测，见工具 schema】
- 当前启动为 workspace-write + cwd `/`，默认可写范围较宽；**但仍受所选 sandbox 策略与 macOS 系统权限（如 Seatbelt、TCC）约束，并非无限制**。【实测 + 通用】
- `codex mcp-server` **官方提供但标记 Experimental**，不等于成熟稳定；**"走官方 MCP 接口" 也不等于低风险**——实际风险取决于写权限范围、是否被覆盖到更宽权限、调用频率与所处理数据的敏感度。【判断】
- 要形成强隔离须 OS 级手段（独立用户 / 容器 / VM），参数与提示词替代不了。【通用】

## 产出

当前资产在根目录 `cowork-codex-bridge/`（README、配置片段、弃用脚本、案例复盘）。按约定宜归入本目录 `01_projects/cowork_codex_bridge/`，经确认暂不移动。

## 复盘

单向 MCP 集成可用于个人开发派活；若需 Codex 主动回调 Cowork 的真双向，需另设反向通道，目前没有。【判断】

## 待办

- 是否将根目录 `cowork-codex-bridge/` 资产合并入本目录（暂不移动，待确认）。
- 是否将可复用经验提炼写入 `04_cases/`（暂不写，待确认）。
