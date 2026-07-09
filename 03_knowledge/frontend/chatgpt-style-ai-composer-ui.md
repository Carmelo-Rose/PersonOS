# ChatGPT/Gemini 式 AI 入口界面的极简实现方法

## 元数据

- 状态：已验证
- 类型：方法
- 领域：frontend
- 最后更新：2026-07-05
- 标签：frontend, ai-ui, composer, minimal-ui, ChatGPT, Gemini, Mono

## 用户动作/判断来源

- 用户在 Mono Web 原型探索中否定复杂工作台/cockpit 方案，要求改成 ChatGPT 式极简中心输入页面。
- 用户提供 ChatGPT 和 Gemini 截图，要求按成熟产品的比例、元素密度和 composer 行为校准。
- 用户连续纠正输入框、快捷入口、发送按钮、加号、长文本展开态、中文化和背景特效的细节。

## 适用条件

- 设计 AI 助手、企业 Agent、创作工作台或多工具平台的首屏入口。
- 用户目标是先获得干净可信的入口体验，而不是展示完整功能矩阵。
- 页面有复杂能力或背景特效，但首屏需要让输入框成为唯一主焦点。

## 核心内容

- 先收敛首屏信息：保留品牌/极简 rail、中心问候、单一 composer、少量快捷 chip；删除顶部导航、状态条、项目上下文、recent strip 等工作台信息。
- 背景和特效只能作为氛围层：默认低存在感，交互时短暂出现，不得抢输入框焦点。
- composer 默认态应是单行 pill；长文本输入时自动增高，到上限后 textarea 内部滚动。
- composer 展开态应分成两层：上方文本区独占宽度，下方工具栏放加号/模式/发送等操作；不要把加号继续放在文本行左侧。
- 图标尺寸和字形要按视觉重心校准：字体字符可能造成偏下/偏重，应使用可控图形或成熟图标实现。
- 用成熟产品截图做比例参照，并用浏览器几何指标只辅助判断，不能替代视觉校准。

## 边界与例外

- 不适用于需要第一屏展示数据表、监控指标或复杂任务队列的后台系统。
- 如果产品已进入重度工作流阶段，可以逐步引入项目、历史、画布和工具面板，但不应提前挤进首屏。
- 特效只在不影响可读性、性能和核心输入焦点时使用。

## 失效风险

中：ChatGPT/Gemini 的具体 UI 细节会变化，但中心输入、低元素密度、渐进披露和 composer 展开态分层仍是可复用原则。

## 关联项

- 03_knowledge/frontend/css-mask-vs-webgl-shader-reveal.md
- 03_knowledge/frontend/cursor-mask-reveal-terminology.md
- 03_knowledge/frontend/design-reference-importance.md

## 待确认或待验证

- 无
