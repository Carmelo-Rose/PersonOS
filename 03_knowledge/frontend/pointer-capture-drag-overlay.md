# 可拖拽浮层用 pointer capture 稳定收尾

## 元数据

- 状态：已验证
- 类型：方法
- 领域：frontend
- 最后更新：2026-07-17
- 标签：frontend, pointer-events, drag, overlay, sidebar, browser-ui

## 用户动作/判断来源

- 本次招聘助手浮层拖拽修复过程中，用户明确指出松手后仍继续跟随鼠标、按住拖拽又偶发失效
- userscript/boss-helper.user.js 中将拖拽改为 pointerdown / setPointerCapture / pointermove / pointerup / lostpointercapture / blur 组合

## 适用条件

- 需要实现可拖拽的浏览器浮层、侧边栏、弹窗或面板
- 需要兼容鼠标按下、松手、切出窗口或捕获丢失等终止场景

## 核心内容

对于可拖拽浮层，不要只用 mousemove 和 buttons 判断拖拽是否继续；应在 pointerdown 时记录 pointerId 并调用 setPointerCapture，让后续移动、松手、失焦和捕获丢失都走统一收尾。这样可以同时解决「松手后仍继续跟随」和「拖拽中途偶发失效」两类问题。

## 边界与例外

- 如果宿主环境不支持 Pointer Events，需要回退到更保守的鼠标事件方案
- 对非浮层、非全局拖拽的简单交互，不一定需要完整 pointer capture 管线

## 失效风险

中。浏览器事件细节和 Pointer Events 兼容行为可能随平台或宿主容器变化，但方法本身较稳定。

## 关联项

- 无

## 待确认或待验证

- 无
