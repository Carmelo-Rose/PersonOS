# macOS 文件误删后的多级恢复策略

## 元数据

- 状态：已验证
- 类型：方法
- 领域：automation
- 最后更新：2026-07-04
- 标签：macOS, 文件恢复, 版本管理, TextEdit, AppleScript

## 用户动作/判断来源

- 2026-07-04：TextEdit 文件 test_副本.txt 被误触清空为 0 字节，先后尝试撤销历史、剪贴板粘贴均无效，通过 AppleScript 连续撤销 + macOS Versions 版本浏览成功恢复全部内容

## 适用条件

- 在 macOS 上使用 TextEdit 或其他支持 Versions 的应用编辑文件时误删或错误编辑后需要恢复
- 文件已被保存（落盘），但编辑器窗口未关闭
- macOS 的自动版本快照机制可用

## 核心内容

macOS 文件误删后的恢复策略按优先级排序：
1) 编辑器撤销历史：如果窗口未关闭且撤销历史未被覆盖，连续 Command+Z 回退
2) macOS 版本浏览：菜单「文件→复原到→浏览所有版本」可查看系统自动保存的历史快照，找到有内容的版本点击「恢复」
3) 自动保存目录：TextEdit 的自动保存信息位于 ~/Library/Containers/com.apple.TextEdit/Data/Library/Autosave Information/
4) Time Machine 快照：若已开启时间机器，通过 tmutil listlocalsnapshots / 检查并按时间点恢复
5) AppleScript 自动化触发：远程协助时可用 osascript 向 TextEdit 发送 keystroke 触发连续撤销，或通过菜单项打开版本浏览器

## 边界与例外

- 仅适用于 macOS 原生支持 Versions 的应用（TextEdit、Pages、Numbers、Keynote），第三方编辑器需依赖各自的本地历史功能
- Versions 快照是间歇性自动保存的，不保证每次编辑都有快照
- 撤销历史在编辑器关闭后清空，快照依赖系统定时触发
- Time Machine 需预先配置且连接备份硬盘

## 失效风险

低——macOS Versions 是系统级功能，已稳定存在多年

## 关联项

- 无

## 待确认或待验证

- 无
