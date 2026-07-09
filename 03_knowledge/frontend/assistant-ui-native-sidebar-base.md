# assistant-ui 原生侧边栏前端底座集成

## 元数据

- 状态：已验证
- 类型：方法
- 领域：frontend
- 最后更新：2026-07-06
- 标签：assistant-ui, Mono, frontend, sidebar, Next.js

## 用户动作/判断来源

- 用户选择 assistant-ui/assistant-ui 作为 Mono 新 web 前端底座。
- 用户确认完整 Base 体验需要侧边栏，不只是中间 Thread 主模块。
- 用户纠偏要求先不要加太多元素，上一版挺好但缺少原生侧边栏。
- 实现从自定义工具工作台面板回退为 assistant-ui 原生 ThreadListSidebar + Thread 组合，并通过 tsc/build 验证。

## 适用条件

- 在 Mono 或类似项目中，需要用 assistant-ui 搭 React/Next 前端底座。
- 目标是先建立可运行 UI shell，而不是立即做完整业务工作台。
- 用户强调保留开源前端的原生结构或截图中的 Base 体验。

## 核心内容

- 优先从 assistant-ui 官方模板入手，而不是只复制 Thread 主模块。关键组合是 AssistantRuntimeProvider 包住 SidebarProvider，页面内放 ThreadListSidebar、SidebarInset/header 和 Thread。
- ThreadListSidebar、ThreadList、Thread 等原生组件在 packages/ui/src/components/assistant-ui 中；完整组合可参考 templates/default/app/assistant.tsx。
- 如果只是搭底座，保留最小顶部栏和原生侧边栏，不要提前加入工具卡、工作流切换、状态标签等 Mono 业务层。
- 为了不用 API Key 也能验证前端，可临时使用 useLocalRuntime + ChatModelAdapter mock；后续再替换为 Chrome extension background 消息桥或服务端 API。
- 若浏览器翻译插件给 html 注入属性导致 hydration mismatch，可在 Next root layout 的 html 标签上加 suppressHydrationWarning。
- 如果默认 shadcn Sidebar 在窄宽度下折叠导致用户看不到原生侧边栏，而当前阶段目标是展示完整底座，可在 ThreadListSidebar 上传 collapsible="none"。

## 边界与例外

- 这不是最终 Mono 产品信息架构，只是前端底座组合方法。
- 不要把 mock runtime 当作生产 API 接入方案。
- 当用户明确要移动端抽屉行为时，不应强行使用 collapsible="none"。
- 业务工具入口、Image2 模板、素材下载等应在底座确认后再逐步接入。

## 失效风险

assistant-ui、Next、shadcn Sidebar 的 API 和默认响应式行为可能随版本变化；升级后需重新确认 SidebarProvider、ThreadListSidebar、Thread 的组合方式。

## 关联项

- 04_cases/success_cases.jsonl: Mono 采用 assistant-ui 搭建原生侧边栏前端底座

## 待确认或待验证

- 尚未验证嵌入 Chrome extension drawer 后的尺寸和消息桥方案。
