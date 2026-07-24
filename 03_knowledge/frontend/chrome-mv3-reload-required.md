# Chrome MV3 插件改代码后必须手动重新加载才生效

## 元数据

- 状态：已验证
- 类型：工具用法
- 领域：frontend
- 最后更新：2026-07-22
- 标签：Chrome扩展, Manifest V3, 调试, 热更新

## 用户动作/判断来源

- 2026-07-22 Mono 插件调试：改了 background.js 的接口地址后，怀疑插件行为没变化，排查后确认是因为没有在 chrome://extensions 里点重新加载，service worker 还在跑旧代码

## 适用条件

- Manifest V3 Chrome 扩展，以 unpacked/加载已解压的扩展 方式在 chrome://extensions 里调试
- 刚编辑了 background.js（service worker）或 popup.js 等扩展代码，准备验证新行为

## 核心内容

Chrome 扩展的 background service worker 不会因为磁盘上的源文件变化而自动重新加载/热更新。每次修改 background.js、popup.js 等文件后，必须去 chrome://extensions 找到对应扩展，手动点击'重新加载'（循环箭头图标），新代码才会生效。如果调试时发现改了代码但行为看起来没变化，第一件事应该先检查是不是忘了点重新加载，而不是急着怀疑代码逻辑本身有问题。

## 边界与例外

- 只适用于开发时'加载已解压的扩展程序'调试模式；已发布到 Chrome 网上应用店、用户端自动更新的场景不适用（那是另一套更新机制）
- content script 的行为有时会随页面刷新部分生效，但 background/service worker 的逻辑仍需要显式重新加载扩展本身

## 失效风险

如果 Chrome 扩展加载机制变化（例如未来支持真正的热重载），此知识可能过时；目前基于 Chrome MV3 的实际行为

## 关联项

- 无

## 待确认或待验证

- 无
