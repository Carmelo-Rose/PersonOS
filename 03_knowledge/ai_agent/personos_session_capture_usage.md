# PersonOS 会话记录使用方法

## 元数据

- 状态：已验证
- 类型：方法
- 领域：ai_agent
- 最后更新：2026-06-18
- 标签：PersonOS, 会话采集, 统一候选板, 一次确认, Manifest分发, Agent协作, Skill架构

## 用户动作/判断来源

- 用户多次强调不想逐个调用专项 skill，希望只说一次“记录这次”。
- 用户让 Claude cowork 通过 MCP 与 Codex 协同同步 skills 后，在 Codex 中直接调用新版 personos-session-capture 记录当前会话。
- 当前 personos-session-capture/SKILL.md 已升级为批量候选板、一次确认、冻结 manifest、apply_manifest.py 分发的默认流程。
- 当前会话中用户确认先写入 case 更新与 usage 文档更新，prompt 与 organ 候选暂缓。

## 适用条件

- 需要把当前对话或工作 session 沉淀到 PersonOS 时。
- 一次会话可能同时包含 case、knowledge、prompt、organ 或 profile 候选时。
- 用户希望只调用一次主入口，而不是手动逐个调用专项 capture skill 时。
- 目标 Agent 支持读取或加载 PersonOS skills，且能运行本地写入脚本时。

## 核心内容

- 默认入口是 personos-session-capture。用户在 Codex 中直接说“记录这次”，或明确说“使用 $personos-session-capture 记录这次”。
- 新版默认流程不是“主对象写完后再逐个处理派生候选”，而是一次性抽取所有 meaningful capture objects，分别路由到 04_cases、03_knowledge、05_prompts、02_organs 或 00_profile 候选。
- session-capture 先运行各组 finder 做查重，再按对应 schema 草稿到可确认粒度，输出统一候选板。候选板需要显示类型、标题、目标组与文件/ID、操作、新增或更新依据、内容预览、证据、未决项和查重结果。
- 用户可以一次回复“写入 1、2，暂缓 3、4”或要求修改某些条目。只有用户确认的条目会进入写入流程。
- 确认后，session-capture 冻结 manifest，不再重推理内容；apply_manifest.py 根据 manifest 调用 cases、knowledge、prompt、organ 的专项写入脚本。
- 专项 skill 的深度交互流程仍然保留：当单个对象需要访谈、重构、复杂新旧判断或脚本拒绝时，再切到对应专项 skill。
- 00_profile 只作为候选信号展示，不从单次 session 直接写入。

## 边界与例外

- 不得在用户确认前写入 PersonOS。
- 不得把未被用户选择的候选项批量写入。
- 不得让主入口绕过专项写入脚本直接改文件。
- 如果 schema drafting 后目标组、目标路径、核心内容或更新对象发生实质变化，必须单独再确认。
- 在不支持 skill 自动发现的 Agent 中，只能要求 Agent 显式读取 PersonOS/.agents/skills/personos-session-capture/SKILL.md 并按流程执行。
- 如果目标 Agent 无法运行写入脚本，应只生成候选板或 frozen manifest，由能访问 PersonOS 仓库与脚本的 Agent 执行。

## 失效风险

如果未来 Agent 提供真正的代码级 skill 调用接口，或 session-capture 改为子 agent 编排优先，这份使用方法需要重写。

## 关联项

- 04_cases/decision_cases.jsonl#decision_20260616_001
- 03_knowledge/ai_agent/skill-dispatch-is-model-orchestration.md
- 03_knowledge/ai_agent/proactive-capture-reminders-need-hooks.md

## 待确认或待验证

- 不同 Agent 对多 skill 自动装载、MCP 同步和本地脚本执行的稳定性仍需继续验证。
- 当候选很多或存在冲突更新时，是否需要把统一候选板拆成分组确认仍待实测。
