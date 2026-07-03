# 前端交互术语：Cursor Mask Reveal

## 元数据

- 状态：待验证
- 类型：术语
- 领域：frontend
- 最后更新：2026-06-24
- 标签：前端交互, 术语, CSS mask, 动效, reveal

## 用户动作/判断来源

- 用户在探索前端隐藏层揭示效果时，只知道视觉效果描述（鼠标小圆区域移动时临时显示隐藏背景），不知道正确术语
- 用户问 ChatGPT 查询正确叫法，GPT 给出术语体系和参考网站
- 用户明确拒绝 scratch/scrap 方向，接受 Cursor Mask Reveal 术语

## 适用条件

- 需要实现鼠标移动临时揭示隐藏背景的前端交互效果
- 需要搜索参考案例或 Awwwords 上的同类效果
- 需要与前端开发者或 AI 编码工具沟通此类效果的准确需求

## 核心内容

正确术语体系：Cursor Mask Reveal / Mouse Pointer Mask Reveal / Background Revealing Cursor / Spotlight Cursor Reveal / Mask Cursor Effect。
错误方向术语（不要使用）：Scratch Reveal / Displacement Scratch / Permanent Reveal。
核心交互定义：鼠标有一个小圆形区域 → 鼠标移动到哪里 → 哪里临时显示隐藏背景 → 移走后继续隐藏（非永久擦除）。
参考案例网站：
1. Creative Nights — Mouse pointer mask reveal（Awwwords，WebGL + reactive cursor）
2. Minh Pham — Mask cursor（Awwwords，经典 mask cursor portfolio）
3. Background Revealing Cursor（Awwwords，cursor/interactive/reveal/fade）
4. Hover Trails and Mask Reveal on Cursor Move（动态轨迹 + 遮罩揭示）
5. Framer Cursor Mask Reveal Component（产品化组件，遮罩穿透前景图显示背景图）

## 边界与例外

- 仅适用于临时揭示类效果，不适用于永久擦除（刮刮乐）场景
- 参考网站链接需实测确认是否仍可访问

## 失效风险

术语本身稳定，但参考网站链接可能失效

## 关联项

- 无

## 待确认或待验证

- 参考网站链接未实测确认可访问性
- CSS Mask 版 demo 已跑通，术语体系在实际开发中被确认正确
