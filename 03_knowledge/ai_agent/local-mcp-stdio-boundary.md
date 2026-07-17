# 本机 MCP stdio 配置的适用边界

## 元数据

- 状态：已验证
- 类型：工具用法
- 领域：ai_agent
- 最后更新：2026-07-05
- 标签：MCP, stdio, 本机Agent, 工具配置, 边界说明

## 用户动作/判断来源

- 用户在 local-project-index MCP 原型完成后，主动校准记录边界：本机 stdio 通路可用只说明同机客户端可调用，不代表外部网络接入已打通。
- 用户进一步确认 mcpServers 配置是给同机、支持 MCP 的客户端使用，不是给远程外部机器直接访问。
- 项目 README 中保留了同机客户端通过 node 启动 dist/src/server.js 的 mcpServers 配置示例。

## 适用条件

- 为本机 Agent、Claude Desktop、Cursor 或其他同机 MCP 客户端配置本地 stdio server。
- 说明本地 MCP 原型验证结果时，需要区分同机 stdio 调用链和远程网络访问能力。
- 把本机项目工具化时，第一版只需要本地客户端启动命令，而不需要对外开放端口。

## 核心内容

- mcpServers 配置中的 command、args、env 是让同一台机器上的 MCP 客户端启动本地 server 的方式。
- 通过 smoke:mcp 验证 stdio server，只能证明本机客户端到本地 MCP server 的 stdio 调用链可用。
- 它不证明远程外部机器可以访问，也不包含网络监听、鉴权、隧道、反向代理或 HTTP transport 设计。
- 若后续需要外部网络接入，应作为单独方案处理，重新设计 transport、授权边界、访问控制和部署方式。

## 边界与例外

- 不要把同机 mcpServers 配置写成远程外部机器可直接调用的配置。
- 不要从 npm run smoke:mcp 成功推出公网、局域网或跨机器访问已经打通。
- 如果 MCP 工具开始执行命令或写文件，需要重新设计权限和确认边界；本条只覆盖本地只读 stdio 原型。

## 失效风险

中。MCP 客户端配置入口和 SDK API 可能变化；但 stdio 配置不等于远程网络接入这一边界较稳定。

## 关联项

- 04_cases/success_cases.jsonl: 本机 local-project-index MCP 原型打通 stdio 调用

## 待确认或待验证

- 远程访问 MCP 的具体 transport、鉴权和部署方案尚未设计。
